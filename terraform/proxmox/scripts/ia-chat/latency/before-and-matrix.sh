#!/bin/sh
# PVE: ejecutar solo bajo el alcance IA-CHAT-LATENCY; la matriz detiene630router.
set -eu
python3 /root/ia-local/latency/long-prompt.py long-before-gemma gemma-4-26b
python3 /root/ia-local/latency/swap-report.py gemma-loaded-before
python3 /root/ia-local/latency/guarded-warm.py latency-before-qwen qwen3.6-35b
python3 /root/ia-local/latency/long-prompt.py long-before-qwen qwen3.6-35b
python3 /root/ia-local/latency/swap-report.py qwen-loaded-before
python3 /root/ia-local/latency/benchmark-matrix.py
