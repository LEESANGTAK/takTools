@echo off
setlocal enabledelayedexpansion

set curDir=%~dp0
set userStartDir="%userprofile%\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup"
set genBatchFileName=create_virtualDrive
set ext=.bat
set batchFile=
set configFile=%curDir%config_virtualDrive.ini
set driveKey=drive
set driveVal="-1"

:: gets the drive char from config file
for /f "usebackq delims=" %%i in ("!configFile!") do (
    set ln=%%i
    for /f "tokens=1,2 delims==" %%a in ("!ln!") do (
        set curKey=%%a
        set curVal=%%b
        if "x!driveKey!"=="x!curKey!" (
            set driveVal=!curVal!
            goto :main
        )
    )
)

:: VirtualDrive settings
:main
if "!driveVal!"=="-1" (
    echo ERROR : not defined the project driver in config file...
) else (
    echo This project drive : !driveVal!
    set batchFile=%genBatchFileName%_%driveVal%%ext%
    echo !batchFile!

    pushd %userStartDir%
    :: Deleting an existing batch file
    del /F /Q /A "!batchFile!" 2>nul
    del "info*" 2>nul

    :: Remove virtual drives
    subst !driveVal!: /d >nul
)

pause
