#!/bin/bash
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y --no-install-recommends ca-certificates wget curl git cmake build-essential pkg-config libssl-dev python3 python3-pil fonts-dejavu-core
if [ ! -d /opt/llama.cpp/.git ]; then
 git clone --branch v1.0.0 --depth 1 https://github.com/ggml-org/llama.cpp.git /opt/llama.cpp
fi
cd /opt/llama.cpp
test "$(git describe --tags --exact-match)" = v1.0.0
test "$(git rev-parse HEAD)" = b1b770d90d94cad9e9ea5b993bdbc383a522fb28
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release -DGGML_NATIVE=ON -DGGML_CUDA=OFF -DLLAMA_BUILD_TESTS=OFF -DLLAMA_BUILD_EXAMPLES=ON
cmake --build build --config Release --target llama-server llama-bench -j 3
build/bin/llama-server --help > /root/llama-server-help.txt
build/bin/llama-bench --help > /root/llama-bench-help.txt
git rev-parse HEAD > /root/llama-commit.txt
