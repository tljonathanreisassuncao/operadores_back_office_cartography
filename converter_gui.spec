import os
import pathlib
from PyInstaller.utils.hooks import collect_submodules

project_dir = str(pathlib.Path(".").resolve())

a = Analysis(
    ['converter_tps_gui.py'],
    pathex=[project_dir],
    binaries=[],
    datas=[
        ('ConvertRinex/tps2rin.exe', 'ConvertRinex'),
        ('img/icon.png', 'img'),
        ('arquivos/*', 'arquivos'),
        ('resultados_voos/*', 'resultados_voos'),
        ('resultados_rinex/*', 'resultados_rinex'),
    ],
    hiddenimports=collect_submodules('PIL') + ["PIL.Image", "PIL.ImageTk"],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
)
