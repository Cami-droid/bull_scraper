@echo off
set LOGFILE=registro_ejecuciones.log

llegar

echo Iniciando el proceso de amanecer... >> %LOGFILE%
echo Fecha: %date% Hora: %time% >> %LOGFILE%

REM --- Ejecutando scripts de Python ---

echo. >> %LOGFILE%
echo Ejecutando dashboard_to_excel.py... >> %LOGFILE%
python dashboard_to_excel.py
if %errorlevel% neq 0 (
    echo ¡Error! dashboard_to_excel.py falló con codigo %errorlevel%. >> %LOGFILE%
    goto :fin
)

echo. >> %LOGFILE%
echo Ejecutando cauciones_to_excel.py... >> %LOGFILE%
python cauciones_to_excel.py
if %errorlevel% neq 0 (
    echo ¡Error! cauciones_to_excel.py falló con codigo %errorlevel%. >> %LOGFILE%
    goto :fin
)

echo. >> %LOGFILE%
echo Ejecutando main.py... >> %LOGFILE%
python main.py
if %errorlevel% neq 0 (
    echo ¡Error! main.py falló con codigo %errorlevel%. >> %LOGFILE%
    goto :fin
)

echo. >> %LOGFILE%
echo Ejecutando h5_to_excel.py... >> %LOGFILE%
python h5_to_excel.py
if %errorlevel% neq 0 (
    echo ¡Error! h5_to_excel.py falló con codigo %errorlevel%. >> %LOGFILE%
    goto :fin
)

:fin
echo. >> %LOGFILE%
echo Proceso de amanecer finalizado exitosamente. >> %LOGFILE%
echo ------------------------------------------------ >> %LOGFILE%