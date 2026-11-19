#!/usr/bin/env bash
# Run only on a disposable Docker host with local loopback access.
set -euo pipefail

image=couchdb@sha256:c311385c44e9708952c3b9ada25eb538f2b5a57d0cf89bfd07f4a4dbf962697c
fixture="crm-couchdb-rehearsal-$(openssl rand -hex 10)"
old_password=$(openssl rand -hex 24)
new_password=$(openssl rand -hex 24)
base_url=
active_container=
fixture_volume=

cleanup() {
    if [[ -n "$active_container" ]]; then docker rm -f "$active_container" >/dev/null 2>&1 || true; fi
    if [[ -n "$fixture_volume" ]]; then docker volume rm "$fixture_volume" >/dev/null 2>&1 || true; fi
}
trap cleanup EXIT

request() {
    local password=$1
    shift
    curl --config - --silent --show-error --max-time 5 "$@" <<<"user = \"fixture:$password\""
}

start() {
    local password=$1
    active_container=$(COUCHDB_USER=fixture COUCHDB_PASSWORD="$password" docker run --detach \
        --label crm.rotation.fixture="$fixture" \
        --env COUCHDB_USER --env COUCHDB_PASSWORD \
        --publish 127.0.0.1::5984 --mount "type=volume,source=$fixture_volume,target=/opt/couchdb/data" \
        "$image")
    base_url="http://$(docker port "$active_container" 5984/tcp)"
    for ((attempt=0; attempt<60; attempt++)); do
        if request "$password" --fail "$base_url/_all_dbs" >/dev/null 2>&1; then return 0; fi
        sleep 1
    done
    echo 'CouchDB sintético no disponible con la credencial esperada.' >&2
    return 1
}

stop() {
    docker stop "$active_container" >/dev/null
    docker rm "$active_container" >/dev/null
    active_container=
}

assert_rejected() {
    local code
    code=$(request "$1" --output /dev/null --write-out '%{http_code}' "$base_url/_all_dbs")
    test "$code" = 401
}

docker pull "$image" >/dev/null
fixture_volume=$(docker volume create --label crm.rotation.fixture="$fixture" "$fixture")
start "$old_password"
request "$old_password" --fail --request PUT "$base_url/rehearsal" >/dev/null
stop
start "$new_password"
assert_rejected "$old_password"
request "$new_password" --fail "$base_url/rehearsal" >/dev/null
stop
start "$old_password"
assert_rejected "$new_password"
request "$old_password" --fail "$base_url/rehearsal" >/dev/null
stop
echo 'PASS: CouchDB aceptó el cambio y el rollback sobre el mismo volumen sintético.'
