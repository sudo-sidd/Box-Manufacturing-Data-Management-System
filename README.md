# Corrugation Plant Management System

## Executive Summary

The Corrugation Plant Management System is a unified platform for managing raw materials, production planning, operations, attendance, and reporting in a corrugated box manufacturing environment. Built with Django (backend) and Electron (desktop app), and designed with DevOps best practices, it enables real-time tracking, automation, and analytics for plant operations.

## Objectives
- Real-time tracking of raw materials and live stock display
- Automated deduction of materials per process step
- Operations planning with pre-saved box specs and workflows
- Production execution with efficiency and waste tracking
- Attendance planning and cost analysis
- Comprehensive dashboards and reporting

## Key Features

### Inventory Management
- Purchase entry for all raw materials (paper reels, gum, ink, pin coils, strapping rolls)
- Live stock display and shortage alerts
- Automatic deduction and waste logging per process

### Operations Planning
- Box template management with dimensional and material formulas
- Price quote generation based on live costs and margins
- Configurable process flows (corrugation, pasting, creasing, printing, stitching, bundling, counting)

### Production Execution
- Interactive shop-floor module for operators
- Real-time input of times, material usage, waste, and issues
- Auto-calculation of efficiency metrics

### Attendance & Costing
- Daily attendance capture and personnel utilization
- Cost calculation per person per hour, including bonuses and overhead

### Reporting & Analytics
- Actual vs. planned consumption, waste, and efficiency
- Finished goods, scrap, and inventory aging
- Cost and variance analysis dashboards

## System Architecture

```
+----------------------+       +------------------+       +--------------------+
|  Web & Desktop UI    || API Gateway      || Microservices      |
|  (Operators, Admin)  |       +------------------+       | - Inventory        |
+----------------------+                                 | - Planning         |
                                                        | - Production       |
                                                        | - Attendance       |
                                                        | - Reporting        |
                                                        +--------------------+
                                                                |
                                                                v
                                                        +--------------------+
                                                        |  PostgreSQL / NoSQL |
                                                        +--------------------+
                                                                |
                                                                v
                                                        +--------------------+
                                                        |  DevOps Toolchain   |
                                                        | - GitLab CI/CD      |
                                                        | - Docker & Kubernetes|
                                                        | - Prometheus & Grafana|
                                                        +--------------------+
```

- **Backend:** Django (Python), modular apps for inventory, planning, production, attendance, and reporting
- **Frontend:** Electron desktop app (see `src/`)
- **Database:** SQLite (dev), PostgreSQL (prod), NoSQL for logs (future)
- **DevOps:** GitLab CI/CD, Docker, Kubernetes, Prometheus, Grafana

## Project Structure

```
box-manufacturing-desktop/
├── package.json         # Electron app config
├── corrugated_box_mfg/  # Django backend
│   ├── manage.py
│   ├── requirements.txt
│   ├── box_mfg/         # Django project settings
│   ├── accounts/        # User management
│   ├── data_cleanup/    # Data cleaning utilities
│   ├── finished_goods/  # Finished goods module
│   ├── inventory/       # Inventory management
│   ├── ...
├── src/                # Electron app source
│   ├── main.js
│   ├── preload.js
│   ├── loading.html
```

## Setup & Installation

### 1. Backend (Django)

```fish
# From the project root:
cd box-manufacturing-desktop/corrugated_box_mfg

# (Recommended) Create a virtual environment
python3 -m venv venv
source venv/bin/activate.fish

# Install dependencies
pip install -r requirements.txt

# Apply migrations
python manage.py migrate

# Create a superuser (for admin access)
python manage.py createsuperuser

# Run the development server (default: http://127.0.0.1:8000)
python manage.py runserver
```

### 2. Desktop App (Electron)

```fish
cd box-manufacturing-desktop
npm install
npm start
```

## Usage

- Access the app via the Electron desktop interface (or browser at http://127.0.0.1:8000)
- Log in with your credentials
- Use inventory, planning, production, and reporting modules as per your workflow

## DevOps & CI/CD

- Version control: GitLab (protected branches, merge requests)
- CI/CD: Automated build, test, security scan, and deployment pipelines
- Containerization: Docker images for backend and frontend
- Orchestration: Kubernetes with Helm charts
- Monitoring: Prometheus (metrics), Grafana (dashboards), ELK (logs)
- Infrastructure as Code: Terraform for cloud resources

## Testing

Run backend tests:
```fish
python manage.py test
```

## Implementation Roadmap

| Phase | Timeline      | Key Activities                                    |
|-------|---------------|---------------------------------------------------|
| 1     | Month 1–2     | Requirements refinement; architecture design      |
| 2     | Month 3–4     | Core inventory and planning modules; CI/CD setup  |
| 3     | Month 5–6     | Production execution workflows; attendance module |
| 4     | Month 7       | Reporting dashboards; analytics integration       |
| 5     | Month 8       | User acceptance testing; DevOps tuning            |
| 6     | Month 9       | Production rollout; monitoring & support handover |

## Non-Functional Requirements
- Scalability: Modular, microservices-ready
- Availability: 99.9% uptime target
- Security: Role-based access, encryption
- Performance: Sub-second response for stock queries
- Usability: Responsive, intuitive UI

## Acknowledgments
- Built with Django, Electron, and open-source libraries
- DevOps toolchain: GitLab, Docker, Kubernetes, Prometheus, Grafana

## Reference
- [Corrugation Plant Data Model (Excel)](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/41149007/faea3466-7507-4a8a-be62-806c36d629b7/software-development-data-corrugation-plant.xlsx)
3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Install Node.js dependencies:
   ```bash
   cd ../src
   npm install
   ```
5. Apply migrations:
   ```bash
   python manage.py migrate
   ```
6. Run the development server:
   ```bash
   python manage.py runserver
   ```
7. Start the Electron application:
   ```bash
   npm start
   ```

## Usage

- Access the application through the Electron desktop interface.
- Log in with your credentials to access the dashboard.
- Use the inventory management features to add, edit, or delete items.

## Development

### Prerequisites

- Python 3.8+
- Django 3.2+
- Node.js (for managing frontend dependencies)

### Running Tests

To run tests, use the following command:

```bash
python manage.py test
```

## Acknowledgments

- Built with Django, a high-level Python web framework.
- Uses Electron to provide a desktop application experience.
- Leverages various open-source libraries for enhanced functionality.
