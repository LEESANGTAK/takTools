#-
# ===========================================================================
# Copyright 2024 Autodesk, Inc. All rights reserved.
#
# Use of this software is subject to the terms of the Autodesk license
# agreement provided at the time of installation or download, or which
# otherwise accompanies this software in either electronic or hard copy form.
# ===========================================================================
#+
# Mesh Area operator library

add_library( MeshAreaOps SHARED)
target_compile_definitions( MeshAreaOps PRIVATE MESH_AREA_OPS_BUILD_DLL )
target_sources( MeshAreaOps PRIVATE MeshAreaOps.cpp )

target_link_libraries( MeshAreaOps
    PUBLIC
        Amino::Cpp
        Bifrost::Object )
target_link_libraries( MeshAreaOps
    PRIVATE
        Amino::Core
        Bifrost::Math
        MeshArea )

bifrost_set_install_rpath(MeshAreaOps)
install( TARGETS MeshAreaOps DESTINATION lib )

# Generate and install the json files
set( headers_to_parse
    MeshAreaOps.h
)

bifrost_header_parser(
    MeshAreaOpsJson       # Name of the target.
    "json/${PROJECT_NAME}" # Install and build dirs - relative to install prefix
                           # and build directory
    HEADER_FILES ${headers_to_parse})

# Create config json file to load the bifrost pack
set( CONFIG_PACK_VERSION "${PROJECT_VERSION}")
set( CONFIG_PACK_NAME "MeshArea")
set( CONFIG_SHARED_LIBS "./lib")
set( CONFIG_JSON_FILES "./json/${PROJECT_NAME}")
set( config_json ${CMAKE_BINARY_DIR}/${PROJECT_NAME}PackConfig.json )
configure_file(PackConfig.json.in ${config_json} )
install(FILES ${config_json} DESTINATION . )
