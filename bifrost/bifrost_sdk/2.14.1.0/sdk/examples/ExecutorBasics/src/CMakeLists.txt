#-
# ===========================================================================
# Copyright 2025 Autodesk, Inc. All rights reserved.
#
# Use of this software is subject to the terms of the Autodesk license
# agreement provided at the time of installation or download, or which
# otherwise accompanies this software in either electronic or hard copy form.
# ===========================================================================
#+

#
# Define the ExecutorBasics TypeTranslation table
#
add_library(ExecutorBasicsTranslation SHARED
    ExecutorBasicsExport.h
    ExecutorBasicsValueData.h
    ExecutorBasicsTranslation.cpp
    ExecutorBasicsTranslation.h
)

target_link_libraries(ExecutorBasicsTranslation
    PRIVATE
        Amino::Core
        BifrostGraph::Executor
)

set_target_properties(ExecutorBasicsTranslation
    PROPERTIES DEFINE_SYMBOL EXECUTOR_BASICS_TRANSLATION_EXPORT)

#
# Configure the ExecutorBasicsConfig.json file
# This file contains paths to load shared library and json libraries.
# Those paths are not the same if we are in the install tree or the build tree
# so we need to configure it twice.
#
set(EXECUTOR_BASICS_TRANSLATION_LIB_PATH "./lib")
configure_file(ExecutorBasicsConfig.json.in ${CMAKE_CURRENT_BINARY_DIR}/ExecutorBasicsConfig_install.json)

# Configure the ExecutorBasicsConfig.json for the build tree.
# (For running tests or just to be able to run the application from VisualStudio)
# The file will be in the same directory as the shared library (This handles multi-config generator and single-config generator).
set(EXECUTOR_BASICS_TRANSLATION_LIB_PATH ".")
configure_file(ExecutorBasicsConfig.json.in ${CMAKE_CURRENT_BINARY_DIR}/ExecutorBasicsConfig_build.json)
file(GENERATE
    OUTPUT $<TARGET_FILE_DIR:ExecutorBasicsTranslation>/ExecutorBasicsConfig.json
    INPUT ${CMAKE_CURRENT_BINARY_DIR}/ExecutorBasicsConfig_build.json
)

bifrost_set_install_rpath(ExecutorBasicsTranslation)
install(
    FILES ${CMAKE_CURRENT_BINARY_DIR}/ExecutorBasicsConfig_install.json
    RENAME ExecutorBasicsConfig.json
    DESTINATION .
)
install(TARGETS ExecutorBasicsTranslation DESTINATION lib)

#
# The ExecutorBasics executable
#
add_executable(ExecutorBasics
    main.cpp
    ExecutorBasicsValueData.h
)
set_target_properties(ExecutorBasics
    PROPERTIES OUTPUT_NAME executor_basics)

include(${BIFROST_LOCATION}/sdk/cmake/setup.cmake)
find_package(Bifrost REQUIRED SDK)

target_link_libraries(ExecutorBasics
    PRIVATE
        Amino::Core
        BifrostGraph::Executor
)

bifrost_set_install_rpath(ExecutorBasics
    EXTRA_RPATHS
        ${BIFROST_LOCATION}/lib
        ${BIFROST_LOCATION}/thirdparty/lib)
install(TARGETS ExecutorBasics DESTINATION bin )


#
# Define tests
#

set(PATH_TO_ADD "")
if(WIN32)
    file(GLOB USD_LIB_PATHS "${BIFROST_LOCATION}/packs/usd_pack/*/thirdparty/bin/usd_usd.dll" "${BIFROST_LOCATION}/packs/usd_pack/*/thirdparty/bin/usd.dll")
    if(NOT USD_LIB_PATHS)
        message(FATAL_ERROR "Can't find usd libs.")
    ENDIF(NOT USD_LIB_PATHS)

    # We may ship Bifrost USD with multiple USD versions.
    # We build the sdk-examples only against the most recent USD version.
    list(SORT USD_LIB_PATHS)
    list(LENGTH USD_LIB_PATHS usd_lib_paths_length)
    math(EXPR last_index "${usd_lib_paths_length} - 1")
    list(GET USD_LIB_PATHS ${last_index} USD_LIB_PATH)

    file(TO_NATIVE_PATH ${USD_LIB_PATH} USD_LIB_PATH_NATIVE)
    get_filename_component(USD_PACK_DIR "${USD_LIB_PATH_NATIVE}" DIRECTORY)

    set(PATH_TO_ADD
        "${BIFROST_LOCATION}/bin"
        "${BIFROST_LOCATION}/thirdparty/bin"
        "${USD_PACK_DIR}")

    bifrost_convert_to_env_var_list( INPUT_LIST ${PATH_TO_ADD} OUTPUT_VAR PATH_TO_ADD)
endif(WIN32
)

# test with config file from cmdline
add_test(NAME ExecutorBasics_ConfigArg COMMAND executor_basics
    --config-file ${BIFROST_LOCATION}/resources/standalone_config.json
    --config-file ${BIFROST_LOCATION}/packs/packs_standalone_config.json
    --config-file $<TARGET_FILE_DIR:ExecutorBasicsTranslation>/ExecutorBasicsConfig.json
    --definition-file ${CMAKE_CURRENT_SOURCE_DIR}/../AddNumbers.json
    --graph-name Examples::SDK::AddNumbers
    --set-port value1 2
    --set-port value2 13
)

set_tests_properties(ExecutorBasics_ConfigArg PROPERTIES
    ENVIRONMENT "PATH=${PATH_TO_ADD}"
    PASS_REGULAR_EXPRESSION "Output value for port 'result': 15.000000"
)

# test with config file from env
add_test(NAME ExecutorBasics_ConfigEnv COMMAND executor_basics
    --definition-file ${CMAKE_CURRENT_SOURCE_DIR}/../AddNumbers.json
    --graph-name Examples::SDK::AddNumbers
    --set-port value1 3.1
    --set-port value2 0.04159
)

set(BIFROST_LIB_CONFIG_FILES
    "${BIFROST_LOCATION}/resources/standalone_config.json"
    "${BIFROST_LOCATION}/packs/packs_standalone_config.json"
    "$<TARGET_FILE_DIR:ExecutorBasicsTranslation>/ExecutorBasicsConfig.json")

bifrost_convert_to_env_var_list( INPUT_LIST ${BIFROST_LIB_CONFIG_FILES} OUTPUT_VAR BIFROST_LIB_CONFIG_FILES)

set_tests_properties(ExecutorBasics_ConfigEnv PROPERTIES
    ENVIRONMENT "PATH=${PATH_TO_ADD};BIFROST_LIB_CONFIG_FILES=${BIFROST_LIB_CONFIG_FILES}"
    PASS_REGULAR_EXPRESSION "Output value for port 'result': 3.14159"
)

####################################################################################
# Visual Studio specific
#
# Setup ExecutorBasics properties to be able to run directly in VisualStudio.
# - Add bifrost library path
# - This will allow to execute the graph Examples::SDK::AddNumbers from AddNumbers.json.
####################################################################################
set_target_properties(
    ExecutorBasics
    PROPERTIES
        VS_DEBUGGER_ENVIRONMENT "PATH=${PATH_TO_ADD}"
        VS_DEBUGGER_COMMAND_ARGUMENTS "--config-file \"${BIFROST_LOCATION}/resources/standalone_config.json\" --config-file \"${BIFROST_LOCATION}/packs/packs_standalone_config.json\"  \
                                       --config-file \"$<TARGET_FILE_DIR:ExecutorBasicsTranslation>/ExecutorBasicsConfig.json\" --definition-file \"${CMAKE_CURRENT_SOURCE_DIR}/../AddNumbers.json\" \
                                       --graph-name Examples::SDK::AddNumbers --set-port value1 2 --set-port value2 13"
)
set_property(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR} PROPERTY VS_STARTUP_PROJECT ExecutorBasics)

set_property(GLOBAL PROPERTY USE_FOLDERS ON)
set_target_properties(ExecutorBasics ExecutorBasicsTranslation
    PROPERTIES FOLDER ${PROJECT_NAME}
)
