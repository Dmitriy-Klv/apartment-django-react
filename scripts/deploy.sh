#!/bin/sh
set -e

git pull
docker compose build
docker compose up -d
docker compose ps
