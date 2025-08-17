import whisper
import torch

# Caché de modelos para no recargar si el usuario cambia de modelo
_model_cache = {}

def get_model(model_name: str = "base"):
    """
    Obtiene (y cachea) un modelo Whisper por nombre.
    """
    if model_name not in _model_cache:
        # Cárgalo en GPU si existe; si no, en CPU
        device = "cuda" if torch.cuda.is_available() else "cpu"
        # Carga el modelo y guárdalo en caché
        _model_cache[model_name] = whisper.load_model(model_name, device=device)
    return _model_cache[model_name]

def transcribir_archivo(ruta_audio: str, model_name: str = "base") -> str:
    """
    Transcribe un archivo de audio usando Whisper local.
    :param ruta_audio: Ruta al archivo de audio (mp3, wav, m4a, etc.)
    :param model_name: Modelo whisper a usar (tiny, base, small, medium, large)
    :return: Texto transcrito (limpio al inicio y al final)
    """
    # Obtiene el modelo (cargado en GPU si es posible)
    modelo = get_model(model_name)
    # Verifica que el archivo existe
    usar_gpu = torch.cuda.is_available()
    # Evita la advertencia: sólo usa fp16 si hay GPU
    resultado = modelo.transcribe(ruta_audio, fp16=usar_gpu)
    # Extrae el texto del resultado
    texto = resultado.get("text", "")
    # Limpieza: quita espacios/saltos al inicio y fin
    return (texto or "").strip()

# === Soporte para ejecución en subproceso ===
def _worker_transcribir(ruta_audio: str, model_name: str, queue):
    """
    Función objetivo del proceso hijo: hace la transcripción y coloca el texto en la queue.
    Cualquier excepción se devuelve como cadena que empiece con 'ERROR:'.
    """
    try:
        texto = transcribir_archivo(ruta_audio, model_name=model_name)
        queue.put(texto)
    except Exception as e:
        queue.put(f"ERROR: {e}")