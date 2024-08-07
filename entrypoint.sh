#!/bin/sh

# Exit immediately if a command exits with a non-zero status
set -e

# Set Flask app environment variable
export FLASK_APP=main.py

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
sleep 5

# Create admin user
echo "Creating admin user..."
flask create-admin

# Start the Flask application with Gunicorn
echo "Starting Flask application with Gunicorn..."
exec gunicorn -w 4 -b 0.0.0.0:1473 "main:app"
