# Nginx Service Project

This project sets up an Nginx service to host a web application with proper configurations for static and media files. It utilizes Docker for containerization, making it easy to deploy and manage.

## Project Structure

- **config/**: Contains Nginx configuration files.
  - **nginx.conf**: Main configuration for Nginx.
  - **sites-available/**: Directory for additional server configurations.
  
- **docker/**: Contains files for building and running the Docker container.
  - **Dockerfile**: Instructions for building the Nginx Docker image.
  - **docker-compose.yml**: Defines services and configurations for Docker.

- **scripts/**: Contains deployment and setup scripts.
  - **deploy.sh**: Script for deploying the Nginx service.
  - **setup.sh**: Script for initial setup tasks.

- **.env.example**: Template for environment variables.

- **.gitignore**: Specifies files to be ignored by Git.

## Setup Instructions

1. **Clone the Repository**:
   ```
   git clone <repository-url>
   cd nginx-service
   ```

2. **Copy the Environment Variables**:
   ```
   cp .env.example .env
   ```

3. **Build the Docker Image**:
   ```
   docker-compose build
   ```

4. **Start the Services**:
   ```
   docker-compose up
   ```

5. **Access the Application**:
   Open your web browser and navigate to `http://localhost`.

## Usage Guidelines

- Modify the `config/nginx.conf` file to adjust Nginx settings as needed.
- Use the `scripts/deploy.sh` script for deployment tasks.
- Update the `.env` file with your environment-specific variables.

## Contributing

Feel free to submit issues or pull requests for improvements or bug fixes.