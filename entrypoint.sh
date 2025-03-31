#!/bin/sh

# Exit immediately if a command exits with a non-zero status
set -e

# Set Flask app environment variables
export FLASK_ENV=production
export FLASK_APP=main.py

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

# Start the Flask app with Gunicorn (HTTP only — SSL handled by Traefik)
echo "Starting Flask application with Gunicorn on port 8000..."
exec gunicorn -w 4 -b 0.0.0.0:8000 "main:app"