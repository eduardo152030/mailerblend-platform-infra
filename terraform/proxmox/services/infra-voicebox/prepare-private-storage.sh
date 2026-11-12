#!/usr/bin/env bash
# CT627 only: private exact originals, outside the API data volume.
set -euo pipefail
[[ $(hostname) == infra-voicebox ]]
[[ $(id -u) == 0 ]]
[[ ! -L /srv/voicebox/private-originals ]]
install -d -o root -g root -m 0700 /srv/voicebox/private-originals
