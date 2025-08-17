import os
import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
from tkinter import ttk
from transcriptor import _worker_transcribir
import multiprocessing as mp  # proceso separado para poder cancelar

class TranscriptorGUI:
    def __init__(self):
        self.ventana = tk.Tk()
        self.ventana.title("TranscriptoApp - Transcriptor Offline")
        self.ventana.geometry("700x520")

        # Estado del trabajo en proceso/cancelación
        self.proc = None
        self.queue = None

        # 1) Lista desplegable de modelos
        modelos = ["tiny", "base", "small", "medium", "large"]
        self.modelo_var = tk.StringVar(value="base")
        frame_modelo = tk.Frame(self.ventana)
        frame_modelo.pack(pady=(10, 0))
        tk.Label(frame_modelo, text="Modelo Whisper:").grid(row=0, column=0, padx=(0, 6))
        self.combo_modelo = ttk.Combobox(frame_modelo, textvariable=self.modelo_var, values=modelos, state="readonly", width=12)
        self.combo_modelo.grid(row=0, column=1)

        # Botones principales
        frame_top = tk.Frame(self.ventana)
        frame_top.pack(pady=10)
        self.btn_cargar = tk.Button(frame_top, text="Abrir audio y transcribir", command=self.transcribir_audio)
        self.btn_cargar.grid(row=0, column=0, padx=5)
        self.btn_cancelar = tk.Button(frame_top, text="Cancelar", state="disabled", command=self.cancelar)
        self.btn_cancelar.grid(row=0, column=1, padx=5)

        # 2) Label con el nombre del archivo seleccionado
        self.lbl_archivo = tk.Label(self.ventana, text="Ningún archivo seleccionado", anchor="w")
        self.lbl_archivo.pack(fill="x", padx=10)

        # 3) Label de estado
        self.lbl_estado = tk.Label(self.ventana, text="Listo.", anchor="w", fg="#555")
        self.lbl_estado.pack(fill="x", padx=10, pady=(0, 4))

        # Barra de progreso (indeterminada)
        self.progress = ttk.Progressbar(self.ventana, mode="indeterminate")
        self.progress.pack(fill="x", padx=10)
        self.progress.stop()
        self.progress.pack_forget()  # oculta inicialmente

        # Área de texto
        self.text_area = scrolledtext.ScrolledText(self.ventana, wrap=tk.WORD, width=80, height=18)
        self.text_area.pack(padx=10, pady=10, fill="both", expand=True)

        # Botones copiar/guardar
        self.frame_botones = tk.Frame(self.ventana)
        self.frame_botones.pack(pady=(0, 10))

        self.btn_copiar = tk.Button(self.frame_botones, text="Copiar", command=self.copiar_texto)
        self.btn_copiar.grid(row=0, column=0, padx=5)

        self.btn_guardar = tk.Button(self.frame_botones, text="Guardar", command=self.guardar_texto)
        self.btn_guardar.grid(row=0, column=1, padx=5)

    # -------- utilidades GUI --------
    def _set_estado(self, texto, color="#555"):
        self.lbl_estado.config(text=texto, fg=color)
        self.ventana.update_idletasks()

    def _mostrar_progreso(self, mostrar=True):
        if mostrar:
            self.progress.pack(fill="x", padx=10)
            self.progress.start(10)  # velocidad de la marquesina
        else:
            self.progress.stop()
            self.progress.pack_forget()

    # -------- acciones --------
    def transcribir_audio(self):
        archivo = filedialog.askopenfilename(filetypes=[("Archivos de audio", "*.mp3 *.wav *.m4a *.flac *.ogg *.m4b *.mp4 *.aac")])
        if not archivo:
            return

        self.lbl_archivo.config(text=os.path.basename(archivo))
        self._set_estado("Preparando transcripción…", "#0066cc")

        # Deshabilitar/activar botones
        self.btn_cargar.config(state="disabled")
        self.btn_cancelar.config(state="normal")
        self._mostrar_progreso(True)

        modelo = self.modelo_var.get()

        # Crear proceso y cola para recibir el resultado
        self.queue = mp.Queue()
        self.proc = mp.Process(target=_worker_transcribir, args=(archivo, modelo, self.queue))
        self.proc.start()
        # empezar a revisar periódicamente si hay resultado
        self.ventana.after(200, self._revisar_resultado)

    def _revisar_resultado(self):
        if self.queue is None:
            return
        try:
            texto = self.queue.get_nowait()
        except Exception:
            # Si el proceso sigue vivo, seguimos esperando
            if self.proc is not None and self.proc.is_alive():
                self._set_estado("Transcribiendo… esto puede tardar dependiendo del tamaño del audio.", "#0066cc")
                self.ventana.after(400, self._revisar_resultado)
                return
            else:
                # Sin texto y proceso muerto (raro): algo falló
                self._finalizar_trabajo("ERROR: El proceso terminó sin devolver resultado.")
                return

        # Llegó resultado
        if isinstance(texto, str) and texto.startswith("ERROR:"):
            self._finalizar_trabajo(texto, es_error=True)
        else:
            self._finalizar_trabajo(texto)

    def _finalizar_trabajo(self, texto, es_error=False, cancelado=False):
        # Limpiar proceso/cola
        if self.proc is not None:
            if self.proc.is_alive():
                self.proc.join(timeout=0.1)
            self.proc = None
        self.queue = None

        # Mostrar texto (si no fue cancelado)
        self.text_area.delete("1.0", tk.END)
        if cancelado:
            self.text_area.insert(tk.END, "")
        else:
            self.text_area.insert(tk.END, texto)

        # Estado final + UI
        if cancelado:
            self._set_estado("Transcripción cancelada por el usuario.", "#cc7a00")
        elif es_error:
            self._set_estado("Ocurrió un problema al transcribir. Revisa el archivo o el modelo.", "#cc0000")
        else:
            self._set_estado("¡Listo! Transcripción terminada.", "#117733")

        # ✅ Desactivar siempre “Cancelar” cuando ya hay un resultado
        self.btn_cancelar.config(state="disabled")

        self._mostrar_progreso(False)
        self.btn_cargar.config(state="normal")

    def cancelar(self):
        # Termina el proceso y marca como cancelado
        if self.proc is not None and self.proc.is_alive():
            try:
                self.proc.terminate()
            except Exception:
                pass
        self._finalizar_trabajo("", cancelado=True)

    def copiar_texto(self):
        self.ventana.clipboard_clear()
        self.ventana.clipboard_append(self.text_area.get("1.0", tk.END))
        self.ventana.update()
        messagebox.showinfo("Copiado", "Texto copiado al portapapeles")

    def guardar_texto(self):
        archivo_guardar = filedialog.asksaveasfilename(defaultextension=".txt",
                                                       filetypes=[("Archivo de texto", "*.txt")])
        if archivo_guardar:
            with open(archivo_guardar, "w", encoding="utf-8") as f:
                f.write(self.text_area.get("1.0", tk.END))
            messagebox.showinfo("Guardado", "Transcripción guardada con éxito")

    def run(self):
        self.ventana.mainloop()
