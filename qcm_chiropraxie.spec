# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for QCM Chiropraxie
Builds a standalone macOS .app bundle
"""

import os
from pathlib import Path

block_cipher = None

# Get the repo root (where this spec file lives)
REPO_ROOT = Path(SPECPATH)

# Collect all data files to include in the bundle
datas = [
    # Main HTML interface
    (str(REPO_ROOT / 'app.html'), '.'),
    # Web assets (bank, decks, styles)
    (str(REPO_ROOT / 'web'), 'web'),
    # Bank build scripts (for rebuilding bank.json)
    (str(REPO_ROOT / 'bank'), 'bank'),
    # Source files for question generation
    (str(REPO_ROOT / 'generate_qcm_400.py'), '.'),
    (str(REPO_ROOT / 'tissus_conjonctifs_extracted.txt'), '.'),
]

# Filter out non-existent paths
datas = [(src, dst) for src, dst in datas if os.path.exists(src)]

a = Analysis(
    ['start_qcm.py'],
    pathex=[str(REPO_ROOT)],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'email',
        'email.utils',
        'email.parser',
        'email.message',
        'html.parser',
        'http.server',
        'socketserver',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'unittest',
        'pydoc',
        'doctest',
        'pickle',
        'sqlite3',
        'ssl',
        'ftplib',
        'imaplib',
        'poplib',
        'smtplib',
        'telnetlib',
        'xmlrpc',
    ],
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
    name='QCM Chiropraxie',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # No terminal window
    disable_windowed_traceback=False,
    argv_emulation=True,  # Required for macOS .app
    target_arch=None,  # Use current architecture (or 'universal2' for both)
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
    name='QCM Chiropraxie',
)

app = BUNDLE(
    coll,
    name='QCM Chiropraxie.app',
    icon=None,  # Add 'assets/icon.icns' when available
    bundle_identifier='com.dmicheneau.qcm-chiropraxie',
    info_plist={
        'CFBundleName': 'QCM Chiropraxie',
        'CFBundleDisplayName': 'QCM Chiropraxie',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHighResolutionCapable': True,
        'LSMinimumSystemVersion': '10.15',
        'NSRequiresAquaSystemAppearance': False,  # Support dark mode
    },
)
