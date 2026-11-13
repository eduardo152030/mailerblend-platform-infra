#!/bin/sh
# CT627 CPU candidate: effective UID is already999. Never change users or owners.
set -eu
[ "$(id -u)" = 999 ] || { echo 'error: this image requires effective UID999' >&2; exit 1; }
for dir in /app/data /app/data/cache /app/data/profiles /app/data/generations /qwen-jobs \
           /home/voicebox/.cache /home/voicebox/.cache/huggingface; do
    mkdir -p "$dir" 2>/dev/null || { echo "error: cannot create required directory $dir as UID999" >&2; exit 1; }
    [ -r "$dir" ] && [ -w "$dir" ] && [ -x "$dir" ] || {
        echo "error: UID999 requires read/write/traverse access to $dir" >&2; exit 1;
    }
done
if [ -n "${NUMBA_CACHE_DIR:-}" ]; then
    mkdir -p "$NUMBA_CACHE_DIR" || exit 1
    [ -w "$NUMBA_CACHE_DIR" ] || { echo 'error: NUMBA_CACHE_DIR is not writable by UID999' >&2; exit 1; }
fi
for file in /app/backend/config.py /app/backend/models.py; do
    [ -r "$file" ] || { echo "error: UID999 cannot read $file" >&2; exit 1; }
done
if [ -e /app/data/voicebox.db ]; then
    [ -r /app/data/voicebox.db ] && [ -w /app/data/voicebox.db ] || {
        echo 'error: UID999 requires read/write access to voicebox.db' >&2; exit 1;
    }
fi
[ "$#" -gt 0 ] || { echo 'error: missing application command' >&2; exit 1; }
exec "$@"
