@echo off
title Cockpit Operacional - WIN/WDO
color 0B
echo ========================================================
echo    INICIANDO O SERVIDOR DO COCKPIT OPERACIONAL...
echo ========================================================
echo.

:: Inicia o navegador com o endereço do sistema em segundo plano
start http://127.0.0.1:8000/index.html

:: Inicia o Uvicorn na pasta raiz do projeto
python -m uvicorn api_backend.main:app --reload

pause