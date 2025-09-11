#-
# ===========================================================================
# Copyright 2024 Autodesk, Inc. All rights reserved.
#
# Use of this software is subject to the terms of the Autodesk license
# agreement provided at the time of installation or download, or which
# otherwise accompanies this software in either electronic or hard copy form.
# ===========================================================================
#+

include_guard( DIRECTORY )

# BIFROST_WARNINGS_AS_ERRORS is optional and can be passed as environment variable or CMake variable.
# BIFROST_WARNINGS_AS_ERRORS=ON|OFF
if( NOT BIFROST_WARNINGS_AS_ERRORS )
    if( DEFINED ENV{BIFROST_WARNINGS_AS_ERRORS} )
        set( BIFROST_WARNINGS_AS_ERRORS $ENV{BIFROST_WARNINGS_AS_ERRORS})
    endif()
endif()

if( NOT BIFROST_WARNINGS_AS_ERRORS )
   return()
endif()

message( STATUS "Bifrost: BIFROST_WARNINGS_AS_ERRORS is set to ${BIFROST_WARNINGS_AS_ERRORS}" )
# Set warnings as errors
function( bifrost_set_warnings_as_errors )
    # Enable warnings as errors based on CMake compiler IDs
    if( CMAKE_CXX_COMPILER_ID MATCHES "Clang" )
        set( flags  "-Werror -Wall -Wextra -Wpedantic -Wfloat-equal -Wconversion -Wshadow -Wno-c++98-compat -Wno-c++98-compat-pedantic -Wno-padded -Wno-exit-time-destructors -Wno-global-constructors -Wno-weak-vtables" )
    elseif( CMAKE_CXX_COMPILER_ID STREQUAL "GNU" )
        set( flags  "-Werror -Wall -Wextra -Wpedantic -Wfloat-equal -Wconversion -Wshadow -Wno-comment" )
    elseif( CMAKE_CXX_COMPILER_ID STREQUAL "MSVC" )
        set( flags  "/EHsc /W4 /WX /wd4251 /wd4324" )
    else()
        message( WARNING "Bifrost: No warnings as errors set. Unsupported compiler: `${CMAKE_CXX_COMPILER_ID}`" )
    endif()

    if( flags )
        set( CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${flags}" PARENT_SCOPE )
        message( STATUS "Bifrost: Warnings as errors added flags to CMAKE_CXX_FLAGS: ${flags}")
    endif()
endfunction()

bifrost_set_warnings_as_errors()
