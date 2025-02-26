# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

datas = [('data', 'data'), ('logs', 'logs'), ('output', 'output'), ('deployment-analyse.py', '.')]
binaries = [('C:\\Users\\axels\\AppData\\Local\\Programs\\Python\\Python313\\python*.dll', '.'), ('C:\\Users\\axels\\AppData\\Local\\Programs\\Python\\Python313\\DLLs\\*.dll', '.')]
hiddenimports = ['pandas', 'numpy', 'matplotlib', 'matplotlib.backends.backend_tkagg', 'seaborn', 'configparser', 'tkinter', 'PIL']

# Exclude large CSV files and test directories from data collection
excludes = ['test', 'tests', 'testing', 'sample_data']

# Collect all required packages but exclude test directories and large data files
tmp_ret = collect_all('pandas', exclude_datas=[('**/Editorial_Importzeit*.csv', None), ('**/test*/**', None), ('**/sample_data/**', None)])
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]

tmp_ret = collect_all('numpy', exclude_datas=[('**/test*/**', None), ('**/sample_data/**', None)])
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]

tmp_ret = collect_all('matplotlib', exclude_datas=[('**/test*/**', None), ('**/sample_data/**', None)])
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]

tmp_ret = collect_all('seaborn', exclude_datas=[('**/test*/**', None)])
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]

tmp_ret = collect_all('openpyxl', exclude_datas=[('**/test*/**', None)])
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]

tmp_ret = collect_all('PIL', exclude_datas=[('**/test*/**', None)])
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['standalone.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    noarchive=False,
    optimize=0,
)

# Custom function to exclude files with specific patterns
def exclude_files(analysis):
    excluded_patterns = [
        '*Editorial_Importzeit*.csv',
        '*/test/*',
        '*/tests/*',
        '*/testing/*',
        '*/sample_data/*',
        '*.pdb',
        '*/__pycache__/*'
    ]
    
    filtered_datas = []
    for data in analysis.datas:
        should_exclude = False
        for pattern in excluded_patterns:
            import fnmatch
            if fnmatch.fnmatch(data[0], pattern):
                should_exclude = True
                break
        if not should_exclude:
            filtered_datas.append(data)
    
    analysis.datas = filtered_datas
    return analysis

# Apply exclusion filters
a = exclude_files(a)

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
