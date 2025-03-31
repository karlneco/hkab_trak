#!/bin/sh

# Exit immediately if a command exits with a non-zero status
set -e

# Set Flask app environment variable
export FLASK_ENV=production
export FLASK_APP=main.py

# Start cron in the background
cron

# Initialize database migrations if the migrations folder does not exist
flask db init || true

# Function to run database migrations
migrate_db() {
    echo "Running database migrations..."
    flask db migrate -m "initial db" || echo "Skipping migration creation; it might already exist."
    flask db upgrade
}

# Run migrations
migrate_db

# Allow time for database migrations to complete
sleep 3

# Create admin user
echo "Creating admin user..."
flask create-admin

if [ ! -f "$CERT_PATH" ] || [ ! -f "$KEY_PATH" ]; then
  echo "Generating new SSL certificate for $DOMAIN..."
  certbot certonly --standalone --non-interactive --agree-tos -m "$EMAIL" -d "$DOMAIN"
else
  echo "SSL certificate already exists."
fi

ln -sf /etc/letsencrypt/live/absent.calgaryhoshuko.org/fullchain.pem /app/server.crt
ln -sf /etc/letsencrypt/live/absent.calgaryhoshuko.org/privkey.pem /app/server.key

# Start the Flask app with gunicorn and certs
echo "Starting Flask application with Gunicorn and SSL..."
exec gunicorn -w 4 -b 0.0.0.0:1473 --keyfile "$KEY_PATH" --certfile "$CERT_PATH" "main:app"