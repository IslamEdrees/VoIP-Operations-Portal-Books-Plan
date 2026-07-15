#!/usr/bin/env bash

set -euo pipefail

echo
echo "========================================="
echo " STEP 01 - SYSTEM REQUIREMENTS"
echo "========================================="

if [ "$(id -u)" -ne 0 ]; then
    echo "ERROR: Run installer as root."
    exit 1
fi

if [ ! -f /etc/os-release ]; then
    echo "Unsupported OS."
    exit 1
fi

. /etc/os-release

echo "Detected OS : $PRETTY_NAME"

if [ "$ID" != "ubuntu" ]; then
    echo "Only Ubuntu is supported."
    exit 1
fi

echo
echo "Updating package index..."

apt-get update

echo
echo "Installing required packages..."

DEBIAN_FRONTEND=noninteractive apt-get install -y \
git \
curl \
wget \
unzip \
zip \
vim \
nano \
tree \
jq \
software-properties-common \
apt-transport-https \
ca-certificates \
gnupg \
lsb-release \
build-essential \
python3 \
python3-pip \
python3-venv

echo
echo "Installed versions"

git --version

python3 --version

pip3 --version

curl --version | head -1

echo
echo "STEP 01 SUCCESS"
