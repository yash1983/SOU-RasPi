@echo off
echo 🚀 SOU Raspberry Pi Deployment Script
echo =====================================

set PI_IP=192.168.8.56
set PI_USER=yashr
set REMOTE_PATH=/home/yashr/SOU-RasPi

echo Testing connection to %PI_IP%...
ping -n 1 %PI_IP% >nul 2>&1
if errorlevel 1 (
    echo ❌ Cannot reach Raspberry Pi at %PI_IP%
    echo Please check:
    echo   - Pi is powered on and connected to WiFi
    echo   - IP address is correct
    echo   - Both devices are on the same network
    pause
    exit /b 1
)

echo ✅ Connection successful!

echo.
echo Choose deployment method:
echo 1. SCP (requires SSH key setup)
echo 2. Manual instructions
echo 3. Exit
echo.
set /p choice="Enter your choice (1-3): "

if "%choice%"=="1" goto scp_deploy
if "%choice%"=="2" goto manual_instructions
if "%choice%"=="3" goto end
goto invalid_choice

:scp_deploy
echo.
echo Using SCP method...
echo Note: This requires SSH key authentication to be set up first.
echo.

echo Creating remote directory...
ssh %PI_USER%@%PI_IP% "mkdir -p %REMOTE_PATH%"

if errorlevel 1 (
    echo ❌ SSH connection failed. Please set up SSH keys first.
    echo See deploy_manual.md for instructions.
    pause
    exit /b 1
)

echo Copying files...
scp -r ./* %PI_USER%@%PI_IP%:%REMOTE_PATH%/

if errorlevel 1 (
    echo ❌ File copy failed.
    pause
    exit /b 1
)

echo ✅ Deployment successful!
goto post_deploy

:manual_instructions
echo.
echo 📋 Manual Deployment Instructions:
echo =================================
echo.
echo 1. Set up SSH keys (see deploy_manual.md)
echo 2. Copy files manually using one of these methods:
echo    - SCP: scp -r ./* yashr@192.168.8.56:/home/yashr/SOU-RasPi/
echo    - Git: Clone repository on Pi
echo    - USB: Copy files to USB drive and transfer
echo.
echo 3. SSH into Pi and run setup:
echo    ssh yashr@192.168.8.56
echo    cd /home/yashr/SOU-RasPi
echo    pip3 install -r requirements.txt
echo    sudo apt-get install python3-opencv libzbar0
echo.
goto end

:post_deploy
echo.
echo 🎉 Deployment complete!
echo.
echo Next steps:
echo 1. SSH into your Pi: ssh %PI_USER%@%PI_IP%
echo 2. Navigate to project: cd %REMOTE_PATH%
echo 3. Install dependencies: pip3 install -r requirements.txt
echo 4. Install system packages: sudo apt-get install python3-opencv libzbar0
echo 5. Test system: python3 test_attractions.py
echo 6. Run attraction: python3 AttractionA.py
echo.
goto end

:invalid_choice
echo ❌ Invalid choice. Please enter 1, 2, or 3.
pause
goto end

:end
echo.
echo Press any key to exit...
pause >nul
