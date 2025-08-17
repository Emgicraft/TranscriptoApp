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
echo === Instalar requirements ===
%PY% -m pip install --upgrade pip || (
  echo [ERROR] No se pudo actualizar pip.
  exit /b 1
)
%PY% -m pip install -r requirements.txt || (
  echo [ERROR] No se pudieron instalar los paquetes de requirements.txt
  exit /b 1
)

echo.
echo === Descargar y preparar ffmpeg ===
call :download_ffmpeg || exit /b 1

echo.
echo [OK] Requerimientos instalados y ffmpeg listo.
exit /b 0


:download_ffmpeg
mkdir "vendor\ffmpeg\bin" 2>nul

echo Descargando ffmpeg...
powershell -NoLogo -NoProfile -Command ^
 "try { Invoke-WebRequest -Uri '%FF_URL%' -OutFile '%FF_ZIP%' -UseBasicParsing } catch { Write-Error $_ ; exit 2 }"
if errorlevel 1 (
  echo [ERROR] No se pudo descargar ffmpeg.
  exit /b 1
)

echo Extrayendo ffmpeg...
rmdir /s /q "%FF_TMP%" 2>nul
powershell -NoLogo -NoProfile -Command ^
 "Expand-Archive -LiteralPath '%FF_ZIP%' -DestinationPath '%FF_TMP%' -Force" || (
  echo [ERROR] No se pudo extraer el ZIP de ffmpeg.
  exit /b 1
)

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

copy /Y "%FF_DIR%\bin\ffmpeg.exe" "vendor\ffmpeg\bin\" >nul || (
  echo [ERROR] No se pudo copiar ffmpeg.exe
  exit /b 1
)
copy /Y "%FF_DIR%\bin\ffprobe.exe" "vendor\ffmpeg\bin\" >nul || (
  echo [ERROR] No se pudo copiar ffprobe.exe
  exit /b 1
)

rmdir /s /q "%FF_TMP%" 2>nul
del /q "%FF_ZIP%" 2>nul

echo ffmpeg listo en vendor\ffmpeg\bin
exit /b 0
