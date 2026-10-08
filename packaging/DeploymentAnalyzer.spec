# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller build of the Deployment Analyzer GUI.

Run from the repository root:
    pyinstaller --noconfirm --clean packaging/DeploymentAnalyzer.spec
"""

import os

from PyInstaller.utils.hooks import collect_data_files

ROOT = os.path.abspath(os.path.join(SPECPATH, os.pardir))

a = Analysis(
    [os.path.join(SPECPATH, "entry.py")],
    pathex=[os.path.join(ROOT, "src")],
    binaries=[],
    datas=collect_data_files("seaborn") + collect_data_files("matplotlib", subdir="mpl-data"),
    hiddenimports=[
        "matplotlib.backends.backend_tkagg",
        "matplotlib.backends.backend_pdf",
        "matplotlib.backends.backend_svg",
        "openpyxl",
        "PIL._tkinter_finder",
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=["IPython", "jupyter", "notebook", "pytest", "scipy", "tkinter.test"],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="DeploymentAnalyzer",
    debug=False,
    strip=False,
    upx=False,
    console=False,
)
coll = COLLECT(exe, a.binaries, a.datas, strip=False, upx=False, name="DeploymentAnalyzer")
