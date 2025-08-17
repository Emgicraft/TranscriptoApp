import whisper

# Carga el modelo solo una vez al inicio
modelo = whisper.load_model("base")  # tiny, base, small, medium, large

def transcribir_archivo(ruta_audio: str) -> str:
    """
    Transcribe un archivo de audio usando Whisper local.
    :param ruta_audio: Ruta al archivo de audio (mp3, wav, m4a, etc.)
    :return: Texto transcrito
    """
    try:
        resultado = modelo.transcribe(ruta_audio)
        return resultado["text"]
    except Exception as e:
        return f"Error en la transcripción: {e}"
