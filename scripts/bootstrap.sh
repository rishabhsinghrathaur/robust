#!/usr/bin/env bash

set -euo pipefail

echo "Robust bootstrap"
echo "1. Copy .env.example to .env"
echo "2. Start infra with docker compose up -d"
echo "3. Set up backend, dashboard, and ai services independently"

