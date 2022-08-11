# -*- mode: python ; coding: utf-8 -*-
from kivy_deps import sdl2, glew
block_cipher = None


a = Analysis(['..\\Proxyshop\main.py'],
             pathex=[],
             binaries=[],
             datas=[],
             hiddenimports=[
                'proxyshop.templates',
                'proxyshop.gui',
                'kivy',
                'svglib.svglib',
                'reportlab.graphics',
                'requests',
                'googleapiclient.discovery'
             ],
             hookspath=["proxyshop/hooks"],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

a.datas += [
    ('fonts/Beleren Small Caps.ttf', 'fonts/Beleren Small Caps.ttf', 'DATA'),
    ('proxyshop/gdrive.yaml', 'proxyshop/gdrive.yaml', 'DATA'),
    ('proxyshop/img/proxyshop.png', 'proxyshop/img/proxyshop.png', 'DATA')
]

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,  
          *[Tree(p) for p in (sdl2.dep_bins + glew.dep_bins)],
          name='Proxyshop',
          debug=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          icon='proxyshop/img/favicon.ico')