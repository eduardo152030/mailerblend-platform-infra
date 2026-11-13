#!/bin/sh
# CPU accounting for this approved CT only. Runs as nobody in the existing Node image.
set -eu
HOST_ROOT=${PILOT_HOST_ROOT:-/}
METRIC_DIR=${PILOT_METRIC_DIR:-/var/lib/node_exporter/textfile}
[ "$(cat "$HOST_ROOT/etc/hostname")" = infra-webui ] || exit 2
[ "$(grep -c '^cpu[0-9]' "$HOST_ROOT/proc/stat")" = 2 ] || exit 2
umask 077
mkdir -p "$METRIC_DIR"
update() {
  now=$(date +%s)
  if awk -v now="$now" '
    $1=="usage_usec" {total=$2; have_total=1}
    $1=="user_usec" {user=$2; have_user=1}
    $1=="system_usec" {system_cpu=$2; have_system=1}
    END {
      if (!have_total || !have_user || !have_system) exit 1
      labels="{ct_id=\"631\",resource_scope=\"lxc\",cpu_source=\"cgroup_v2\"}"
      print "# HELP lxc_cpu_usage_seconds_total CPU time consumed by this LXC, including descendants."
      print "# TYPE lxc_cpu_usage_seconds_total counter"
      printf "lxc_cpu_usage_seconds_total%s %.6f\n",labels,total/1000000
      print "# TYPE lxc_cpu_user_seconds_total counter"
      printf "lxc_cpu_user_seconds_total%s %.6f\n",labels,user/1000000
      print "# TYPE lxc_cpu_system_seconds_total counter"
      printf "lxc_cpu_system_seconds_total%s %.6f\n",labels,system_cpu/1000000
      print "# TYPE lxc_cpu_capacity_cores gauge"
      printf "lxc_cpu_capacity_cores%s 2\n",labels
      print "# TYPE lxc_cpu_collector_success gauge"
      printf "lxc_cpu_collector_success%s 1\n",labels
      print "# TYPE lxc_cpu_collector_timestamp_seconds gauge"
      printf "lxc_cpu_collector_timestamp_seconds%s %s\n",labels,now
    }' "$HOST_ROOT/sys/fs/cgroup/cpu.stat" > "$METRIC_DIR/lxc-cpu.prom.tmp"; then
    mv "$METRIC_DIR/lxc-cpu.prom.tmp" "$METRIC_DIR/lxc-cpu.prom"
  else
    printf 'lxc_cpu_collector_success{ct_id="631",resource_scope="lxc",cpu_source="cgroup_v2"} 0\n' > "$METRIC_DIR/lxc-cpu.prom.tmp"
    mv "$METRIC_DIR/lxc-cpu.prom.tmp" "$METRIC_DIR/lxc-cpu.prom"
    return 1
  fi
}
update
[ "${1:-}" != --once ] || exit 0
(while sleep 5; do update || exit 1; done) &
exec /bin/node_exporter "$@"
