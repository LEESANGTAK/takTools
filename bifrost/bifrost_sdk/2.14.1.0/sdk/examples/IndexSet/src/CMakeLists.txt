#-
# ===========================================================================
# Copyright 2022 Autodesk, Inc. All rights reserved.
#
# Use of this software is subject to the terms of the Autodesk license
# agreement provided at the time of installation or download, or which
# otherwise accompanies this software in either electronic or hard copy form.
# ===========================================================================
#+

# Build and install the library
add_library( IndexSetOps SHARED)
target_compile_definitions( IndexSetOps PRIVATE INDEX_SET_BUILD_NODEDEF_DLL )
target_sources( IndexSetOps PRIVATE IndexSet.cpp)
target_link_libraries( IndexSetOps PUBLIC Amino::Cpp )
target_link_libraries( IndexSetOps PUBLIC Amino::Core )
bifrost_set_install_rpath(IndexSetOps)
install( TARGETS IndexSetOps DESTINATION lib )

# Generate and install the json files
set( headers_to_parse 
    IndexSet.h
)

bifrost_header_parser( 
    IndexSetJsonFiles      # Name of the target.
    "json/${PROJECT_NAME}" # Install and build dirs - relative to install prefix
                           # and build directory
    INCLUDE_DIRS ${CMAKE_CURRENT_SOURCE_DIR}
    HEADER_FILES ${headers_to_parse})

# Create config json file to load the bifrost pack
set( CONFIG_PACK_VERSION "${PROJECT_VERSION}")
set( CONFIG_PACK_NAME "${PROJECT_NAME}")
set( CONFIG_SHARED_LIBS "./lib")
set( CONFIG_JSON_FILES "./json/${PROJECT_NAME}")
set( config_json ${CMAKE_BINARY_DIR}/${PROJECT_NAME}PackConfig.json )
configure_file(PackConfig.json.in ${config_json} )
install(FILES ${config_json} DESTINATION . )
