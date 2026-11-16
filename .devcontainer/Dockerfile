FROM mcr.microsoft.com/devcontainers/python:3.13-bookworm

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    strace \
    iproute2 \
    iputils-ping \
    curl \
    nodejs \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir uv

WORKDIR /workspaces/system-craft
