#-
# ===========================================================================
# Copyright 2024 Autodesk, Inc. All rights reserved.
#
# Use of this software is subject to the terms of the Autodesk license
# agreement provided at the time of installation or download, or which
# otherwise accompanies this software in either electronic or hard copy form.
# ===========================================================================
#+
# TwistDeformer library
add_library( TwistDeformer SHARED )
target_compile_definitions( TwistDeformer PRIVATE TWIST_DEFORMER_BUILD_DLL )
target_sources( TwistDeformer PRIVATE TwistDeformer.cpp )
target_link_libraries( TwistDeformer
    PUBLIC
        Amino::Core
        Bifrost::Object
        Bifrost::Math
        Bifrost::Geometry )
target_include_directories( TwistDeformer PUBLIC $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include> )

bifrost_set_install_rpath(TwistDeformer)
install( TARGETS TwistDeformer
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
