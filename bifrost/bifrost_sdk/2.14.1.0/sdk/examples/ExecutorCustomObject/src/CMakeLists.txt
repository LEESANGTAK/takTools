#-
# ===========================================================================
# Copyright 2025 Autodesk, Inc. All rights reserved.
#
# Use of this software is subject to the terms of the Autodesk license
# agreement provided at the time of installation or download, or which
# otherwise accompanies this software in either electronic or hard copy form.
# ===========================================================================
#+

include(${BIFROST_LOCATION}/sdk/cmake/setup.cmake)
find_package(Bifrost REQUIRED SDK)

#
# Define cmake target to parse ExecutorCustomObject.h
# and generate a json file for our custom type.
# This will call amino cpp2json tool.
#
bifrost_header_parser(
    ExecutorCustomObjectJsonFiles   # Name of the target.
    "json/${PROJECT_NAME}"          # Install and build dirs - relative to install prefix and build directory
    INCLUDE_DIRS ${CMAKE_CURRENT_SOURCE_DIR}
    HEADER_FILES ExecutorCustomObject.h
)

#
# Define the ExecutorCustomObjectTranslation target.
# This is the shared library which will convert our custom type.
#
add_library(ExecutorCustomObjectTranslation SHARED
    ExecutorCustomObjectExport.h
    ExecutorCustomObjectValueData.h
    ExecutorCustomObjectTranslation.cpp
    ExecutorCustomObjectTranslation.h
)

target_link_libraries(ExecutorCustomObjectTranslation
    PRIVATE
        Amino::Core
        BifrostGraph::Executor
)

set_target_properties(ExecutorCustomObjectTranslation
    PROPERTIES DEFINE_SYMBOL EXECUTOR_CUSTOM_OBJECT_TRANSLATION_EXPORT)

#
# Configure the ExecutorCustomObjectPackConfig.json file
# This file contains paths to load shared libraries and json libraries.
# Those paths are not the same if we are in the install tree or the build tree
# so we need to configure it twice.
#
set(CONFIG_JSON_FILES "json/${PROJECT_NAME}")
set(EXECUTOR_CUSTOM_OBJECT_TRANSLATION_LIB_PATH "./lib")
configure_file(ExecutorCustomObjectPackConfig.json.in ${CMAKE_CURRENT_BINARY_DIR}/ExecutorCustomTypePackConfig_install.json)

# Configure the ExecutorCustomObjectPackConfig.json. for the build tree.
# (For running tests or just to be able to run the application from VisualStudio)
# This file will be in the same directory as the shared library (This handles multi-config generator and single-config generator).
set(CONFIG_JSON_FILES "${CMAKE_BINARY_DIR}/json/${PROJECT_NAME}")
set(EXECUTOR_CUSTOM_OBJECT_TRANSLATION_LIB_PATH ".")
configure_file(ExecutorCustomObjectPackConfig.json.in ${CMAKE_CURRENT_BINARY_DIR}/ExecutorCustomTypePackConfig_build.json)
file(GENERATE
    OUTPUT $<TARGET_FILE_DIR:ExecutorCustomObjectTranslation>/ExecutorCustomObjectPackConfig.json
    INPUT ${CMAKE_CURRENT_BINARY_DIR}/ExecutorCustomTypePackConfig_build.json
)

bifrost_set_install_rpath(ExecutorCustomObjectTranslation)
install(
    FILES ${CMAKE_CURRENT_BINARY_DIR}/ExecutorCustomTypePackConfig_install.json
    RENAME ExecutorCustomObjectPackConfig.json
    DESTINATION . )
install(TARGETS ExecutorCustomObjectTranslation DESTINATION lib)

#
# The ExecutorCustomObject executable
#
add_executable(ExecutorCustomObject
    main.cpp
    ExecutorCustomObjectValueData.h
)

set_target_properties(ExecutorCustomObject
    PROPERTIES OUTPUT_NAME executor_custom_object)

target_link_libraries(ExecutorCustomObject
    PRIVATE
        Amino::Core
        BifrostGraph::Executor
)

bifrost_set_install_rpath(ExecutorCustomObject
    EXTRA_RPATHS
        ${BIFROST_LOCATION}/lib
        ${BIFROST_LOCATION}/thirdparty/lib)
install(TARGETS ExecutorCustomObject DESTINATION bin )


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
endif(WIN32)

# test with config file from cmdline
add_test(NAME ExecutorCustomObject_ConfigArg COMMAND ExecutorCustomObject
    --config-file ${BIFROST_LOCATION}/resources/standalone_config.json
    --config-file ${BIFROST_LOCATION}/packs/packs_standalone_config.json
    --config-file $<TARGET_FILE_DIR:ExecutorCustomObjectTranslation>/ExecutorCustomObjectPackConfig.json
    --definition-file ${CMAKE_CURRENT_SOURCE_DIR}/TranslateBoundingBox.json
    --graph-name Examples::SDK::TranslateBoundingBox
)

set_tests_properties(ExecutorCustomObject_ConfigArg PROPERTIES
    ENVIRONMENT "PATH=${PATH_TO_ADD}"
    PASS_REGULAR_EXPRESSION "Output value for port 'outBB' min \\[ 3, 2, 6 \\] max \\[ 5, 4, 8 \\]"
)

# test with config file from env
add_test(NAME ExecutorCustomObject_ConfigEnv COMMAND ExecutorCustomObject
    --definition-file ${CMAKE_CURRENT_SOURCE_DIR}/TranslateBoundingBox.json
    --graph-name Examples::SDK::TranslateBoundingBox
)

set(BIFROST_LIB_CONFIG_FILES
    "${BIFROST_LOCATION}/resources/standalone_config.json"
    "${BIFROST_LOCATION}/packs/packs_standalone_config.json"
    "$<TARGET_FILE_DIR:ExecutorCustomObjectTranslation>/ExecutorCustomObjectPackConfig.json")

bifrost_convert_to_env_var_list( INPUT_LIST ${BIFROST_LIB_CONFIG_FILES} OUTPUT_VAR BIFROST_LIB_CONFIG_FILES)

set_tests_properties(ExecutorCustomObject_ConfigEnv PROPERTIES
    ENVIRONMENT "PATH=${PATH_TO_ADD};BIFROST_LIB_CONFIG_FILES=${BIFROST_LIB_CONFIG_FILES}"
    PASS_REGULAR_EXPRESSION "Output value for port 'outBB' min \\[ 3, 2, 6 \\] max \\[ 5, 4, 8 \\]"
)

####################################################################################
# Visual Studio specific
#
# Setup ExecutorCustomObject properties to be able to run directly in VisualStudio.
# - Add bifrost library path
# - This will allow to execute the graph Examples::SDK::TranslateBoundingBox from
#   TranslateBoundingBox.json.
####################################################################################
set_target_properties(
    ExecutorCustomObject
    PROPERTIES
        VS_DEBUGGER_ENVIRONMENT "PATH=${PATH_TO_ADD}"
        VS_DEBUGGER_COMMAND_ARGUMENTS "--config-file \"${BIFROST_LOCATION}/resources/standalone_config.json\" --config-file \"${BIFROST_LOCATION}/packs/packs_standalone_config.json\" \
                                       --config-file \"$<TARGET_FILE_DIR:ExecutorCustomObjectTranslation>/ExecutorCustomObjectPackConfig.json\" --definition-file \"${CMAKE_CURRENT_SOURCE_DIR}/TranslateBoundingBox.json\" \
                                       --graph-name Examples::SDK::TranslateBoundingBox"
)
set_property(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR} PROPERTY VS_STARTUP_PROJECT ExecutorCustomObject)

set_property(GLOBAL PROPERTY USE_FOLDERS ON)
set_target_properties(
    ExecutorCustomObject ExecutorCustomObjectJsonFiles ExecutorCustomObjectTranslation
    PROPERTIES FOLDER ${PROJECT_NAME}
)
