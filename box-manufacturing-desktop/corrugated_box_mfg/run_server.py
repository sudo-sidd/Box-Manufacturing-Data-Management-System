#!/usr/bin/env python
import os
import sys
from pathlib import Path
import logging
import django
import shutil

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def setup_django_environment():
    try:
        # Set the Django settings module
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'box_mfg.settings')

        # Determine if we're running in a PyInstaller bundle
        if getattr(sys, 'frozen', False):
            # Running in a PyInstaller bundle
            BASE_DIR = Path(sys._MEIPASS)
            logger.info(f"Running from PyInstaller bundle at {BASE_DIR}")
            
            # Set up paths for static files, templates and database
            static_root = Path(BASE_DIR) / 'staticfiles'
            os.environ['STATIC_ROOT'] = str(static_root)
            static_root.mkdir(exist_ok=True)
            
            template_dir = Path(BASE_DIR) / 'templates'
            os.environ['TEMPLATE_DIRS'] = str(template_dir)
            template_dir.mkdir(exist_ok=True)
            
            # Create media directory if it doesn't exist
            media_dir = Path(BASE_DIR) / 'media'
            media_dir.mkdir(exist_ok=True)
            os.environ['MEDIA_ROOT'] = str(media_dir)
            
            # Set database path to be next to the executable
            exe_dir = Path(sys.executable).parent
            db_path = exe_dir / 'db.sqlite3'
            
            if not db_path.exists():
                bundle_db = Path(BASE_DIR) / 'db.sqlite3'
                if bundle_db.exists():
                    shutil.copy2(str(bundle_db), str(db_path))
                    logger.info(f"Copied database to: {db_path}")
                else:
                    logger.warning("No database found in bundle")
            
            os.environ['DATABASE_PATH'] = str(db_path)
            logger.info(f"Using database at: {db_path}")
            
            # Add bundle directory to Python path
            if str(BASE_DIR) not in sys.path:
                sys.path.insert(0, str(BASE_DIR))
        
        else:
            # Running in development mode
            BASE_DIR = Path(__file__).resolve().parent
            logger.info(f"Running in development mode from {BASE_DIR}")
            if str(BASE_DIR) not in sys.path:
                sys.path.insert(0, str(BASE_DIR))

        # Initialize Django
        django.setup()
        return True

    except Exception as e:
        logger.error(f"Error setting up Django environment: {e}", exc_info=True)
        return False

def run_server():
    """Run the Django server with appropriate settings"""
    from django.core.management import execute_from_command_line
    
    try:
        if not setup_django_environment():
            logger.error("Failed to setup Django environment")
            input("Press Enter to exit...")
            return

        # Set server arguments
        if getattr(sys, 'frozen', False):
            server_args = ['django_app', 'runserver', '127.0.0.1:8000', '--noreload']
        else:
            server_args = sys.argv

        try:
            # Apply migrations
            logger.info("Applying migrations...")
            execute_from_command_line(['manage.py', 'migrate', '--noinput'])
            
            # Create superuser if needed
            from django.contrib.auth.models import User
            if not User.objects.filter(is_superuser=True).exists():
                logger.info("Creating default admin user...")
                User.objects.create_superuser('admin', 'admin@example.com', 'admin')
                logger.info("Default admin user created with username 'admin' and password 'admin'")
            
            # Start the server
            logger.info("Starting Django server on http://127.0.0.1:8000")
            execute_from_command_line(server_args)
        
        except Exception as e:
            logger.error(f"Error during server operations: {str(e)}")
            logger.error("Full error:", exc_info=True)
            logger.info("\nTroubleshooting steps:")
            logger.info("1. Check if port 8000 is available")
            logger.info("2. Verify database permissions")
            logger.info("3. Check static files directory permissions")
            logger.info("4. Ensure all required dependencies are installed")
            input("\nPress Enter to exit...")
    
    except Exception as e:
        logger.error(f"Critical error: {str(e)}")
        logger.error("Full error:", exc_info=True)
        input("\nPress Enter to exit...")

if __name__ == '__main__':
    run_server()

# -*- mode: python ; coding: utf-8 -*-
import sys
from pathlib import Path

block_cipher = None

# Get the absolute root directory of your project
root_dir = Path('s:/Projects/sidd/corrugated_box_mfg').resolve()

a = Analysis(
    [str(root_dir / 'run_server.py')],
    pathex=[str(root_dir)],
    binaries=[],
    datas=[
        (str(root_dir / 'box_mfg'), 'box_mfg'),
        (str(root_dir / 'manage.py'), '.'),
        (str(root_dir / 'db.sqlite3'), '.'),
        (str(root_dir / 'staticfiles'), 'staticfiles'),
        (str(root_dir / 'templates'), 'templates'),
        (str(root_dir / 'media'), 'media'),
    ],
    hiddenimports=[
        'django',
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'django.template.loader_tags',
        'django.template.defaulttags',
        'django.template.context_processors',
        'django.template.loaders.filesystem',
        'django.template.loaders.app_directories',
        'django.middleware',
        'django.urls.resolvers',
        'django.core.management',
        'django.core.management.commands.migrate',
        'django.core.management.commands.runserver',
        'django.core.management.commands.collectstatic',
        'crispy_forms',
        'rest_framework',
        'whitenoise',
        'whitenoise.middleware',
        'whitenoise.storage',
        'box_mfg',
        'finished_goods',
        'inventory',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='BoxMfg',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='BoxMfg',
)