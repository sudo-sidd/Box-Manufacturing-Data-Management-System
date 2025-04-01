#!/bin/bash

# This script is used for initial setup tasks for the Nginx service project.

# Update package list and install necessary packages
sudo apt-get update
sudo apt-get install -y nginx docker.io docker-compose

# Start and enable Docker service
sudo systemctl start docker
sudo systemctl enable docker

# Create necessary directories for Nginx
sudo mkdir -p /app/staticfiles
sudo mkdir -p /app/media

# Copy Nginx configuration files to the appropriate location
sudo cp config/nginx.conf /etc/nginx/nginx.conf
sudo cp config/sites-available/default.conf /etc/nginx/sites-available/default

# Test Nginx configuration for syntax errors
sudo nginx -t

# Restart Nginx to apply changes
sudo systemctl restart nginx

echo "Setup completed successfully."