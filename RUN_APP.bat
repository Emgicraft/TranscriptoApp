@echo off
setlocal
REM Ejecuta TranscriptoApp desde el código fuente

REM Ir a la carpeta del script
cd /d "%~dp0"

REM 1) Elegir intérprete: entorno local (sin consola) > py > python
set "PYEXE="
if exist "env\Scripts\pythonw.exe" set "PYEXE=env\Scripts\pythonw.exe"
if not defined PYEXE if exist "env\Scripts\python.exe" set "PYEXE=env\Scripts\python.exe"
if not defined PYEXE where py >nul 2>&1 && set "PYEXE=py"
if not defined PYEXE where python >nul 2>&1 && set "PYEXE=python"

if not defined PYEXE (
  echo [ERROR] No se encontro Python. Ejecuta primero setup_env.bat
  pause
  exit /b 1
)

REM 2) Aviso si falta ffmpeg
if not exist "vendor\ffmpeg\bin\ffmpeg.exe" (
  echo [ADVERTENCIA] No se encontro vendor\ffmpeg\bin\ffmpeg.exe
  echo Ejecuta ^"setup_env.bat^" o ^"install_requirements.bat^" para descargar ffmpeg.
)

REM 3) Ejecutar la app
echo Iniciando TranscriptoApp...
if /i "%PYEXE%"=="py" (
  REM Intentar modo windowed; si no, modo normal
  %PYEXE% -3w main.py 2>nul || %PYEXE% -3 main.py
) else (
  "%PYEXE%" main.py
)

endlocal
