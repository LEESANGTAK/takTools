#-
#*****************************************************************************
# Copyright 2024 Autodesk, Inc. All rights reserved.
#
# Use of this software is subject to the terms of the Autodesk license
# agreement provided at the time of installation or download, or which
# otherwise accompanies this software in either electronic or hard copy form.
#*****************************************************************************
#+

# FindBifrost
#   Find the Bifrost related components (and libraries)
#
# Imported Components:
#   This module provides the following components
#       SDK  - Application agnostic SDK libraries.
#              Ex.: To write Bifrost C++ nodes.
#       Maya - Application specific libraries for Maya.
#
# Result Variable:
#   Bifrost_FOUND

if (NOT DEFINED BIFROST_LOCATION)
    message(FATAL_ERROR "Required variable BIFROST_LOCATION has not been defined.")
endif()

function(bifrost_init)

    set( need_required )
    if (Bifrost_FIND_REQUIRED)
        set(need_required REQUIRED)
    endif()

    set( need_quietly)
    if (Bifrost_FIND_QUIETLY)
        set(need_quietly QUIET)
    endif()

    set( all_modules SDK Maya )
    if( Bifrost_FIND_COMPONENTS )
        set(all_modules ${Bifrost_FIND_COMPONENTS})
    endif()

    # Finding modules, not Configs - use local CMAKE_MODULE_PATH
    set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} "${BIFROST_LOCATION}/sdk/cmake/internal")

    set( found_modules)
    foreach(module ${all_modules})
        find_package(Bifrost${module}
            ${need_quietly}
            ${need_required}
        )
        list( APPEND found_modules Bifrost${module}_FOUND)
    endforeach()

    include(FindPackageHandleStandardArgs)
    find_package_handle_standard_args(Bifrost
       FAIL_MESSAGE "Bifrost  Package not found..."
       REQUIRED_VARS "${found_modules}"
    )

    set( Bifrost_FOUND ${Bifrost_FOUND} PARENT_SCOPE)
endfunction()

# Using a function to scope variables and avoid polluting the global namespace!
bifrost_init()
