#!/bin/sh
# Build a candidate only. Never deploy, restart production or start inference.
set -eu
[ "$(hostname)" = infra-voicebox ]
[ "$(docker image inspect --format '{{.Id}}' local/voicebox:d085-candidate)" = sha256:19af4754968dacacbb9104f8ea40826dbea4f9f772992397cf322802d7babbfe ]
exec docker build --network none --pull=false -t local/voicebox:d086-uid999-candidate "${1:-/srv/voicebox/chatterbox-d085/startup-fix}"
