#!/usr/bin/env bash
# Executed on the deployment host over verified SSH; also testable with local stubs.
set -euo pipefail
MODE="${1:?Expected snapshot or apply}"
READINESS_TIMEOUT="${2:-90}"
READINESS_INTERVAL="${3:-2}"
for VALUE in "$READINESS_TIMEOUT" "$READINESS_INTERVAL"; do
  [[ "$VALUE" =~ ^[1-9][0-9]*$ ]] && (( VALUE <= 3600 )) || {
    echo 'Readiness timeout/interval must be integers between 1 and 3600 seconds.' >&2; exit 2;
  }
done
cd "${MONITORING_DIR:-/opt/infra-prom}"
mkdir -p .runtime
chmod 700 .runtime

state() {
  docker inspect --format '{{.Id}} {{.State.StartedAt}} {{.State.Status}}' "$1" 2>/dev/null || echo 'missing missing missing'
}

config_hash() {
  local SERVICE="$1" PATHNAME
  local -a PATHS
  if [[ "$SERVICE" == prometheus ]]; then
    PATHS=(config/prometheus.yml config/rules config/targets)
  else
    PATHS=(.runtime/alertmanager.yml .runtime/telegram_bot_token config/alertmanager/templates)
  fi
  # Content and names only: timestamps do not cause unnecessary reloads.
  for PATHNAME in "${PATHS[@]}"; do
    if [[ -e "$PATHNAME" ]]; then
      find "$PATHNAME" -type f -exec sha256sum {} +
    else
      printf 'missing %s\n' "$PATHNAME"
    fi
  done | LC_ALL=C sort | sha256sum | cut -d' ' -f1
}

redact_logs() {
  # No full inspect/config dumps. Hide the exact token, token-shaped strings and URLs.
  awk '
    BEGIN { if ((getline secret < ".runtime/telegram_bot_token") < 0) secret="" }
    { if (secret != "") while ((p=index($0,secret)) > 0)
        $0=substr($0,1,p-1) "[REDACTED]" substr($0,p+length(secret)); print }
  ' | sed -E 's/[0-9]{5,}:[A-Za-z0-9_-]+/[REDACTED]/g; s#https?://[^[:space:]]+#[URL REDACTED]#g; s/([Pp]assword|[Tt]oken|[Aa]uthorization)[=:][[:space:]]*[^[:space:]]+/\1=[REDACTED]/g'
}

diagnostics() {
  local SERVICE
  for SERVICE in prometheus alertmanager; do
    echo "--- $SERVICE state ---" >&2
    docker inspect --format 'status={{.State.Status}} exit={{.State.ExitCode}} restarting={{.State.Restarting}} started={{.State.StartedAt}}' "$SERVICE" 2>&1 | redact_logs >&2 || true
    echo "--- $SERVICE last 80 log lines (redacted) ---" >&2
    docker logs --tail 80 "$SERVICE" 2>&1 | redact_logs >&2 || true
  done
}

failed() {
  echo "ERROR: $*" >&2
  diagnostics
  exit 1
}

url() {
  case "$1" in
    prometheus) echo http://127.0.0.1:9090 ;;
    alertmanager) echo http://127.0.0.1:9093 ;;
  esac
}

pause_retry() {
  local REMAINING="$1" DELAY="$READINESS_INTERVAL"
  (( DELAY > REMAINING )) && DELAY="$REMAINING"
  (( DELAY > 0 )) && sleep "$DELAY"
  return 0
}

wait_ready() {
  local SERVICE="$1" DEADLINE=$((SECONDS + READINESS_TIMEOUT)) STATUS REMAINING
  echo "Waiting for $SERVICE readiness (timeout ${READINESS_TIMEOUT}s)..."
  while (( SECONDS < DEADLINE )); do
    STATUS=$(state "$SERVICE")
    case "$STATUS" in
      *' exited'|*' dead'|*' restarting'|*' missing') failed "$SERVICE is not running: $STATUS" ;;
    esac
    REMAINING=$((DEADLINE - SECONDS))
    if curl -fsS --connect-timeout 1 --max-time "$REMAINING" "$(url "$SERVICE")/-/ready" >/dev/null 2>&1; then
      echo "$SERVICE ready."
      return 0
    fi
    pause_retry "$((DEADLINE - SECONDS))"
  done
  failed "$SERVICE readiness timed out after ${READINESS_TIMEOUT}s."
}

reload_metric() {
  local SERVICE="$1" METRIC="$2" LIMIT="${3:-3}"
  (( LIMIT > 0 )) || return 1
  (( LIMIT > 3 )) && LIMIT=3
  curl -fsS --connect-timeout 1 --max-time "$LIMIT" "$(url "$SERVICE")/metrics" 2>/dev/null |
    awk -v metric="${SERVICE}_config_${METRIC}" '$1 == metric {print $2}'
}

wait_reload() {
  local SERVICE="$1" BEFORE="$2" DEADLINE=$((SECONDS + READINESS_TIMEOUT)) TIMESTAMP SUCCESS
  while (( SECONDS < DEADLINE )); do
    TIMESTAMP=$(reload_metric "$SERVICE" last_reload_success_timestamp_seconds "$((DEADLINE - SECONDS))") || TIMESTAMP=''
    SUCCESS=$(reload_metric "$SERVICE" last_reload_successful "$((DEADLINE - SECONDS))") || SUCCESS=''
    if [[ "$SUCCESS" == 0 ]]; then failed "$SERVICE rejected the configuration reload."; fi
    if [[ "$SUCCESS" == 1 ]] && awk -v after="$TIMESTAMP" -v before="$BEFORE" 'BEGIN {exit !(after+0 > before+0)}'; then
      return 0
    fi
    pause_retry "$((DEADLINE - SECONDS))"
  done
  failed "$SERVICE did not confirm a successful reload within ${READINESS_TIMEOUT}s."
}

case "$MODE" in
  snapshot)
    for SERVICE in prometheus alertmanager; do
      state "$SERVICE" > ".runtime/before-$SERVICE"
      # Preserve the last accepted hash across failed/retried deployments.
      if [[ ! -f ".runtime/loaded-$SERVICE" ]]; then
        config_hash "$SERVICE" > ".runtime/loaded-$SERVICE"
      fi
    done
    ;;
  apply)
    trap 'failed "Deployment command failed (line $LINENO)."' ERR
    docker compose config --quiet
    docker compose pull
    docker compose run --rm --no-deps --entrypoint /bin/promtool prometheus check config /etc/prometheus/prometheus.yml
    docker compose run --rm --no-deps --entrypoint /bin/amtool alertmanager check-config /etc/alertmanager/alertmanager.yml
    docker compose up -d
    for SERVICE in prometheus alertmanager; do
      [[ -f ".runtime/before-$SERVICE" ]] || failed "Missing pre-deployment snapshot for $SERVICE."
      BEFORE=$(cat ".runtime/before-$SERVICE")
      wait_ready "$SERVICE"
      AFTER=$(state "$SERVICE")
      HASH=$(config_hash "$SERVICE")
      LOADED=$(cat ".runtime/loaded-$SERVICE")
      if [[ "$BEFORE" == "$AFTER" && "$AFTER" == *' running' && "$HASH" != "$LOADED" ]]; then
        STAMP=$(reload_metric "$SERVICE" last_reload_success_timestamp_seconds) || STAMP=''
        [[ "$STAMP" =~ ^[0-9.eE+-]+$ ]] || failed "Cannot read $SERVICE reload timestamp; refusing an unverified reload."
        echo "Reloading changed configuration in existing $SERVICE container."
        docker kill --signal=SIGHUP "$SERVICE" >/dev/null
        wait_reload "$SERVICE" "$STAMP"
        wait_ready "$SERVICE"
      elif [[ "$BEFORE" != "$AFTER" ]]; then
        echo "$SERVICE was created or restarted; configuration read at startup, no SIGHUP."
      else
        echo "$SERVICE configuration unchanged; no SIGHUP."
      fi
      printf '%s\n' "$HASH" > ".runtime/loaded-$SERVICE"
    done
    ;;
  *) echo 'Expected snapshot or apply.' >&2; exit 2 ;;
esac
