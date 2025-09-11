#-
# ===========================================================================
# Copyright 2024 Autodesk, Inc. All rights reserved.
#
# Use of this software is subject to the terms of the Autodesk license
# agreement provided at the time of installation or download, or which
# otherwise accompanies this software in either electronic or hard copy form.
# ===========================================================================
#+
# MeshWeldUV library
add_library( MeshWeldUV SHARED )
target_compile_definitions( MeshWeldUV PRIVATE MESH_WELD_UV_BUILD_DLL )
target_sources( MeshWeldUV PRIVATE MeshWeldUV.cpp )
target_link_libraries( MeshWeldUV
    PUBLIC
        Amino::Core
        Bifrost::Object
        Bifrost::Math
        Bifrost::Geometry )
target_include_directories( MeshWeldUV PUBLIC $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include> )

bifrost_set_install_rpath(MeshWeldUV)
install( TARGETS MeshWeldUV
         EXPORT ${CMAKE_PROJECT_NAME}
         DESTINATION lib
         INCLUDES DESTINATION include )

install( DIRECTORY   include/
         DESTINATION include )

include(CMakePackageConfigHelpers)
write_basic_package_version_file(
    ${PROJECT_BINARY_DIR}/cmake/${CMAKE_PROJECT_NAME}ConfigVersion.cmake
    VERSION 0.1.0
    COMPATIBILITY AnyNewerVersion )

# Package for using the installed build
install(
    EXPORT      ${CMAKE_PROJECT_NAME}
    DESTINATION cmake
    FILE        ${CMAKE_PROJECT_NAME}Config.cmake)
install(
    FILES "${PROJECT_BINARY_DIR}/cmake/${CMAKE_PROJECT_NAME}ConfigVersion.cmake"
    DESTINATION cmake)
