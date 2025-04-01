#!/bin/bash

# Navigate to the directory containing the Docker Compose file
cd "$(dirname "$0")/../docker"

# Build the Docker image for the Nginx service
docker-compose build

# Start the Nginx service and any other defined services
docker-compose up -d

# Optionally, you can include commands to check the status of the services
docker-compose ps

# Print a message indicating that the deployment is complete
echo "Nginx service deployed successfully."