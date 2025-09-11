#-
# ===========================================================================
# Copyright 2024 Autodesk, Inc. All rights reserved.
#
# Use of this software is subject to the terms of the Autodesk license
# agreement provided at the time of installation or download, or which
# otherwise accompanies this software in either electronic or hard copy form.
# ===========================================================================
#+

# Follows the conventions of FindGTest.cmake module by checking
# GTest_FOUND and GTEST_ROOT.
#
# GTest_ROOT may be used to specify the location of the GTest installation.
# Passed-in on the CMake command line overrides the environemnt variable.
# If GTest_ROOT is not set, then we will download and build GTest from source.
#
# GTest_FOUND will be set to TRUE if GTest is found, FALSE otherwise.
# If GTest was found before this module is included then we return immediately.
#
# If GTest was not already found and GTest_ROOT is not set then we will
# download and build GTest from source.

# Already found GTest - return immediately
if( GTest_FOUND )
    message( STATUS "Found GTest already: skipping")
    return()
endif()

# GTEST_ROOT may be used to specify the location of the GTest installation.
# Passed-in on the CMake command line overrides the environemnt variable.
if( NOT GTEST_ROOT )
    if( DEFINED ENV{GTEST_ROOT} )
        set( GTEST_ROOT $ENV{GTEST_ROOT})
    endif()
endif()

if( GTEST_ROOT )
    find_package( GTest REQUIRED HINTS ${GTEST_ROOT} )
    if( NOT GTest_FOUND )
        message( FATAL_ERROR "Not found GTest: ${GTEST_ROOT}")
    else()
        message( STATUS "Found GTest: ${GTEST_ROOT}")
        return()
    endif()
endif()

# If GTest_ROOT is not set, then we will download and build GTest from source.
function( init_google_test )
    include(FetchContent)

    FetchContent_Declare(
        googletest
        GIT_REPOSITORY https://github.com/google/googletest.git
        GIT_TAG release-1.12.1
        GIT_CONFIG core.longpaths=true
    )

    # For Windows: Prevent overriding the parent project's compiler/linker settings
    set(gtest_force_shared_crt ON CACHE BOOL "" FORCE)

    # Only GTEST and no install.
    # Tests run in the build.
    set( BUILD_GMOCK OFF )
    set( INSTALL_GTEST OFF )
    FetchContent_makeAvailable( googletest )

    if( NOT TARGET GTest::gtest OR NOT TARGET GTest::gtest_main )
        set( GTest_FOUND FALSE)
        message( FATAL_ERROR "Not found GTest")
    else()
        get_target_property( orgigGtest GTest::gtest ALIASED_TARGET )
        get_target_property( orgigGtestMain GTest::gtest_main ALIASED_TARGET )
        if( CMAKE_CXX_COMPILER_ID STREQUAL "GNU")
            set( flags
                    -Wno-conversion
                    -Wno-undef
                    -Wno-missing-noreturn
                    -Wno-switch-enum
                    -Wno-zero-as-null-pointer-constant)
        endif()
        if( CMAKE_CXX_COMPILER_ID MATCHES "Clang" )
            set( flags
                    -Wno-unused-member-function
                    -Wno-undef
                    -Wno-global-constructors
                    -Wno-weak-vtables
                    -Wno-reserved-identifier
                    -Wno-missing-noreturn
                    -Wno-covered-switch-default
                    -Wno-switch-enum
                    -Wno-used-but-marked-unused
                    -Wno-zero-as-null-pointer-constant)
        endif()
        target_compile_options( ${orgigGtest} PRIVATE ${flags} )
        target_compile_options( ${orgigGtestMain} PRIVATE ${flags} )
        message( STATUS "Found GTest: built from source")
    endif()

    set( GTest_FOUND TRUE )
    set( GTest_FOUND ${GTest_FOUND} PARENT_SCOPE )
endfunction()

init_google_test()
