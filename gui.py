import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
from transcriptor import transcribir_archivo

class TranscriptorGUI:
    def __init__(self):
        self.ventana = tk.Tk()
        self.ventana.title("TranscriptoApp - Transcriptor Offline")
        self.ventana.geometry("600x400")

        self.btn_cargar = tk.Button(self.ventana, text="Abrir audio y transcribir", command=self.transcribir_audio)
        self.btn_cargar.pack(pady=10)

        self.text_area = scrolledtext.ScrolledText(self.ventana, wrap=tk.WORD, width=70, height=15)
        self.text_area.pack(padx=10, pady=10)

        self.frame_botones = tk.Frame(self.ventana)
        self.frame_botones.pack()

        self.btn_copiar = tk.Button(self.frame_botones, text="Copiar", command=self.copiar_texto)
        self.btn_copiar.grid(row=0, column=0, padx=5)

        self.btn_guardar = tk.Button(self.frame_botones, text="Guardar", command=self.guardar_texto)
        self.btn_guardar.grid(row=0, column=1, padx=5)

    def transcribir_audio(self):
        archivo = filedialog.askopenfilename(filetypes=[("Archivos de audio", "*.mp3 *.wav *.m4a")])
        if archivo:
            texto = transcribir_archivo(archivo)
            self.text_area.delete("1.0", tk.END)
            self.text_area.insert(tk.END, texto)

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
