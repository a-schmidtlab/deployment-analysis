# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['standalone.py'],
    pathex=[],
    binaries=[('C:\\WINDOWS\\System32\\msvcp140.dll', '.'), ('C:\\WINDOWS\\System32\\vcruntime140.dll', '.'), ('C:\\WINDOWS\\System32\\vcruntime140_1.dll', '.')],
    datas=[('data', 'data'), ('logs', 'logs'), ('output', 'output'), ('deployment-analyse.py', '.')],
    hiddenimports=['pandas', 'pandas.core.api', 'pandas.core.computation.expressions', 'numpy', 'numpy.core', 'numpy.random', 'matplotlib', 'matplotlib.backends.backend_tkagg', 'seaborn'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=['C:\\temp\\deploy_build\\build\\runtime_hooks\\numpy_hook.py', 'C:\\temp\\deploy_build\\build\\runtime_hooks\\debug_hook.py'],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='DeploymentAnalyzer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='DeploymentAnalyzer',
)
