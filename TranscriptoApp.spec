# TranscriptoApp.spec
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

hidden = []  # añade módulos si alguno no se detecta (p.ej. 'soundfile')

block_cipher = None

whisper_datas  = collect_data_files('whisper',  includes=['assets/*'])
tiktoken_datas = collect_data_files('tiktoken', includes=['**/*'])  # para evitar futuros errores del tokenizador

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[
        ('vendor/ffmpeg/bin/ffmpeg.exe', 'ffmpeg'),
        ('vendor/ffmpeg/bin/ffprobe.exe', 'ffmpeg'),
    ],
    datas=whisper_datas + tiktoken_datas + [
        # ('assets/logo.png', 'assets'),
        # ('config.json', '.'),
    ],
    hiddenimports=hidden, # o: collect_submodules('tiktoken') si quieres ser extra-cauto
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
    a.binaries,
    a.zipfiles,
    a.datas,
    name='TranscriptoApp',   # 👈 Aquí defines el nombre del .exe
    console=False,          # True si quieres consola
    icon=None,              # 'assets/app.ico' si tienes icono
    onefile=True,   # 👈 Esto fuerza a que se genere un solo .exe
    # 👇 evita ventana extra en subprocesos en Windows
    disable_windowed_traceback=True,
    argv_emulation=False
)
