FROM python:3.10-slim-bookworm@sha256:5be5aaecb962a41567bc8041f1e9e3432cb085b037fe057f9a562630b2e4b370
RUN apt-get update && apt-get install -y --no-install-recommends build-essential libopenblas-dev ca-certificates && rm -rf /var/lib/apt/lists/*
COPY source/ /engine/
WORKDIR /engine
RUN make blas SIMD=portable -j2 && sha256sum qwen_tts > binary.sha256 && dpkg-query -W > build-packages.txt
ENV OPENBLAS_NUM_THREADS=2 OMP_NUM_THREADS=2
CMD ["./qwen_tts", "--caps"]
