@echo off
setlocal

REM ===== Config =====
set "FF_URL=https://github.com/GyanD/codexffmpeg/releases/download/2025-08-14-git-cdbb5f1b93/ffmpeg-2025-08-14-git-cdbb5f1b93-essentials_build.zip"
set "FF_ZIP=ffmpeg.zip"
set "FF_TMP=_ffmpeg_tmp"

REM ===== Detectar Python (py launcher o python) =====
set "PY="
where py >nul 2>&1 && set "PY=py"
if not defined PY where python >nul 2>&1 && set "PY=python"
if not defined PY (
  echo [ERROR] No se encontro Python. Instala Python 3.8+ y vuelve a intentar.
  exit /b 1
)

echo.
echo === 1) Crear entorno virtual: env ===
%PY% -m venv env || (
  echo [ERROR] No se pudo crear el entorno virtual.
  exit /b 1
)

echo Activando entorno...
call "env\Scripts\activate.bat" || (
  echo [ERROR] No se pudo activar el entorno virtual.
  exit /b 1
)

echo.
echo === 2) Actualizar pip e instalar requirements ===
python -m pip install --upgrade pip || (
  echo [ERROR] No se pudo actualizar pip.
  exit /b 1
)
pip install -r requirements.txt || (
  echo [ERROR] No se pudieron instalar los paquetes de requirements.txt
  exit /b 1
)

echo.
echo === 3) Descargar y preparar ffmpeg ===
call :download_ffmpeg || exit /b 1

echo.
echo [OK] Entorno listo. Para usarlo: 
echo     call env\Scripts\activate
echo.
exit /b 0


:download_ffmpeg
REM Crear carpetas destino
mkdir "vendor\ffmpeg\bin" 2>nul

REM Descargar ZIP
echo Descargando ffmpeg...
powershell -NoLogo -NoProfile -Command ^
 "try { Invoke-WebRequest -Uri '%FF_URL%' -OutFile '%FF_ZIP%' -UseBasicParsing } catch { Write-Error $_ ; exit 2 }"
if errorlevel 1 (
  echo [ERROR] No se pudo descargar ffmpeg.
  exit /b 1
)

REM Extraer ZIP
echo Extrayendo ffmpeg...
rmdir /s /q "%FF_TMP%" 2>nul
powershell -NoLogo -NoProfile -Command ^
 "Expand-Archive -LiteralPath '%FF_ZIP%' -DestinationPath '%FF_TMP%' -Force" || (
  echo [ERROR] No se pudo extraer el ZIP de ffmpeg.
  exit /b 1
)

REM Detectar carpeta extraida (ffmpeg-*-essentials_build)
set "FF_DIR="
for /d %%D in ("%FF_TMP%\ffmpeg-*") do (
  set "FF_DIR=%%~fD"
  goto :found_dir
)
:found_dir
if not defined FF_DIR (
  echo [ERROR] No se encontro la carpeta extraida de ffmpeg.
  exit /b 1
)

REM Copiar binarios necesarios
copy /Y "%FF_DIR%\bin\ffmpeg.exe" "vendor\ffmpeg\bin\" >nul || (
  echo [ERROR] No se pudo copiar ffmpeg.exe
  exit /b 1
)
copy /Y "%FF_DIR%\bin\ffprobe.exe" "vendor\ffmpeg\bin\" >nul || (
  echo [ERROR] No se pudo copiar ffprobe.exe
  exit /b 1
)

REM Limpieza
rmdir /s /q "%FF_TMP%" 2>nul
del /q "%FF_ZIP%" 2>nul

echo ffmpeg listo en vendor\ffmpeg\bin
exit /b 0
