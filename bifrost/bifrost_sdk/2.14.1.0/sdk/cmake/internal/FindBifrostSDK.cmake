#-
#*****************************************************************************
# Copyright 2024 Autodesk, Inc. All rights reserved.
#
# Use of this software is subject to the terms of the Autodesk license
# agreement provided at the time of installation or download, or which
# otherwise accompanies this software in either electronic or hard copy form.
#*****************************************************************************
#+

# FindBifrostSDK
#   Find the BifrostSDK related libraries and executables
#
# Imported Targets
#   This module provides access to the following:
#      Bifrost::cpp2json  Access to cpp2json executable. Parsing of C++ headers.
#
#      Amino::Core Access to AminoCore library. Core types: Ptr, String, Array, ...
#      Amino::Cpp  Access to AminoCppOpSDK library. Support for creating Bifrost C++ operators and types.
#
#      Bifrost::Object    Access to BifrostObject library. Dictionary-like structure used in Bifrost.
#      Bifrost::Math      Access to BifrostMath library. Math types: vectors, matrices...
#      Bifrost::FileUtils Access to BifrostFileUtils library.
#
#      BifrostGraph::Executor Access to BifrostBoardExecutor. Translation table basic support.
#
# Result Variable:
#   BifrostSDK_FOUND

if (NOT DEFINED BIFROST_LOCATION)
    message(FATAL_ERROR "Required variable BIFROST_LOCATION has not been defined.")
endif()

include( ${BIFROST_LOCATION}/sdk/cmake/bifrost_sdk_version.info )

function(bifrost_sdk_init)
    set( all_targets
         Amino::Core
         Amino::Cpp
         Bifrost::cpp2json
         Bifrost::FileUtils
         Bifrost::Geometry
         Bifrost::Math
         Bifrost::Object
         BifrostGraph::Executor )

    set(targets_defined)
    set(targets_not_defined)
    foreach( one_target ${all_targets} )
        if(TARGET ${one_target})
            list(APPEND targets_defined ${one_target})
        else()
            list(APPEND targets_not_defined ${one_target})
        endif()
    endforeach()

    # Already all defined - OK
    if("${targets_defined}" STREQUAL "${all_targets}")
        set(BifrostSDK_FOUND true PARENT_SCOPE)
        return()
    endif()

    # Some defined some not defined - Error
    if(NOT "${targets_defined}" STREQUAL "")
        set(BifrostSDK_FOUND false PARENT_SCOPE)
        message(FATAL_ERROR "Some (but not all) targets in this export set were already defined.\nTargets Defined: ${targets_defined}\nTargets not yet defined: ${targets_not_defined}\n")
        return()
    endif()

    # Nothing defined, then define all targets
    set(bifrost_sdk_version_suffix ${BIFROST_SDK_ARCH_VERSION}_${BIFROST_SDK_MAJOR_VERSION}_${BIFROST_SDK_MINOR_VERSION})

    set(BIFROST_BIN_HINTS    "${BIFROST_LOCATION}/bin")
    set(BIFROST_INC_HINTS    "${BIFROST_LOCATION}/sdk/include")
    set(BIFROST_LIB_HINTS "")

    set(CMAKE_FIND_LIBRARY_PREFIXES "")
    set(CMAKE_FIND_LIBRARY_SUFFIXES "" )

    if(CMAKE_SYSTEM_NAME STREQUAL "Windows")
        set(CMAKE_FIND_LIBRARY_PREFIXES "")
        set(CMAKE_FIND_LIBRARY_SUFFIXES ".lib" )
        set( BIFROST_LIB_HINTS "${BIFROST_LOCATION}/sdk/lib")
    elseif( CMAKE_SYSTEM_NAME STREQUAL "Linux")
        set(CMAKE_FIND_LIBRARY_PREFIXES "lib")
        set(CMAKE_FIND_LIBRARY_SUFFIXES ".so")
        set( BIFROST_LIB_HINTS "${BIFROST_LOCATION}/lib")
    elseif(CMAKE_SYSTEM_NAME STREQUAL "Darwin")
        set(CMAKE_FIND_LIBRARY_PREFIXES "lib")
        set(CMAKE_FIND_LIBRARY_SUFFIXES ".dylib")
        set(BIFROST_LIB_HINTS "${BIFROST_LOCATION}/lib")
    endif()

    # Check if the Public SDK is part of the Preview SDK or not.
    # The current Preview SDK will have a root Amino directory.
    # The Public SDK does not.
    set(Amino_INCLUDE_DIR ${BIFROST_INC_HINTS})
    if(IS_DIRECTORY ${BIFROST_INC_HINTS}/Amino/Amino AND IS_DIRECTORY ${BIFROST_INC_HINTS}/Amino/Bifrost)
        set(Amino_INCLUDE_DIR ${BIFROST_INC_HINTS}/Amino)
    endif()
    set(Bifrost_INCLUDE_DIR ${BIFROST_INC_HINTS})
    set(Executor_INCLUDE_DIR ${BIFROST_INC_HINTS})

    # Amino
    find_library(AminoCppOpSDK_LIBRARY
        NAMES AminoCppOpSDK_${bifrost_sdk_version_suffix}
        HINTS ${BIFROST_LIB_HINTS}
        NO_DEFAULT_PATH
    )

    find_library(AminoCore_LIBRARY
        NAMES AminoCore_${bifrost_sdk_version_suffix}
        HINTS ${BIFROST_LIB_HINTS}
        NO_DEFAULT_PATH
    )

    # Bifrost
    find_library(BifrostFileUtils_LIBRARY
        NAMES BifrostFileUtils_${bifrost_sdk_version_suffix}
        HINTS ${BIFROST_LIB_HINTS}
        NO_DEFAULT_PATH
    )

    find_library(BifrostGeometry_LIBRARY
        NAMES BifrostGeometry_${bifrost_sdk_version_suffix}
        HINTS ${BIFROST_LIB_HINTS}
        NO_DEFAULT_PATH
    )

    find_library(BifrostMath_LIBRARY
        NAMES BifrostMath_${bifrost_sdk_version_suffix}
        HINTS ${BIFROST_LIB_HINTS}
        NO_DEFAULT_PATH
    )

    find_library(BifrostObject_LIBRARY
        NAMES BifrostObject_${bifrost_sdk_version_suffix}
        HINTS ${BIFROST_LIB_HINTS}
        NO_DEFAULT_PATH
    )

    # BifrostGraph
    find_library(BifrostBoardExecutor_LIBRARY
        NAMES BifrostBoardExecutor_${bifrost_sdk_version_suffix}
        HINTS ${BIFROST_LIB_HINTS}
        NO_DEFAULT_PATH
    )

    # Programs
    find_program( cpp2json_PROGRAM
        NAMES cpp2json
        HINTS ${BIFROST_BIN_HINTS}
        NO_DEFAULT_PATH )

    # Find all the necessary libs and files
    include(FindPackageHandleStandardArgs)
    find_package_handle_standard_args(BifrostSDK
        "Bifrost SDK Package not found..."
        Amino_INCLUDE_DIR
        Executor_INCLUDE_DIR
        Bifrost_INCLUDE_DIR
        AminoCppOpSDK_LIBRARY
        AminoCore_LIBRARY
        BifrostFileUtils_LIBRARY
        BifrostGeometry_LIBRARY
        BifrostMath_LIBRARY
        BifrostObject_LIBRARY
        BifrostBoardExecutor_LIBRARY
        cpp2json_PROGRAM
    )

    # Define the targets...
    # Using Bifrost::cpp2json as check that targets have already been defined
    if(BifrostSDK_FOUND )

        add_executable(Bifrost::cpp2json IMPORTED)
        set_property(TARGET Bifrost::cpp2json PROPERTY IMPORTED_LOCATION "${cpp2json_PROGRAM}")

        add_library(Amino::Cpp UNKNOWN IMPORTED)
        set_target_properties(Amino::Cpp PROPERTIES
            IMPORTED_LOCATION "${AminoCppOpSDK_LIBRARY}"
            INTERFACE_INCLUDE_DIRECTORIES "${Amino_INCLUDE_DIR}"
        )

        add_library(Amino::Core UNKNOWN IMPORTED)
        set_target_properties(Amino::Core PROPERTIES
            IMPORTED_LOCATION "${AminoCore_LIBRARY}"
            INTERFACE_INCLUDE_DIRECTORIES "${Amino_INCLUDE_DIR}"
        )

        add_library(Bifrost::FileUtils UNKNOWN IMPORTED)
        set_target_properties(Bifrost::FileUtils PROPERTIES
            IMPORTED_LOCATION "${BifrostFileUtils_LIBRARY}"
            INTERFACE_INCLUDE_DIRECTORIES "${Bifrost_INCLUDE_DIR}"
        )

        add_library(Bifrost::Geometry UNKNOWN IMPORTED)
        set_target_properties(Bifrost::Geometry PROPERTIES
            IMPORTED_LOCATION "${BifrostGeometry_LIBRARY}"
            INTERFACE_INCLUDE_DIRECTORIES "${Bifrost_INCLUDE_DIR}"
        )

        add_library(Bifrost::Math UNKNOWN IMPORTED)
        set_target_properties(Bifrost::Math PROPERTIES
            IMPORTED_LOCATION "${BifrostMath_LIBRARY}"
            INTERFACE_INCLUDE_DIRECTORIES "${Bifrost_INCLUDE_DIR}"
        )

        add_library(Bifrost::Object UNKNOWN IMPORTED)
        set_target_properties(Bifrost::Object PROPERTIES
            IMPORTED_LOCATION "${BifrostObject_LIBRARY}"
            INTERFACE_INCLUDE_DIRECTORIES "${Bifrost_INCLUDE_DIR}"
        )

        add_library(BifrostGraph::Executor UNKNOWN IMPORTED)
        set_target_properties(BifrostGraph::Executor PROPERTIES
            IMPORTED_LOCATION "${BifrostBoardExecutor_LIBRARY}"
            INTERFACE_INCLUDE_DIRECTORIES "${Executor_INCLUDE_DIR}"
        )
    endif()

    set(BifrostSDK_FOUND ${BifrostSDK_FOUND} PARENT_SCOPE)
endfunction()

# Using a function to scope variables and avoid polluting the global namespace!
bifrost_sdk_init()
