#!/usr/bin/env bash
set -euo pipefail
umask 077
target="${1:?Expected private output path}"
mkdir -m 700 "$target"
openssl req -x509 -newkey rsa:3072 -noenc -days 1825 -sha256 \
    -subj '/CN=EVA internal origin CA' -addext 'basicConstraints=critical,CA:TRUE' \
    -addext 'keyUsage=critical,keyCertSign,cRLSign' \
    -keyout "$target/ca.key" -out "$target/origin-ca.crt" 2>/dev/null
for name in eva-api.internal eva-ui.internal; do
    openssl req -new -newkey rsa:2048 -noenc -subj "/CN=$name" \
        -keyout "$target/$name.key" -out "$target/$name.csr" 2>/dev/null
    openssl x509 -req -in "$target/$name.csr" -days 365 -sha256 \
        -CA "$target/origin-ca.crt" -CAkey "$target/ca.key" -CAcreateserial \
        -extfile <(printf 'subjectAltName=DNS:%s\nextendedKeyUsage=serverAuth\n' "$name") \
        -out "$target/$name.crt" 2>/dev/null
    openssl verify -CAfile "$target/origin-ca.crt" -verify_hostname "$name" "$target/$name.crt"
done
