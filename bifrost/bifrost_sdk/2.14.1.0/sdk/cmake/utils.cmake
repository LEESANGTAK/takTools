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

include( ${BIFROST_LOCATION}/sdk/cmake/cpp2json.cmake )
#===============================================================================
# JSON Generation
#===============================================================================

# Helper function to parse the headers to generate json files used to add
# custom types and operators in Amino library.
#
#   bifrost_header_parser(<target_name> <json_output_dir>
#       other modes are standard amino_cpp2json modes.(see cpp2json.cmake)
#   )
#
#   target_name - Name of the target
#   json_output_dir - Path where the json files are generated. Used for build
#                     (relative to the build directory) and install (relative
#                     to the install directory).
function(bifrost_header_parser target_name json_output_dir)
    get_target_property( bifrost_inc_dirs  Amino::Core  INTERFACE_INCLUDE_DIRECTORIES )

    if (IS_ABSOLUTE ${json_output_dir})
        message( FATAL_ERROR "Bifrost: The json_output_dir path cannot be absolute. It must be relative to the build and install directories.")
    endif()

    FILE(MAKE_DIRECTORY ${CMAKE_BINARY_DIR}/${json_output_dir})

    amino_cpp2json(${target_name}
        OUT_VAR      node_def_jsons
        CPP2JSON     $<TARGET_FILE:Bifrost::cpp2json>
        DESTINATION  ${CMAKE_BINARY_DIR}/${json_output_dir}
        INCLUDE_DIRS ${bifrost_inc_dirs}
        ${ARGN}
    )
    install(FILES ${node_def_jsons}  DESTINATION ${json_output_dir})
endfunction(bifrost_header_parser)

# Configure the rpaths of the given target.
#
# Assume that the default dependencies are located in the same directory as the
# target.
#
#   bifrost_set_install_rpath(target EXTRA_RPATHS <dir1> <dir2> ...)
#
#   target      : The target to configure the rpaths.
#   EXTRA_RPATHS: The list of directories to add to the target's rpath.
#                 If a directory is relative, it will be prefixed with the
#                 platform specific prefix: `$ORIGIN` for linux and `@loader_path` for OSX.
#                 Windows is ignored.
function(bifrost_set_install_rpath target)
    set(options)
    set(oneValueArgs)
    set(multiValueArgs EXTRA_RPATHS)
    cmake_parse_arguments( BSIR "${options}" "${oneValueArgs}" "${multiValueArgs}" ${ARGN} )

    if(BSIR_UNPARSED_ARGUMENTS)
        message(FATAL_ERROR "Bifrost: use EXTRA_RPATHS to specify the extra rpaths.")
    endif()

    if(CMAKE_SYSTEM_NAME STREQUAL "Windows")
        return()
    endif()

    set(rpath)
    if(CMAKE_SYSTEM_NAME STREQUAL "Darwin")
        set(rpath "@loader_path/.")
    elseif(CMAKE_SYSTEM_NAME STREQUAL "Linux")
        set(rpath $ORIGIN)
    endif()

    # Append the extra rpaths
    if(BSIR_EXTRA_RPATHS)
        foreach(path ${BSIR_EXTRA_RPATHS})
            set(extra_rpath)
            cmake_path(NATIVE_PATH path NORMALIZE path )
            cmake_path( IS_ABSOLUTE path is_absolute )
            if(is_absolute)
                set(extra_rpath ${path})
            else()
                if(CMAKE_SYSTEM_NAME STREQUAL "Darwin")
                    set(extra_rpath "@loader_path/${path}")
                elseif(CMAKE_SYSTEM_NAME STREQUAL "Linux")
                    set(extra_rpath "$ORIGIN/${path}")
                endif()
            endif()

            list(APPEND rpath "${extra_rpath}")
        endforeach()
    endif()

    set_target_properties(${target} PROPERTIES INSTALL_RPATH "${rpath}")

endfunction(bifrost_set_install_rpath)

# Function to properly convert a list to an environment variable list
# separated by the correct path separator for the current platform
#
# INPUT_LIST: List of paths to convert, can be empty/undefined.
# OUTPUT_VAR: Name of the variable to set with the converted list.
function( bifrost_convert_to_env_var_list)
    set(options)
    set(oneValueArgs OUTPUT_VAR)
    set(multiValueArgs INPUT_LIST)
    cmake_parse_arguments( BCTEVL "${options}" "${oneValueArgs}" "${multiValueArgs}" ${ARGN} )

    if( NOT BCTEVL_OUTPUT_VAR )
        message( FATAL_ERROR "Bifrost: OUTPUT_VAR mode not defined." )
    endif()

    cmake_path(CONVERT "${BCTEVL_INPUT_LIST}" TO_NATIVE_PATH_LIST native_list NORMALIZE)
    if( CMAKE_SYSTEM_NAME STREQUAL "Windows" )
        string(REPLACE ";" "\\;" native_list "${native_list}")
    endif()
    set(${BCTEVL_OUTPUT_VAR} "${native_list}" PARENT_SCOPE)
endfunction()
