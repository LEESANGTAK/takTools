cmake_minimum_required(VERSION 3.0)

include($ENV{DEVKIT_LOCATION}/cmake/pluginEntry.cmake)
include_directories($ENV{EXTERN_INCLUDES})

set(PROJECT_NAME $ENV{PLUGIN_NAME})
project(${PROJECT_NAME})

set(RESOURCES_FILES

)

set(MEL_FILES

)

set(SOURCE_FILES
    pluginMain.cpp
    takCurveCollision.h
    takCurveCollision.cpp
    ${MEL_FILES}
)

set(LIBRARIES
    Foundation
    OpenMaya
    OpenMayaAnim
    OpenMayaFX
    OpenMayaRender
    OpenMayaUI
)

build_plugin()
