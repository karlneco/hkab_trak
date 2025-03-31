FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    certbot \
    cron \
    openssl \
    curl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app and entrypoint
COPY . .

# Make entrypoint executable
RUN chmod +x entrypoint.sh

# Copy the certbot renewal cron job
COPY renew-cron /etc/cron.d/renew-cron
RUN chmod 0644 /etc/cron.d/renew-cron && crontab /etc/cron.d/renew-cron

# Persist certs across container restarts (mount a volume here)
VOLUME ["/etc/letsencrypt", "/var/lib/letsencrypt"]

# Expose HTTP (for certbot) and HTTPS (for Flask SSL)
EXPOSE 80
EXPOSE 443
EXPOSE 5000

# Launch cron and Flask app
ENTRYPOINT ["./entrypoint.sh"]