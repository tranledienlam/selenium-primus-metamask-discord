@echo off
cd /d %~dp0

set VENV_PATH=G:\venv_selenium\Scripts\python.exe
REM Kiểm tra Python trong môi trường ảo
if exist "%VENV_PATH%" (
    set PYTHON_PATH=%VENV_PATH%
) else (
    REM Kiểm tra Python hệ thống
    where python >nul 2>nul
    if %ERRORLEVEL% equ 0 (
        set PYTHON_PATH=python
    ) else (
        echo Python không được tìm thấy trong hệ thống!
        echo Vui lòng cài đặt Python hoặc kiểm tra lại đường dẫn môi trường ảo.
        pause
        exit /b 1
    )
)

REM Chạy script Python với tham số nếu có
"%PYTHON_PATH%" index.py %*