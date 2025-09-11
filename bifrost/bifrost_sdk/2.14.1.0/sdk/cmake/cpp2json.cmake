#-
#*****************************************************************************
# Copyright 2024 Autodesk, Inc. All rights reserved.
#
# Use of this software is subject to the terms of the Autodesk license
# agreement provided at the time of installation or download, or which
# otherwise accompanies this software in either electronic or hard copy form.
#*****************************************************************************
#+

set(AMINO_CPP2JSON_BACKCOMP on)
set(AMINO_CPP2JSON_BACKCOMP_IGNORE_WARNINGS off)

#==============================================================================
# amino_cpp2json
#
# Function that takes a list of c++ header files as input and generates one
# json file for each input in the given destination directory. The name of each
# generated json file has a ".json" extension. So foo.h will produce a
# foo.json in the destination directory.
#
#   amino_cpp2json_2(target_name
#       HEADER_FILES         header1.h header2.h ...
#
#       [CPP2JSON            cpp2json_file_path                              ]
#       [DESTINATION         Directory in which to generate the json files.  ]
#       [DEFINITIONS         <name1>=<value1> <name2>=<value2> ...           ]
#       [INCLUDE_DIRS        include_dir1 include_dir2 ...                   ]
#       [SYSTEM_INCLUDE_DIRS system_include_dir1 system_include_dir2 ...     ]
#       [LINK_LIBS           link_lib1 link_lib2 ...                         ]
#       [OPTIONS             option1 option2 ...                             ]
#
#       [DEPENDS             target1 target2 ...                             ]
#       [PATH                path                                            ]
#       [OUT_VAR             var_name                                        ]
#   )
#
# target_name         - cmake target name.
#
# HEADER_FILES        - path(s) to input C++ header files to parse. If the path
#                       is relative, it will be prefixed with
#                       ${CMAKE_CURRENT_SOURCE_DIR} before calling cpp2json.
#
# CPP2JSON            - path to the cpp2json executable file.
#
# DESTINATION         - [optional] path to the output dir where json files are
#                       to be generated. Default is ${CMAKE_CURRENT_BINARY_DIR}.
#                       A relative path is treated relative to
#                       ${CMAKE_CURRENT_BINARY_DIR}.
#
# DEFINITIONS         - [optional] Preprocessor define(s) to be added for
#                       parsing input.
#
# INCLUDE_DIRS        - [optional] path(s) to file(s) to be included when
#                       parsing the C++ header file.
#                       Note: typically better to use LINK_LIBS instead of
#                       INCLUDE_DIRS when possible. This would extract the
#                       include directories to pass to cpp2json from the
#                       link libs targets and setup target dependencies
#                       correctly.
#
# LINK_LIBS           - [optional] cmake targets from which to extract interface
#                       include directories. The libs will also be marked as
#                       dependencies for this target.
#
# SYSTEM_INCLUDE_DIRS - [optional] include path(s) for system headers.
#
# OPTIONS             - [optional] additional options to pass to cpp2json
#                       executable.
#
# DEPENDS             - [optional] cmake target dependencies for this target
#                       The input C++ header file is always automatically added.
#
# PATH                - [optional] full path to a directory to be set in the
#                       PATH environment variable in order to execute cpp2json.
#                       On Windows platform, this argument affects the search
#                       path for both executable files and shared libraries;
#                       it may be required if a third party library
#                       (e.g. tbb.dll), required to run cpp2json, is installed
#                       in a separate directory.
#                       On Unix platforms, this argument affects only the search
#                       path for executable files, and has no effect if the
#                       provided path to the cpp2json binary file is a full
#                       path; nevertheless, it is recommended to not use this
#                       argument on Unix platforms.
#
# OUT_VAR             - [optional] The cmake variable to store the list of
#                       generated json file names.
#
function(amino_cpp2json target_name)
    set(options)
    set(oneValues
        CPP2JSON            # cpp2json executable
        DESTINATION         # output directory in which to generate jsons
        PATH                # PATH to set before running cpp2json executable
        OUT_VAR             # variable to assign to output json files list
    )
    set(multiValues
        HEADER_FILES        # list of header files to run cpp2json on
        DEFINITIONS         # Definitions (-D)
        INCLUDE_DIRS        # Include dirs (-I)
        SYSTEM_INCLUDE_DIRS # System include dirs (-isystem)
        LINK_LIBS           # Target lib dependencies (will use their interface
                            # include dirs when running cpp2json)
        DEPENDS             # target dependencies
        OPTIONS             # Other options to pass to cpp2json
    )

    if (AMINO_CPP2JSON_BACKCOMP)
        list(APPEND oneValues TARGET INPUT OUTPUT OUTPUT_DIR CALL VAR)
        list(APPEND multiValues INPUTS DEFINES INCLUDES SYSTEM_INCLUDES CANCEL)
        list(FIND oneValues ${target_name} oneValueIdx)
        list(FIND multiValues ${target_name} multiValuesIdx)
        if ((NOT ${oneValueIdx} EQUAL -1) OR (NOT ${multiValuesIdx} EQUAL -1))
            # Was used as an argument identifier.
            list(PREPEND ARGN ${target_name})
            unset(target_name)
        endif()
    endif()

    cmake_parse_arguments(CPP2JSON
        "${options}"
        "${oneValues}"
        "${multiValues}"
        ${ARGN})

    if (AMINO_CPP2JSON_BACKCOMP)
        # Report deprecations
        if (DEFINED CPP2JSON_TARGET)
            amino_cpp2json_deprecated_message("TARGET"
                "Use the first argument as the target name instead.")
            set(target_name ${CPP2JSON_TARGET})
        elseif(NOT DEFINED target_name)
            message(WARNING "amino_cpp2json's first argument should be the target name.")
        endif()
        amino_cpp2json_deprecated("INPUT" "HEADER_FILES" ${CPP2JSON_INPUT})
        if (DEFINED CPP2JSON_OUTPUT)
            amino_cpp2json_deprecated_message("OUTPUT"
                "Use DESTINATION directory. If the output file is used to rename the output json to something different than the default, use configure_file on the produced default json to copy it somewhere else differently.")
        endif()
        amino_cpp2json_deprecated("OUTPUT_DIR" "DESTINATION"  ${CPP2JSON_OUTPUT_DIR})
        if (DEFINED CPP2JSON_CALL)
            amino_cpp2json_deprecated_message("CALL"
                "Use OUT_VAR and call your cmake function on the output jsons instead. Remember that doing some kind of post-process on the json files, may require you to fix up your cmake dependencies.")
        endif()
        if (DEFINED CPP2JSON_CANCEL)
            amino_cpp2json_deprecated_message("CANCEL"
                "Use StopToken jobports on your operators instead to support cancellation.")
            unset(CPP2JSON_CANCEL)
        endif()
        amino_cpp2json_deprecated("VAR" "OUT_VAR" ${CPP2JSON_VAR})

        amino_cpp2json_deprecated("INPUTS" "HEADER_FILES" ${CPP2JSON_INPUTS})
        amino_cpp2json_deprecated("DEFINES" "DEFINITIONS" ${CPP2JSON_DEFINES})
        amino_cpp2json_deprecated("INCLUDES" "INCLUDE_DIRS" ${CPP2JSON_INCLUDES})
        amino_cpp2json_deprecated("SYSTEM_INCLUDES" "SYSTEM_INCLUDE_DIRS" ${CPP2JSON_SYSTEM_INCLUDES})
    endif()

    foreach(unknown_arg IN LISTS ARG_UNPARSED_ARGUMENTS)
        set(msg "Unknown argument ${unknown_arg} in ${CMAKE_CURRENT_FUNCTION}.")
        if (NOT AMINO_CPP2JSON_BACKCOMP)
            set(msg "${msg} It's possible that you're using deprecated arguments.
                You may try setting AMINO_CPP2JSON_BACKCOMP to ON and then use
                the warning messages to fix your calls to amino_cpp2json to
                use the non-deprecated arguments.")
        endif()
        message(FATAL_ERROR ${msg})
    endforeach()

    # Validate switches.
    if (NOT CPP2JSON_CPP2JSON)
        # TODO Make this always find cpp2json by default from imported target
        # from find_package for Amino.
        set(CPP2JSON_CPP2JSON $<TARGET_FILE:cpp2json>)
    endif()

    if (NOT CPP2JSON_DESTINATION)
        set(CPP2JSON_DESTINATION ${CMAKE_CURRENT_BINARY_DIR})
    elseif(NOT IS_ABSOLUTE ${CPP2JSON_DESTINATION})
        set(CPP2JSON_DESTINATION
            "${CMAKE_CURRENT_BINARY_DIR}/${CPP2JSON_DESTINATION}")
    endif()

    # All options
    set(all_opts)

    #=======================
    # DEFINITIONS
    #=======================

    foreach(def ${CPP2JSON_DEFINITIONS})
        list(APPEND all_opts "-D${def}")
    endforeach()

    #=======================
    # INCLUDES DIRS
    #=======================

    foreach(include_dir ${CPP2JSON_INCLUDE_DIRS})
        list(APPEND all_opts "-I${include_dir}")
    endforeach()

    set(target_include_dirs)
    # TODO Make this always link against AminoCppOpSDK by default from imported
    # target from find_package for Amino.
    list(REMOVE_DUPLICATES CPP2JSON_LINK_LIBS)
    foreach(target ${CPP2JSON_LINK_LIBS})
        get_target_property(includes ${target} INTERFACE_INCLUDE_DIRECTORIES)
        list(APPEND target_include_dirs ${includes})
    endforeach()
    list(REMOVE_DUPLICATES target_include_dirs)

    foreach(include_dir ${target_include_dirs})
        list(APPEND all_opts $<$<BOOL:${include_dir}>:-I${include_dir}>)
    endforeach()

    #=======================
    # SYSTEM INCLUDES DIRS
    #=======================

    foreach(include_dir ${CPP2JSON_SYSTEM_INCLUDE_DIRS})
        list(APPEND all_opts "-isystem ${inc}")
    endforeach()

    # Add system headers, c++ headers path for OSX, because cpp2json can not
    # auto-detect them on OSX yet.
    if (CMAKE_SYSTEM_NAME STREQUAL "Darwin")
        # Get c++ compiler install directory.
        get_filename_component(CXXBIN ${CMAKE_CXX_COMPILER} DIRECTORY)
        get_filename_component(CXXDIR ${CXXBIN} DIRECTORY)
        list(APPEND all_opts "-isysroot"  ${CMAKE_OSX_SYSROOT}
                             "-toolchain" "${CXXDIR}")
    endif()

    # On linux, gcc headers(e.g. intrinsics) use gcc builtins. cpp2json(clang)
    # does not know those builtins. So pick clang system headers. This will not
    # be needed if clang headers are shipped with cpp2json in future.
    if (CMAKE_SYSTEM_NAME STREQUAL "Linux" AND
        CMAKE_CXX_COMPILER_ID STREQUAL "Clang")
        execute_process(
            COMMAND ${CMAKE_CXX_COMPILER} --print-resource-dir
            OUTPUT_VARIABLE res_dir
            OUTPUT_STRIP_TRAILING_WHITESPACE
        )
        if (NOT "${res_dir}" STREQUAL "")
            list(APPEND all_opts "-isystem"  ${res_dir}/include)
        endif()
    endif()

    #=======================
    # RUN CPP2JSON
    #=======================

    set(cmd_name ${CPP2JSON_CPP2JSON})
    if(DEFINED CPP2JSON_PATH)
        # Add PATH environment for cpp2json.
        cmake_path(NATIVE_PATH CPP2JSON_PATH NORMALIZE path_value)
        set(cmd_name ${CMAKE_COMMAND} -E env PATH="${path_value}"
            ${CPP2JSON_CPP2JSON})
    endif()

    set(output_files)
    foreach(header_file ${CPP2JSON_HEADER_FILES})
        get_filename_component(file_name ${header_file} NAME_WE)
        set(out_file ${CPP2JSON_DESTINATION}/${file_name}.json)

        if (AMINO_CPP2JSON_BACKCOMP AND DEFINED CPP2JSON_OUTPUT)
            set(out_file ${CPP2JSON_OUTPUT})
            if(NOT IS_ABSOLUTE ${out_file})
                set(out_file "${CMAKE_CURRENT_BINARY_DIR}/${out_file}")
            endif()
        endif()

        if(NOT IS_ABSOLUTE ${header_file})
            set(header_file ${CMAKE_CURRENT_SOURCE_DIR}/${header_file})
        endif()
        add_custom_command(
            OUTPUT ${out_file}
            COMMAND ${cmd_name}
                ${all_opts}
                ${CPP2JSON_OPTIONS}
                ${header_file} -o ${out_file}
            DEPENDS
                ${CPP2JSON_CPP2JSON}
                ${CPP2JSON_LINK_LIBS}
                ${CPP2JSON_DEPENDS}
                ${header_file})

        # call the specified cmake function on each output file.
        if (AMINO_CPP2JSON_BACKCOMP)
            if (DEFINED CPP2JSON_CALL)
                cmake_language(CALL ${CPP2JSON_CALL} ${out_file})
            endif()
            if (NOT target_name)
                string(SHA1 target_name ${out_file})
            endif()
        endif()

        list(APPEND output_files ${out_file})
    endforeach()

    #=======================
    # CREATE TARGET
    #=======================

    add_custom_target(${target_name} ALL DEPENDS
        ${output_files} ${CPP2JSON_DEPENDS})

    # Set the OUT_VAR if was asked for.
    if (CPP2JSON_OUT_VAR)
        set(${CPP2JSON_OUT_VAR} ${output_files} PARENT_SCOPE)
    endif()

endfunction(amino_cpp2json)

#==============================================================================
# amino_mergepacks
#
# Merge multiple json files into one.
# cmake wrapper for mergepacks.py script.
#
#   amino_mergepacks(
#       TARGET         - cmake_target_name                                    ]
#       PYTHON         - path of python binary. Defaults to "python3".
#       MERGEPACKS     - full path of mergepacks.py script. (Required)
#       INPUTS         - json1 json2 ...
#       OUTPUT         - merged_json_file_path
#       [DEPENDS       - other_cmake_target .. on which this depends          ]
#       [USE_INTERMEDIATE_FILE]
#   )
#
# TARGET                - A cmake target name for this output.
# PYTHON                - path to python binary.
# MERGEPACKS            - path to mergepacks.py script.
# INPUTS                - input json file path(s).
# OUTPUT                - path of output json file
# DEPENDS               - cmake target name(s) this action depends on.
# USE_INTERMEDIATE_FILE - use an intermediate file containing the given "INPUTS"
#                         as input to the mergepacks script. Useful under some
#                         platforms (like Windows), where the length of commands
#                         are limited (which would result in build failure since
#                         the system would refuse to execute the long command).
#
function(amino_mergepacks)
    set(options USE_INTERMEDIATE_FILE)
    set(singleValues PYTHON MERGEPACKS TARGET OUTPUT)
    set(multiValues INPUTS DEPENDS)
    # Unpack switches.
    cmake_parse_arguments(MP
        "${options}"
        "${singleValues}"
        "${multiValues}"
        ${ARGN})

    # Validate switches.
    # \todo BIFROST-7003 make this a FATAL_ERROR once other repos follow.
    if (NOT MP_TARGET)
        message(WARNING " No TARGET was specified.")
    endif()
    if (NOT MP_PYTHON)
        set(MP_PYTHON "python3")
        message(WARNING " Path of python was not specified with PYTHON, using from PATH.")
    endif()
    if (NOT MP_MERGEPACKS)
        message(FATAL_ERROR " Path of mergepacks.py was not specified with MERGEPACKS.")
    endif()
    if (NOT MP_INPUTS)
        message(FATAL_ERROR " No input file(s) were specified with INPUTS.")
    endif()
    if (NOT MP_OUTPUT)
        message(FATAL_ERROR " No output file was specified with OUTPUT.")
    endif()

    # Need to regenerate merged jsons when either the mergepack target itself
    # has changed, one of the explicitly given target dependencies has changed
    # or a input json file has changed (or was removed or added)
    set(depends
        ${MP_MERGEPACKS}
        ${MP_INPUTS}
        ${MP_DEPENDS}
    )
    if (MP_USE_INTERMEDIATE_FILE)
        get_filename_component(suffix ${MP_OUTPUT} NAME_WE)
        string(JOIN "\",\n    \"" joined ${MP_INPUTS})
        set(joined "{\n  \"mergepack_json_files\" : [\n    \"${joined}\"\n  ]\n}\n")
        set(joined_file ${CMAKE_CURRENT_BINARY_DIR}/mergepack_${suffix}.json)
        file(WRITE ${joined_file} ${joined})
        # override MP_INPUTS to use intermediate file instead
        set(MP_INPUTS ${joined_file})
    endif()

    # command to generate json.
    add_custom_command(
        OUTPUT ${MP_OUTPUT}
        COMMAND ${MP_PYTHON} ${MP_MERGEPACKS}
                ${MP_INPUTS} -o ${MP_OUTPUT}
        DEPENDS ${depends}
    )

    # generate an unique target name based on the output file
    # if none was specified.
    if (NOT MP_TARGET)
        string(SHA1 MP_TARGET ${MP_OUTPUT})
    endif()
    add_custom_target(${MP_TARGET} ALL DEPENDS ${MP_OUTPUT})
endfunction(amino_mergepacks)

#==============================================================================
function(amino_cpp2json_foreach)
    if (AMINO_CPP2JSON_BACKCOMP)
        if (NOT AMINO_CPP2JSON_BACKCOMP_IGNORE_WARNINGS)
            message(WARNING "amino_cpp2json_foreach is deprecated."
                    "Use amino_cpp2json instead.")
        endif()

        cmake_parse_arguments(CPP2JSON "" "VAR" "" ${ARGN})
        amino_cpp2json(${ARGN} VAR out_var)

        if (DEFINED CPP2JSON_VAR)
            set(${CPP2JSON_VAR} ${out_var} PARENT_SCOPE)
        endif()
    else()
        message(FATAL_ERROR
            "No such amino_cpp2json_foreach function. Use amino_cpp2json.")
    endif()
endfunction()

function(amino_cpp2json_deprecated_message previous_arg instead)
    if (NOT AMINO_CPP2JSON_BACKCOMP_IGNORE_WARNINGS)
        message(WARNING "amino_cpp2json ${previous_arg} argument is deprecated."
                "${instead}")
    endif()
endfunction()

function(amino_cpp2json_deprecated previous_arg new_arg)
    if (ARGN)
        amino_cpp2json_deprecated_message(
            ${previous_arg} "Use ${new_arg} instead.")
        set(CPP2JSON_${new_arg} ${ARGN} PARENT_SCOPE)
    endif()
endfunction()
