# transcriptor.py
import os
import sys
from pathlib import Path
import whisper
import torch

# --- Asegurar stdout/stderr en apps sin consola ---
def _ensure_console_streams():
    if sys.stdout is None:
        sys.stdout = open(os.devnull, "w")
    if sys.stderr is None:
        sys.stderr = open(os.devnull, "w")

_ensure_console_streams()  # al importar (proceso padre y también en el hijo al importar)

# -------------------------------------------------------
# 1) ffmpeg incluido en el bundle (PyInstaller --onefile)
# -------------------------------------------------------
def _resource_path(rel: str) -> Path:
    """
    Devuelve la ruta absoluta a un recurso empaquetado.
    Soporta ejecución normal y PyInstaller (--onefile usa _MEIPASS).
    """
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return (base / rel).resolve()

def _prepare_ffmpeg_in_bundle() -> None:
    """
    Asegura que la carpeta 'ffmpeg' quede en PATH para ffmpeg/ffprobe.
    Llamar al inicio del proceso (padre e hijo).
    """
    ffmpeg_dir = _resource_path("ffmpeg")
    if ffmpeg_dir.exists():
        os.environ["PATH"] = str(ffmpeg_dir) + os.pathsep + os.environ.get("PATH", "")
        # Algunas libs respetan estas variables:
        os.environ.setdefault("FFMPEG_BINARY", "ffmpeg")
        os.environ.setdefault("FFPROBE_BINARY", "ffprobe")

# Ejecuta también al importar el módulo (sirve en el padre y en el hijo)
_prepare_ffmpeg_in_bundle()

# -------------------------------------------------------
# 2) Carga de modelos (con caché) y transcripción
# -------------------------------------------------------
_model_cache = {}

def get_model(model_name: str = "base"):
    """
    Obtiene (y cachea) un modelo Whisper por nombre.
    Si hay GPU usa CUDA; si no, CPU.
    """
    if model_name not in _model_cache:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        _model_cache[model_name] = whisper.load_model(model_name, device=device)
    return _model_cache[model_name]

def transcribir_archivo(ruta_audio: str, model_name: str = "base") -> str:
    """
    Transcribe un archivo de audio. Limpia espacios/saltos al inicio y al final.
    """
    _ensure_console_streams()    # por si este módulo se importó antes del fix
    _prepare_ffmpeg_in_bundle()  # idempotente; asegura PATH correcto
    modelo = get_model(model_name)
    usar_gpu = torch.cuda.is_available()
    # Evita warning en CPU: fp16 solo en GPU y 
    # desactiva progreso/salidas de Whisper para evitar escribir en stderr
    resultado = modelo.transcribe(ruta_audio, fp16=usar_gpu, verbose=False)
    texto = resultado.get("text", "")
    return (texto or "").strip()

# -------------------------------------------------------
# 3) Worker para multiprocessing (botón Cancelar real)
# -------------------------------------------------------
def _worker_transcribir(ruta_audio: str, model_name: str, queue):
    """
    Función objetivo del proceso hijo.
    Devuelve el texto por la queue; si falla, devuelve 'ERROR: ...'
    """
    try:
        _ensure_console_streams()    # crítico en el proceso hijo
        _prepare_ffmpeg_in_bundle()  # crítico en el proceso hijo
        texto = transcribir_archivo(ruta_audio, model_name=model_name)
        queue.put(texto)
    except Exception as e:
        queue.put(f"ERROR: {e}")
