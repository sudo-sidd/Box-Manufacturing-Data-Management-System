#!/usr/bin/env python
import os
import sys
import platform
from pathlib import Path

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'box_mfg.settings')

# Determine if we're running in a PyInstaller bundle
if getattr(sys, 'frozen', False):
    # Running in a PyInstaller bundle
    BASE_DIR = Path(sys._MEIPASS)
    print(f"Running from PyInstaller bundle at {BASE_DIR}")
    
    # Set up paths for static files, templates and database
    os.environ['STATIC_ROOT'] = os.path.join(BASE_DIR, 'static')
    os.environ['TEMPLATE_DIRS'] = os.path.join(BASE_DIR, 'templates')
    
    # Create media directory if it doesn't exist
    media_dir = os.path.join(BASE_DIR, 'media')
    os.makedirs(media_dir, exist_ok=True)
    os.environ['MEDIA_ROOT'] = media_dir
    
    # Set database path
    db_path = os.path.join(os.path.dirname(sys.executable), 'db.sqlite3')
    if not os.path.exists(db_path):
        bundle_db = os.path.join(BASE_DIR, 'db.sqlite3')
        if os.path.exists(bundle_db):
            import shutil
            shutil.copy2(bundle_db, db_path)
    
    os.environ['DATABASE_PATH'] = db_path
    print(f"Database path: {db_path}")
else:
    BASE_DIR = Path(__file__).resolve().parent
    print(f"Running in development mode from {BASE_DIR}")

sys.path.insert(0, str(BASE_DIR))

def run_server():
    """Run the Django server with appropriate settings"""
    from django.core.management import execute_from_command_line
    
    # Set sys.argv for frozen environment
    if getattr(sys, 'frozen', False):
        sys.argv = ['django_app', 'runserver', '127.0.0.1:8000', '--noreload']
    
    # Apply migrations
    print("Applying migrations...")
    execute_from_command_line(['manage.py', 'migrate', '--noinput'])
    
    # Collect static files
    print("Collecting static files...")
    execute_from_command_line(['manage.py', 'collectstatic', '--noinput'])
    
    # Start the server
    print("Starting Django server on http://127.0.0.1:8000")
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    run_server()