#!/usr/bin/env bash

set -euo pipefail

echo
echo "========================================="
echo " STEP 04 - DOCKER ENGINE"
echo "========================================="

if command -v docker >/dev/null 2>&1; then

    echo "Docker already installed."

else

    apt-get update

    DEBIAN_FRONTEND=noninteractive apt-get install -y \
        ca-certificates \
        curl \
        gnupg \
        lsb-release

    install -m 0755 -d /etc/apt/keyrings

    curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
        | gpg --dearmor -o /etc/apt/keyrings/docker.gpg

    chmod a+r /etc/apt/keyrings/docker.gpg

    echo \
"deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
$(. /etc/os-release && echo "$VERSION_CODENAME") stable" \
> /etc/apt/sources.list.d/docker.list

    apt-get update

    DEBIAN_FRONTEND=noninteractive apt-get install -y \
        docker-ce \
        docker-ce-cli \
        containerd.io \
        docker-buildx-plugin \
        docker-compose-plugin

fi

systemctl enable docker

systemctl start docker

echo

docker --version

echo

docker compose version

echo

systemctl is-active docker

echo

docker ps

echo

echo "STEP 04 SUCCESS"

