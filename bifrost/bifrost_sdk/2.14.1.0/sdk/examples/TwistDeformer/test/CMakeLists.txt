#-
# ===========================================================================
# Copyright 2024 Autodesk, Inc. All rights reserved.
#
# Use of this software is subject to the terms of the Autodesk license
# agreement provided at the time of installation or download, or which
# otherwise accompanies this software in either electronic or hard copy form.
# ===========================================================================
#+

add_executable( TestTwistDeformer TestTwistDeformer.cpp )
target_link_libraries( TestTwistDeformer
    PRIVATE
        GTest::gtest_main
        TwistDeformer
        Amino::Core
        Bifrost::Math )
add_test( NAME Geom-TestTwistDeformer COMMAND TestTwistDeformer )

if( CMAKE_SYSTEM_NAME STREQUAL "Windows" )
    get_target_property( dependency_path TwistDeformer BINARY_DIR )
    if( CMAKE_CONFIGURATION_TYPES )
        set( dependency_path ${dependency_path}/$<CONFIG>)
    endif()

    set( shared_lib_dirs
        ${BIFROST_LOCATION}/bin
        ${BIFROST_LOCATION}/thirdparty/bin
        ${dependency_path})

    bifrost_convert_to_env_var_list( INPUT_LIST ${shared_lib_dirs} OUTPUT_VAR native_env_var_lib_dirs)
    set_tests_properties(Geom-TestTwistDeformer PROPERTIES ENVIRONMENT "PATH=${native_env_var_lib_dirs}" )
endif()
