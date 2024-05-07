@echo off
:: When delayed expansion is enabled, variables are expanded at execution time rather than at parse time. This can be useful in situations where you need to access variables within loops or blocks of code that change during execution.
setlocal enabledelayedexpansion

:: Set a directory path of the current file to the variable `curDir`
set curDir=%~dp0
set trgDir=
set userStartDir="%userprofile%\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup"
set genBatchFileName=create_virtualDrive
set ext=.bat
set batchFile=
set configFile=%curDir%config_virtualDrive.ini
set driveKey=drive
set driveVal="-1"

for /f "usebackq delims=" %%i in ("!configFile!") do (
    set line=%%i
    for /f "tokens=1,2 delims==" %%a in ("!line!") do (
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
    cd ..
    set trgDir=!CD!
    echo !trgDir!
    pushd %userStartDir%

    del /F /Q /A "!batchFile!" 2>nul
    del "info*" 2>nul

    :: Create a new batch file
    echo subst !driveVal!: !trgDir!>>!batchFile!
    echo exit>>!trgDir!>>!batchFile!

    :: Run the batch file to create a virtual drive
    start !batchFile!
)

pause
