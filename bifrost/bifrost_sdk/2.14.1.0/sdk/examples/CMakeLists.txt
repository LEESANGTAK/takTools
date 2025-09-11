#-
# ===========================================================================
# Copyright 2024 Autodesk, Inc. All rights reserved.
#
# Use of this software is subject to the terms of the Autodesk license
# agreement provided at the time of installation or download, or which
# otherwise accompanies this software in either electronic or hard copy form.
# ===========================================================================
#+

cmake_minimum_required(VERSION 3.20)

# BIFROST_LOCATION must be passed-in or defined by an environment variable.
# Passed-in on the CMake command line overrides the environemnt variable.
if( NOT BIFROST_LOCATION )
    if( DEFINED ENV{BIFROST_LOCATION} )
        set( BIFROST_LOCATION $ENV{BIFROST_LOCATION})
    else()
        message( FATAL_ERROR "Bifrost: BIFROST_LOCATION cmake variable must be defined.")
    endif()
endif()

# Project Name
project(
    BifrostExamples
    VERSION 1.0.0
    LANGUAGES CXX
)

# Bifrost setup and utilities...
include(${BIFROST_LOCATION}/sdk/cmake/setup.cmake)

# Fetch Bifrost SDK
find_package(Bifrost REQUIRED SDK)
# Testing
enable_testing()

# Add all examples sub dir
add_subdirectory(AminoConcepts)
add_subdirectory(Complex)
add_subdirectory(ExecutorBasics)
add_subdirectory(ExecutorCustomObject)
add_subdirectory(ExecutorWatchpoint)
add_subdirectory(HSV)
add_subdirectory(IndexSet)
add_subdirectory(MeshArea)
add_subdirectory(MeshWeldUV)
add_subdirectory(ObjWriter)
add_subdirectory(SimpleAssociative)
add_subdirectory(SimpleNUBSCurve)
add_subdirectory(SimpleString)
add_subdirectory(TwistDeformer)
add_subdirectory(VectorLength)
