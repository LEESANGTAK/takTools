#-
# ===========================================================================
# Copyright 2024 Autodesk, Inc. All rights reserved.
#
# Use of this software is subject to the terms of the Autodesk license
# agreement provided at the time of installation or download, or which
# otherwise accompanies this software in either electronic or hard copy form.
# ===========================================================================
#+

set( graph_dir_names
    associative_left_to_right
    associative_right_to_left
    binary_left_to_right
    binary_right_to_left    )

install(DIRECTORY ${graph_dir_names}
    DESTINATION "./json/${PROJECT_NAME}/graphs")
