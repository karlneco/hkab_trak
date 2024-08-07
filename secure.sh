#!/bin/bash

# Generate a new secret key
secret_key=$(python3 -c 'import secrets; print(secrets.token_hex(32))')

# Path to your original Docker run script
original_script="start.sh"

# Replace the placeholder with the new secret key
sed -i "s/your_secret_key_value/${secret_key}/g" ${original_script}

echo "New SECRET_KEY=${secret_key} has been updated in ${original_script}."