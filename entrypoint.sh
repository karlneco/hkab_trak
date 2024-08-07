#!/bin/sh

# Exit immediately if a command exits with a non-zero status
set -e

# Set Flask app environment variable
export FLASK_APP=main.py

# Run database migrations
flask db init || true  # Ignore if the database is already initialized
flask db migrate -m "initial db"
flask db upgrade

# Allow time for database migrations to complete
sleep 5

# Create admin user (adjust the command if needed)
flask create-admin

# Start the Flask application with gunicorn
exec gunicorn -w 4 -b 0.0.0.0:1473 "main:app"