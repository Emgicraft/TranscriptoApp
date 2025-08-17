import whisper

# Caché de modelos para no recargar si el usuario cambia de modelo
_model_cache = {}

def get_model(model_name: str = "base"):
    """
    Obtiene (y cachea) un modelo Whisper por nombre.
    """
    global _model_cache
    if model_name not in _model_cache:
        _model_cache[model_name] = whisper.load_model(model_name)
    return _model_cache[model_name]

def transcribir_archivo(ruta_audio: str, model_name: str = "base") -> str:
    """
    Transcribe un archivo de audio usando Whisper local.
    :param ruta_audio: Ruta al archivo de audio (mp3, wav, m4a, etc.)
    :param model_name: Modelo whisper a usar (tiny, base, small, medium, large)
    :return: Texto transcrito (limpio al inicio y al final)
    """
    try:
        modelo = get_model(model_name)
        resultado = modelo.transcribe(ruta_audio)
        texto = resultado.get("text", "")
        # Limpieza: quita espacios/saltos al inicio y fin
        return (texto or "").strip()
    except Exception as e:
        return f"Error en la transcripción: {e}"
