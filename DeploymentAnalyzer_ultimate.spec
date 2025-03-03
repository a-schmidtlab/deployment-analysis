# -*- mode: python -*- 
from PyInstaller.utils.hooks import collect_all 
 
datas = [('data', 'data'), ('logs', 'logs'), ('output', 'output'), ('deployment-analyse.py', '.'), ('version.py', '.')] 
binaries = [] 
 
# Explicitly add Python DLLs 
import os, glob 
python_dlls = glob.glob(os.path.join(r'C:\Users\axels\AppData\Local\Programs\Python\Python313', '*.dll')) 
python_dlls += glob.glob(os.path.join(r'C:\Users\axels\AppData\Local\Programs\Python\Python313', 'DLLs', '*.dll')) 
for dll in python_dlls: 
    binaries.append((dll, '.')) 
 
# VC Runtime files 
vc_dlls = glob.glob(os.path.join(os.environ['WINDIR'], 'System32', 'msvcp*.dll')) 
vc_dlls += glob.glob(os.path.join(os.environ['WINDIR'], 'System32', 'vcruntime*.dll')) 
for dll in vc_dlls: 
    binaries.append((dll, '.')) 
 
# Add TK/TCL resources 
import site 
site_packages = site.getsitepackages()[0] 
tcl_dir = os.path.join(r'C:\Users\axels\AppData\Local\Programs\Python\Python313', 'tcl') 
if os.path.exists(tcl_dir): 
    for root, dirs, files in os.walk(tcl_dir): 
        for file in files: 
            full_path = os.path.join(root, file) 
            rel_path = os.path.relpath(full_path, r'C:\Users\axels\AppData\Local\Programs\Python\Python313') 
            target_dir = os.path.dirname(rel_path) 
            datas.append((full_path, target_dir)) 
 
# Special handling for numpy to avoid source directory import issues 
import numpy 
numpy_path = os.path.dirname(numpy.__file__) 
numpy_dlls = glob.glob(os.path.join(numpy_path, 'core', '*.dll')) 
numpy_dlls += glob.glob(os.path.join(numpy_path, 'random', '*.dll')) 
numpy_dlls += glob.glob(os.path.join(numpy_path, 'linalg', '*.dll')) 
numpy_dlls += glob.glob(os.path.join(numpy_path, 'fft', '*.dll')) 
for dll in numpy_dlls: 
    rel_path = os.path.join('numpy', os.path.relpath(os.path.dirname(dll), numpy_path)) 
    binaries.append((dll, rel_path)) 
 
# Add package dependencies 
hiddenimports = ['pandas', 'numpy', 'numpy.core', 'numpy.random', 'numpy.linalg', 'numpy.fft', 
                 'matplotlib', 'matplotlib.backends.backend_tkagg', 
                 'seaborn', 'configparser', 'tkinter', 'PIL', 'csv', 'openpyxl', 
                 'logging', 'logging.handlers', 'datetime', 'argparse', 'threading'] 
 
# Collect all dependencies 
packages = ['pandas', 'matplotlib', 'seaborn', 'PIL', 'openpyxl'] 
for package in packages: 
    tmp_ret = collect_all(package) 
    datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2] 
 
# Special collection for numpy with exclude 
numpy_ret = collect_all('numpy') 
datas += numpy_ret[0] 
binaries += numpy_ret[1] 
hiddenimports += numpy_ret[2] 
 
# Create the Analysis object 
a = Analysis( 
    ['standalone.py'], 
    pathex=[], 
    binaries=binaries, 
    datas=datas, 
    hiddenimports=hiddenimports, 
    hookspath=[], 
    hooksconfig={}, 
    runtime_hooks=[], 
    excludes=[], 
    noarchive=False, 
    optimize=0, 
) 
 
# Add the pyz 
pyz = PYZ(a.pure) 
 
# Create the exe 
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
    console=True, # Set to True for debugging 
    disable_windowed_traceback=False, 
    argv_emulation=False, 
    target_arch=None, 
    codesign_identity=None, 
    entitlements_file=None, 
) 
 
# Create the collection 
coll = COLLECT( 
    exe, 
    a.binaries, 
    a.datas, 
    strip=False, 
    upx=True, 
    upx_exclude=[], 
    name='DeploymentAnalyzer', 
) 
