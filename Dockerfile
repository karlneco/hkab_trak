FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy and install requirements
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app
COPY . .

# Make entrypoint script executable
RUN chmod +x entrypoint.sh

# Expose the internal port used by Gunicorn
EXPOSE 8000

# Run the entrypoint script
ENTRYPOINT ["./entrypoint.sh"]