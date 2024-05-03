@echo off

REM set MayaVersion=2024
set mayapyPath="%ProgramFiles%\Autodesk\Maya%MayaVersion%\bin\mayapy.exe"

%mayapyPath% -m pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org pymel
%mayapyPath% -m pip install numpy
%mayapyPath% -m pip install scipy
%mayapyPath% -m pip install stability-sdk

REM pause