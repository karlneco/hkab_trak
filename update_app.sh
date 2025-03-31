#!/bin/bash
set -e

APP_NAME="hkabtrak"

echo "🔄 Pulling latest code..."
git pull origin main

echo "🧱 Rebuilding Docker image..."
docker compose build

echo "🚀 Restarting container..."
docker compose up -d

echo "✅ Done."