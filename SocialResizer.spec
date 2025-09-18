# SocialResizer.spec
# Build with: python -m PyInstaller SocialResizer.spec

block_cipher = None

a = Analysis(
    ['social_resizer_gui.py'],
    pathex=[],
    binaries=[],
    datas=[('assets/social_resizer.ico', 'assets')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='SocialResizer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon='assets/social_resizer.ico',
)
coll = COLLECT(
    exe, a.binaries, a.zipfiles, a.datas,
    strip=False, upx=True, upx_exclude=[],
    name='SocialResizer'
)
