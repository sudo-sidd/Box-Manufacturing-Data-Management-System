import os
import sys
import platform
from PyInstaller.utils.hooks import collect_submodules, collect_data_files
from pathlib import Path

# Add the project root to Python path
sys.path.append(os.path.abspath(SPECPATH))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'box_mfg.settings')

block_cipher = None

# Platform-specific settings
is_windows = platform.system() == 'Windows'

# Collect all necessary Django and app-specific imports
hidden_imports = collect_submodules('django') + [
    'django.template.loader_tags',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'box_mfg',
    'box_mfg.urls',
    'box_mfg.settings',
    'box_mfg.wsgi',
    'inventory',
    'inventory.urls',
    'inventory.views',
    'inventory.models',
    'finished_goods',
    'finished_goods.urls',
    'finished_goods.views',
    'finished_goods.models',
    'whitenoise.middleware',
    'rest_framework',
    'rest_framework.views',
    'rest_framework.response',
    'rest_framework.parsers',
    'django.utils.autoreload'  # Add this
] + \
collect_submodules('whitenoise') + \
collect_submodules('rest_framework')

# Create necessary directories if they don't exist
for dir_name in ['media', 'static']:
    os.makedirs(os.path.join(SPECPATH, dir_name), exist_ok=True)

# Collect all necessary data files
datas = [
    (os.path.join(SPECPATH, 'static'), 'static'),
    (os.path.join(SPECPATH, 'templates'), 'templates'),
    (os.path.join(SPECPATH, 'inventory/templates'), 'inventory/templates'),
    (os.path.join(SPECPATH, 'finished_goods/templates'), 'finished_goods/templates'),
    (os.path.join(SPECPATH, 'media'), 'media'),
]

# Add database if it exists
if os.path.exists(os.path.join(SPECPATH, 'db.sqlite3')):
    datas.append((os.path.join(SPECPATH, 'db.sqlite3'), '.'))

# Add Django admin static files
django_admin_path = os.path.join(os.path.dirname(os.__file__), 'site-packages/django/contrib/admin/static')
if os.path.exists(django_admin_path):
    datas.append((django_admin_path, 'django/contrib/admin/static'))

a = Analysis(
    ['run_server.py'],
    pathex=[os.path.abspath(SPECPATH)],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['psycopg2'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='django_app',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)