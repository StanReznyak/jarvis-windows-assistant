# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path
import importlib.util
from PyInstaller.utils.hooks import collect_submodules, collect_dynamic_libs, collect_data_files

root = Path(SPECPATH)

base_datas = [
    (str(root / 'assets'), 'assets'),
    (str(root / 'data' / '.gitkeep'), 'data'),
    (str(root / 'model'), 'model'),
    (str(root / 'models'), 'models'),
    (str(root / 'config.example.json'), '.'),
    (str(root / 'VERSION.txt'), '.'),
    (str(root / 'portable_mode.flag'), '.'),
]

for helper_name in [
    'SETUP_LOCAL_MODEL_WINDOWS.bat',
    'CHECK_LOCAL_MODEL_WINDOWS.bat',
    'SET_CLOUD_KEY_WINDOWS.bat',
    'REMOVE_CLOUD_KEY_WINDOWS.bat',
    'CLEAR_REMINDERS_WINDOWS.bat',
    'QUICK_START_RU.txt',
    'MODEL_SETUP_RU.txt',
    'README.md',
    'README_RU.txt',
    'ARCHITECTURE_RU.md',
    'CHANGELOG.txt',
]:
    helper_path = root / helper_name
    if helper_path.exists():
        base_datas.append((str(helper_path), '.'))

packages = ['sounddevice', 'vosk', 'openai', 'httpx', 'httpcore', 'pydantic']
optional_packages = ['faster_whisper', 'ctranslate2', 'av']

extra_datas = []
hiddenimports = ['jarvis', 'jarvis.app', 'jarvis.core', 'jarvis.ui', 'numpy', 'sounddevice', 'vosk', 'openai', 'httpx', 'httpcore', 'pydantic']
binaries = []

for pkg in packages + optional_packages:
    if importlib.util.find_spec(pkg) is None:
        continue
    try:
        extra_datas += collect_data_files(pkg)
    except Exception:
        pass
    try:
        hiddenimports += collect_submodules(pkg)
    except Exception:
        pass

for pkg in ['sounddevice', 'ctranslate2', 'av']:
    if importlib.util.find_spec(pkg) is None:
        continue
    try:
        binaries += collect_dynamic_libs(pkg)
    except Exception:
        pass

datas = base_datas + extra_datas

a = Analysis(
    ['main.py'],
    pathex=[str(root)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='JARVIS',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon=str(root / 'assets' / 'jarvis_icon.ico'),
    version=str(root / 'file_version_info.txt'),
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    name='JARVIS',
)
