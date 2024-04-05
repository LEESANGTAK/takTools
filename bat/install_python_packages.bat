@echo off

set /p mayaVersion=Maya Version?:
set mayapyPath="%ProgramFiles%\Autodesk\Maya%mayaVersion%\bin"

cd %mayapyPath%
mayapy -m pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org pymel
mayapy -m pip install numpy
mayapy -m pip install scipy

pause
