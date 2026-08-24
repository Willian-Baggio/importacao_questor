@echo off
setlocal

cd /d "%~dp0"

echo Iniciando importacao Sittax para Questor...
echo Diretorio: %cd%
echo.

python -m src.app

set RESULT=%errorlevel%

echo.
if %RESULT% neq 0 echo O script terminou com erro - codigo %RESULT%.
if %RESULT% equ 0 echo Execucao finalizada.
echo Log em: %cd%\log\automacao importacao para o questor.log

echo.
pause
