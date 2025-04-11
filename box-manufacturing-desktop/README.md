# Box Manufacturing CRM

## Overview
This project is a Customer Relationship Management (CRM) system tailored for a box manufacturing business. It is built using Django for the backend and Electron for the desktop application interface. This combination allows the application to leverage Django's robust web framework while providing a seamless desktop experience through Electron.

## Features
- **Inventory Management**: Track and manage inventory for items like paper reels, pasting gum, ink, strapping rolls, and pin coils.
- **Order Management**: Manage customer orders and track their status.
- **Activity Logs**: Maintain logs for inventory actions such as additions, deletions, and edits.
- **Summary Tables**: View aggregated data for inventory items.
- **Autocomplete Suggestions**: Provide suggestions for form fields based on existing data.

## How It Works
This project integrates Django and Electron to create a desktop application:
1. **Django Backend**: Handles the core business logic, database interactions, and API endpoints. It serves as the foundation for managing data and processing requests.
2. **Electron Frontend**: Wraps the Django application in a desktop environment, providing a native-like user interface. The Electron app communicates with the Django server running locally to fetch and display data.

## Project Structure
```
box-manufacturing-desktop/
├── package.json
├── build/
├── corrugated_box_mfg/
│   ├── manage.py
│   ├── requirements.txt
│   ├── accounts/
│   ├── box_mfg/
│   ├── data_cleanup/
│   ├── finished_goods/
│   ├── inventory/
│   ├── media/
│   ├── static/
│   ├── templates/
├── src/
│   ├── main.js
│   ├── preload.js
│   ├── loading.html
```

### Key Directories
- **`corrugated_box_mfg/`**: Contains the main Django application.
- **`src/`**: Contains the Electron application files, including the main process (`main.js`) and preload scripts.
- **`build/`**: Stores build artifacts for the Electron application.

## Installation
1. Clone the repository:
   ```bash
   git clone <repository-url>
   ```
2. Navigate to the project directory:
   ```bash
   cd box-manufacturing-desktop/corrugated_box_mfg
   ```
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

## Contributing
Contributions are welcome! Please follow these steps:
1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Commit your changes and push them to your fork.
4. Submit a pull request.

## License
This project is licensed under the MIT License. See the `LICENSE` file for details.

## Acknowledgments
- Built with Django, a high-level Python web framework.
- Uses Electron to provide a desktop application experience.
- Leverages various open-source libraries for enhanced functionality.