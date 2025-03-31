#!/bin/sh

# Exit immediately if a command exits with a non-zero status
set -e

# Set Flask app environment variables
export FLASK_ENV=production
export FLASK_APP=main.py

# Define domain and email for SSL (these can be passed in via environment or hardcoded)
export DOMAIN=absent.calgaryhoshuko.org
export EMAIL=admin@calgaryhoshuko.org

# Define paths to SSL cert/key
export CERT_PATH=/etc/letsencrypt/live/$DOMAIN/fullchain.pem
export KEY_PATH=/etc/letsencrypt/live/$DOMAIN/privkey.pem

# Start cron (needed if using certbot renew via cron later)
cron

# Initialize database migrations if the migrations folder does not exist
flask db init || true

# Run migrations
migrate_db() {
    echo "Running database migrations..."
    flask db migrate -m "initial db" || echo "Skipping migration creation; it might already exist."
    flask db upgrade
}
migrate_db

# Allow time for DB setup
sleep 3

# Create admin user
echo "Creating admin user..."
flask create-admin

# Generate cert if not present
if [ ! -f "$CERT_PATH" ] || [ ! -f "$KEY_PATH" ]; then
  echo "Generating new SSL certificate for $DOMAIN..."
  certbot certonly --standalone --non-interactive --agree-tos -m "$EMAIL" -d "$DOMAIN"
else
  echo "SSL certificate already exists."
fi

# (Optional) Symlink for compatibility
ln -sf "$CERT_PATH" /app/server.crt
ln -sf "$KEY_PATH" /app/server.key

# Start the Flask app with Gunicorn and SSL
echo "Starting Flask application with Gunicorn and SSL..."
exec gunicorn -w 4 -b 0.0.0.0:1473 --keyfile "$KEY_PATH" --certfile "$CERT_PATH" "main:app"