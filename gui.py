import os
import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
from tkinter import ttk
from transcriptor import transcribir_archivo

import threading

class TranscriptorGUI:
    def __init__(self):
        self.ventana = tk.Tk()
        self.ventana.title("TranscriptoApp - Transcriptor Offline")
        self.ventana.geometry("680x520")

        # Lista desplegable de modelos
        modelos = ["tiny", "base", "small", "medium", "large"]
        self.modelo_var = tk.StringVar(value="base")  # por defecto: el actual
        frame_modelo = tk.Frame(self.ventana)
        frame_modelo.pack(pady=(10, 0))
        tk.Label(frame_modelo, text="Modelo Whisper:").grid(row=0, column=0, padx=(0, 6))
        self.combo_modelo = ttk.Combobox(frame_modelo, textvariable=self.modelo_var, values=modelos, state="readonly", width=12)
        self.combo_modelo.grid(row=0, column=1)

        # Botón principal
        self.btn_cargar = tk.Button(self.ventana, text="Abrir audio y transcribir", command=self.transcribir_audio)
        self.btn_cargar.pack(pady=10)

        # Label con el nombre del archivo seleccionado
        self.lbl_archivo = tk.Label(self.ventana, text="Ningún archivo seleccionado", anchor="w")
        self.lbl_archivo.pack(fill="x", padx=10)

        # Label de estado
        self.lbl_estado = tk.Label(self.ventana, text="Listo.", anchor="w", fg="#555")
        self.lbl_estado.pack(fill="x", padx=10, pady=(0, 8))

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

    def _set_estado(self, texto, color="#555"):
        self.lbl_estado.config(text=texto, fg=color)
        self.ventana.update_idletasks()

    def transcribir_audio(self):
        archivo = filedialog.askopenfilename(filetypes=[("Archivos de audio", "*.mp3 *.wav *.m4a *.flac *.ogg *.m4b *.mp4 *.aac")])
        if not archivo:
            return

        # Mostrar nombre de archivo
        self.lbl_archivo.config(text=os.path.basename(archivo))

        # Mensajes de estado y deshabilitar botón mientras procesa
        self._set_estado("Procesando transcripción… esto puede tardar unos minutos.", "#0066cc")
        self.btn_cargar.config(state="disabled")

        modelo = self.modelo_var.get()

        # Evitar congelar la UI: procesa en hilo aparte
        def _worker():
            try:
                texto = transcribir_archivo(archivo, model_name=modelo)
            except Exception as e:
                texto = f"Error en la transcripción: {e}"

            # Volver al hilo de la GUI
            def _finalizar():
                self.text_area.delete("1.0", tk.END)
                self.text_area.insert(tk.END, texto)
                # Mensaje final
                if texto.startswith("Error"):
                    self._set_estado("Ocurrió un problema al transcribir. Revisa el archivo o el modelo.", "#cc0000")
                else:
                    self._set_estado("¡Listo! Transcripción terminada.", "#117733")
                self.btn_cargar.config(state="normal")

            self.ventana.after(0, _finalizar)

        threading.Thread(target=_worker, daemon=True).start()

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
