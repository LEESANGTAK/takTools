@echo %off

rem ---------------------------------------------------------------------------------------
rem Settings
rem ---------------------------------------------------------------------------------------
set MAYA_VERSION=2020
set PLUGIN_NAME=takCollision
rem Use forward slash(/)
set DEVKIT_LOCATION=C:/GoogleDrive/programs_env/maya/library/devkit/2020.4
set EXTERN_INCLUDES=
rem Use backward slash(\)
set MODULE_DIR_PATH=C:\GoogleDrive\programs_env\maya\modules\takTools
rem ---------------------------------------------------------------------------------------


rem Unload plugin before build
python unloadPlugin.py -pn %PLUGIN_NAME% -ns true


rem Create project if not exists
if not exist .\build\%MAYA_VERSION% cmake -H. -B build\%MAYA_VERSION% -G "Visual Studio 16 2019"

rem Build
cmake --build build\%MAYA_VERSION% --config Release


rem Make plug-ins and scripts directory if not exists in module directory
if not exist %MODULE_DIR_PATH%\plug-ins\%MAYA_VERSION% md %MODULE_DIR_PATH%\plug-ins\%MAYA_VERSION%
if not exist %MODULE_DIR_PATH%\scripts md %MODULE_DIR_PATH%\scripts

rem Copy .mll and .mel files to the module directory
for /R .\build\%MAYA_VERSION%\Release\ %%f in (*.mll) do copy "%%f" %MODULE_DIR_PATH%\plug-ins\%MAYA_VERSION%
for /R .\ %%f in (*.mel) do copy "%%f" %MODULE_DIR_PATH%\scripts


rem Load plugin after build
python loadPlugin.py -pn %MODULE_DIR_PATH%\plug-ins\%MAYA_VERSION%\%PLUGIN_NAME% -ts "C:\Users\chst27\Desktop\strap\strap_fxDeformer_001.ma"

echo "Build completed!"
pause
