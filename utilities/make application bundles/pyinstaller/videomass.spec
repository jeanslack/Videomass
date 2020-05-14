# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['videomass'],
             pathex=['C:\\Users\\gianluca\\Documents\\Videomass-master'],
             binaries=[],
             datas=[('C:\\Users\\gianluca\\Documents\\Videomass-master\\art', 'art'), ('C:\\Users\\gianluca\\Documents\\Videomass-master\\locale', 'locale'), ('C:\\Users\\gianluca\\Documents\\Videomass-master\\share', 'share'), ('C:\\Users\\gianluca\\Documents\\Videomass-master\\Win32Setup\\FFMPEG_BIN', 'FFMPEG_BIN'), ('C:\\Users\\gianluca\\Documents\\Videomass-master\\Win32Setup\\NOTICE.rtf', 'DOC'), ('C:\\Users\\gianluca\\Documents\\Videomass-master\\AUTHORS', 'DOC'), ('C:\\Users\\gianluca\\Documents\\Videomass-master\\BUGS', 'DOC'), ('C:\\Users\\gianluca\\Documents\\Videomass-master\\CHANGELOG', 'DOC'), ('C:\\Users\\gianluca\\Documents\\Videomass-master\\COPYING', 'DOC'), ('C:\\Users\\gianluca\\Documents\\Videomass-master\\INSTALL', 'DOC'), ('C:\\Users\\gianluca\\Documents\\Videomass-master\\README.md', 'DOC'), ('C:\\Users\\gianluca\\Documents\\Videomass-master\\TODO', 'DOC')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=['youtube_dl'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='Videomass',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False , icon='C:\\Users\\gianluca\\Documents\\Videomass-master\\art\\videomass.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='Videomass')
