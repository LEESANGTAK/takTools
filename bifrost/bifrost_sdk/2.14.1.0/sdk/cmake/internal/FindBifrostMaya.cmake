#-
#*****************************************************************************
# Copyright 2024 Autodesk, Inc. All rights reserved.
#
# Use of this software is subject to the terms of the Autodesk license
# agreement provided at the time of installation or download, or which
# otherwise accompanies this software in either electronic or hard copy form.
#*****************************************************************************
#+

# FindBifrostMaya
#   Find the BifrostMaya related libraries.
#
# Imported Targets
#   This module provides access to the followin libraries:
#      BifrostGraph::Maya  Access to BifrostMayaHostData library. To exchange data with Maya.
#
# Result Variable:
#   BifrostMaya_FOUND

if (NOT DEFINED BIFROST_LOCATION)
    message(FATAL_ERROR "Required variable BIFROST_LOCATION has not been defined.")
endif()

include( ${BIFROST_LOCATION}/sdk/cmake/bifrost_maya_plugin_version.info )

function(bifrost_maya_init)

    set(bifrost_version_suffix ${BIFROST_MAYA_PLUGIN_APPLICATION_VERSION}_${BIFROST_MAYA_PLUGIN_MAJOR_VERSION}_${BIFROST_MAYA_PLUGIN_MINOR_VERSION})

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

    set( Bifrost_INCLUDE_DIR "${BIFROST_LOCATION}/sdk/include")

    # BifrostGraph Maya
    find_library(BifrostMayaHostData_LIBRARY
        NAMES BifrostMayaHostData_${bifrost_version_suffix}
        HINTS ${BIFROST_LIB_HINTS}
        NO_DEFAULT_PATH
    )

    # Find all the necessary libs and files
    include(FindPackageHandleStandardArgs)
    find_package_handle_standard_args(BifrostMaya
        "Bifrost Maya Package not found..."
        Bifrost_INCLUDE_DIR
        BifrostMayaHostData_LIBRARY
    )

    # Define the targets...
    # Using BifrostGraph::Maya target existence to not redefine
    if(BifrostMaya_FOUND AND NOT TARGET BifrostGraph::Maya)
        add_library(BifrostGraph::Maya UNKNOWN IMPORTED)
        set_target_properties(BifrostGraph::Maya PROPERTIES
            IMPORTED_LOCATION "${BifrostMayaHostData_LIBRARY}"
            INTERFACE_INCLUDE_DIRECTORIES "${Bifrost_INCLUDE_DIR}"
        )
    endif()

    set( BifrostMaya_FOUND ${BifrostMaya_FOUND} PARENT_SCOPE)
endfunction()

# Using a function to scope variables and avoid polluting the global namespace!
bifrost_maya_init()
