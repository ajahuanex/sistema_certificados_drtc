@echo off
echo ========================================
echo PRUEBA DE CONFIGURACION DE CACHE
echo ========================================
echo.

echo Probando configuracion con USE_REDIS=False...
python test-cache-config.py

echo.
echo ========================================
echo PRUEBA COMPLETADA
echo ========================================
pause