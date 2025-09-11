#-
#*****************************************************************************
# Copyright 2024 Autodesk, Inc. All rights reserved.
#
# Use of this software is subject to the terms of the Autodesk license
# agreement provided at the time of installation or download, or which
# otherwise accompanies this software in either electronic or hard copy form.
#*****************************************************************************
#+
include_guard( DIRECTORY )

# Standard printing facilities
include(CMakePrintHelpers)

# Where does the install go
# Set only if setup.cmake is included from the top CMake directory
if( CMAKE_SOURCE_DIR STREQUAL PROJECT_SOURCE_DIR )
    if( CMAKE_INSTALL_PREFIX_INITIALIZED_TO_DEFAULT )
        set(CMAKE_INSTALL_PREFIX "${CMAKE_BINARY_DIR}/${PROJECT_NAME}-${PROJECT_VERSION}" CACHE PATH   "install path" FORCE)
    elseif(NOT CMAKE_INSTALL_PREFIX MATCHES "/${PROJECT_NAME}-${PROJECT_VERSION}$")
        set(CMAKE_INSTALL_PREFIX "${CMAKE_INSTALL_PREFIX}/${PROJECT_NAME}-${PROJECT_VERSION}" CACHE PATH  "install path" FORCE)
    endif()
endif()

# Bifrost baseline C++ is C++17
if( NOT CMAKE_CXX_STANDARD )
    set( CMAKE_CXX_STANDARD 17 )
elseif( CMAKE_CXX_STANDARD LESS 17 )
    message( FATAL_ERROR "Bifrost: CMAKE_CXX_STANDARD must be 17 and up.")
endif()

# Finding Bifrost modules...
# Note: The CMAKE_MODULE_PATH may end-up being passed to other "tools" that
# interpret the "\" as the escape character. A normalized path is appended
# to CMAKE_MODULE_PATH to avoid this issue.
file(TO_CMAKE_PATH "${BIFROST_LOCATION}" normalized_bifrost_location)
list(APPEND CMAKE_MODULE_PATH "${normalized_bifrost_location}/sdk/cmake")

# Main settings feedback
cmake_print_variables( BIFROST_LOCATION )
cmake_print_variables( CMAKE_INSTALL_PREFIX )
cmake_print_variables( CMAKE_CXX_STANDARD )

# Load Bifrost utilities
include( ${BIFROST_LOCATION}/sdk/cmake/utils.cmake )

# Controlled by BIFROST_WARNINGS_AS_ERRORS CMake or environment variable.
# BIFROST_WARNINGS_AS_ERRORS is inactive by default.
include( ${BIFROST_LOCATION}/sdk/cmake/bifrost_warnings_as_errors.cmake)

if( CMAKE_CXX_COMPILER_ID STREQUAL "MSVC" )
    # The /Zc:__cplusplus compiler option enables the __cplusplus preprocessor macro
    # to report an updated value for recent C++ language standards support. By
    # default, Visual Studio always returns the value 199711L for the __cplusplus
    # preprocessor macro.
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /Zc:__cplusplus")
endif()
