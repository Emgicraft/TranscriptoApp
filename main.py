from gui import TranscriptorGUI

if __name__ == "__main__":
    import multiprocessing as mp
    mp.freeze_support()  # 👈 muy importante en ejecutables PyInstaller/Windows
    app = TranscriptorGUI()
    app.run()
