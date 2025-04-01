# -*- mode: python ; coding: utf-8 -*-
import sys
import os
from pathlib import Path

block_cipher = None

# Define project root directory explicitly using absolute path
root_dir = Path('S:/Projects/sidd/corrugated_box_mfg').absolute()

# Include all template directories
template_dirs = [
    (str(root_dir / 'templates'), 'templates'),
    (str(root_dir / 'inventory/templates'), 'inventory/templates'),
    (str(root_dir / 'finished_goods/templates'), 'finished_goods/templates'),
    (str(root_dir / 'accounts/templates'), 'accounts/templates'),
    (str(root_dir / 'data_cleanup/templates'), 'data_cleanup/templates'),
]

# Include all static directories
static_dirs = [
    (str(root_dir / 'static'), 'static'),
    (str(root_dir / 'inventory/static'), 'inventory/static'),
    (str(root_dir / 'finished_goods/static'), 'finished_goods/static'),
]

a = Analysis(
    [str(root_dir / 'run_server.py')],
    pathex=[str(root_dir)],
    binaries=[],
    datas=[
        (str(root_dir / 'box_mfg'), 'box_mfg'),
        (str(root_dir / 'manage.py'), '.'),
        (str(root_dir / 'db.sqlite3'), '.'),
        *template_dirs,  # Add all template directories
        *static_dirs,    # Add all static directories
        (str(root_dir / 'staticfiles'), 'staticfiles'),
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
        'accounts',
        'data_cleanup',
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