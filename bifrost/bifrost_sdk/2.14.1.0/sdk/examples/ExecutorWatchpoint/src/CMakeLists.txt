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
# Define cmake target to parse PeriodicTableElement.h
# and generate a json file for our custom type.
# This will call amino cpp2json tool.
#
bifrost_header_parser(
    PeriodicTableElementJsonFile   # Name of the target.
    "json/${PROJECT_NAME}"         # Install and build dirs - relative to install prefix and build directory
    INCLUDE_DIRS ${CMAKE_CURRENT_SOURCE_DIR}
    HEADER_FILES PeriodicTableElement.h
)

#
# Define the PeriodicTableElementType target.
# This is the shared library which contains our custom PeriodicTableElement type.
#
add_library(PeriodicTableElementType SHARED
    ExecutorWatchpointExport.h
    PeriodicTableElement.h
    PeriodicTableElement.cpp
)

target_link_libraries(PeriodicTableElementType
    PRIVATE
        Amino::Core
        Amino::Cpp
)

set_target_properties(PeriodicTableElementType
    PROPERTIES DEFINE_SYMBOL EXECUTOR_WATCHPOINT_BUILD_DLL)

bifrost_set_install_rpath(PeriodicTableElementType)
install(TARGETS PeriodicTableElementType DESTINATION lib)

#
# Define the PeriodicTableElementWatchpoint target.
# This is the shared library which handle the watchpoint for our custom PeriodicTableElement type.
#
add_library(PeriodicTableElementWatchpoint SHARED
    ExecutorWatchpointExport.h
    PeriodicTableElementWatchpoint.cpp
)

target_link_libraries(PeriodicTableElementWatchpoint
    PRIVATE
        Amino::Core
        BifrostGraph::Executor
        PeriodicTableElementType
)

set_target_properties(PeriodicTableElementWatchpoint
    PROPERTIES DEFINE_SYMBOL EXECUTOR_WATCHPOINT_BUILD_DLL)

#
# Configure the ExecutorWatchpointPackConfig.json file
# This file contains paths to load shared libraries and json libraries.
# Those paths are not the same if we are in the install tree or the build tree
# so we need to configure it twice.
#
set(CONFIG_JSON_FILES "json/${PROJECT_NAME}")
set(CONFIG_LIB_PATH "./lib")
configure_file(ExecutorWatchpointPackConfig.json.in ${CMAKE_CURRENT_BINARY_DIR}/ExecutorWatchpointPackConfig_install.json)

# Configure the ExecutorWatchpointPackConfig.json. for the build tree.
# (For running tests or just to be able to run the application from VisualStudio)
# This file will be in the same directory as the shared library (This handles multi-config generator and single-config generator).
set(CONFIG_JSON_FILES "${CMAKE_BINARY_DIR}/json/${PROJECT_NAME}")
set(CONFIG_LIB_PATH ".")
configure_file(ExecutorWatchpointPackConfig.json.in ${CMAKE_CURRENT_BINARY_DIR}/ExecutorWatchpointPackConfig_build.json)
file(GENERATE
    OUTPUT $<TARGET_FILE_DIR:PeriodicTableElementWatchpoint>/ExecutorWatchpointPackConfig.json
    INPUT ${CMAKE_CURRENT_BINARY_DIR}/ExecutorWatchpointPackConfig_build.json
)

bifrost_set_install_rpath(PeriodicTableElementWatchpoint)
install(
    FILES ${CMAKE_CURRENT_BINARY_DIR}/ExecutorWatchpointPackConfig_install.json
    RENAME ExecutorWatchpointPackConfig.json
    DESTINATION . )
install(TARGETS PeriodicTableElementWatchpoint DESTINATION lib)

#
# The ExecutorWatchpoint executable
#
add_executable(ExecutorWatchpoint
    main.cpp
)

set_target_properties(ExecutorWatchpoint
    PROPERTIES OUTPUT_NAME executor_watchpoint)

target_link_libraries(ExecutorWatchpoint
    PRIVATE
        Amino::Core
        BifrostGraph::Executor
        PeriodicTableElementType
)

bifrost_set_install_rpath(ExecutorWatchpoint
    EXTRA_RPATHS
        ../lib
        ${BIFROST_LOCATION}/lib
        ${BIFROST_LOCATION}/thirdparty/lib)
install(TARGETS ExecutorWatchpoint DESTINATION bin)

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
add_test(NAME ExecutorWatchpoint_ConfigArg COMMAND ExecutorWatchpoint
    --config-file ${BIFROST_LOCATION}/resources/standalone_config.json
    --config-file ${BIFROST_LOCATION}/packs/packs_standalone_config.json
    --config-file $<TARGET_FILE_DIR:PeriodicTableElementWatchpoint>/ExecutorWatchpointPackConfig.json
)

set_tests_properties(ExecutorWatchpoint_ConfigArg PROPERTIES
    ENVIRONMENT "PATH=${PATH_TO_ADD}"
    FAIL_REGULAR_EXPRESSION "Failure at line"
)
