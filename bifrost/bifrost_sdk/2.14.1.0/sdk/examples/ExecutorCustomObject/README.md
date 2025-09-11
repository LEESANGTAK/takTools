# ExecutorCustomObject example

This example is a command line application that shows how to execute a graph with a custom type (C++ user type).

It uses the Amino cpp2json tool (See [CMakeLists.txt](src/CMakeLists.txt))
to process a c++ file ([ExecutorCustomObject.h](src/ExecutorCustomObject.h)) which contains
a user type ([BoundingBox](src/ExecutorCustomObject.h)) to generate a json file
which will be loaded in bifrost. The generated json file contains the translated c++ type.

This example executes a graph defined in [TranslateBoundingBox.json](src/TranslateBoundingBox.json) which uses the custom type as the input value.
The graph does some computations and outputs the transformed custom type as the
output value.

## How to execute

ExecutorCustomObject is a command line example. To execute it, you need to pass arguments on the command line.\
On Windows, you also need to add the paths to your Bifrost libraries (dll) to your PATH environment variable.

- Windows

    If you have used Visual Studio as a CMake generator, you can start the application from Visual Studio
    without any configuration. Otherwise, you can use this batch script to run the example.

    Note: You need to change `<your_bifrost_installation_path>`, `<your_bifrost_examples_installation_path>` and `<usd_version>` with your own values.

    ```bat
    @echo off
    setlocal

    rem The location where Bifrost is installed (ex: C:\Program Files\Autodesk\Bifrost\Maya2025\2.10.0.0\bifrost).
    set BIFROST_LOCATION=<your_bifrost_installation_path>

    set PATH=%PATH%;%BIFROST_LOCATION%/bin
    set PATH=%PATH%;%BIFROST_LOCATION%/thirdparty/bin

    rem replace <usd_version> with your USD version provided with your Bifrost installation.
    set PATH=%PATH%;%BIFROST_LOCATION%/packs/usd_pack/<usd_version>/thirdparty/bin

    rem This is the path where the examples are insatalled (CMAKE_INSTALL_PREFIX).
    rem If you are building all examples, the path will be <my_build_directory>/BifrostExamples-x.x.x by default
    rem (ex: c:/build-sdk-examples/BifrostExamples-1.0.0).
    rem If you are building only ExecutorCustomObject, the path will be <my_build_directory>/ExecutorCustomObject-x.x.x by default
    rem (ex: c:/build-executorCustomObject/ExecutorCustomObject-1.0.0).
    set INSTALL_LOCATION=<your_bifrost_examples_installation_path>

    rem This command assumes you are executing executor_custom_object from the CMake install tree.
    rem If you are executing executor_custom_object from the CMake build tree, you will need to adjust the
    rem command.
    "%INSTALL_LOCATION%/bin/executor_custom_object.exe" ^
        --config-file "%BIFROST_LOCATION%/resources/standalone_config.json" ^
        --config-file "%BIFROST_LOCATION%/packs/packs_standalone_config.json" ^
        --config-file "%INSTALL_LOCATION%/ExecutorCustomObjectPackConfig.json" ^
        --definition-file "%BIFROST_LOCATION%/sdk/examples/ExecutorCustomObject/src/TranslateBoundingBox.json" ^
        --graph-name Examples::SDK::TranslateBoundingBox

    endlocal
    ```

- Linux and OSX

    Your can use this Bash script to run the example.\
    Note: You need to change `<your_bifrost_installation_path>` and `<your_bifrost_examples_installation_path>` with your own values.

    ```bash
    #!/bin/bash

    # The location where Bifrost is installed (ex: /usr/autodesk/bifrost/maya2025/2.10.0.0/bifrost).
    BIFROST_LOCATION=<your_bifrost_installation_path>

    # The path where the examples are insatalled (CMAKE_INSTALL_PREFIX).
    # If you are building all examples, the path will be <my_build_directory>/BifrostExamples-x.x.x by default
    # (ex: /build-sdk-examples/BifrostExamples-1.0.0).
    # If you are building only ExecutorCustomObject, the path will be <my_build_directory>/ExecutorCustomObject-x.x.x by default
    # (ex: /build-executorCustomObject/ExecutorCustomObject-1.0.0).
    INSTALL_LOCATION=<your_bifrost_examples_installation_path>

    # This command assume you are executing executor_custom_object from the CMake install tree.
    # If you are executing executor_custom_object from the CMake build tree, you will need to adjust the
    # command.
    $INSTALL_LOCATION/bin/executor_custom_object \
        --config-file $BIFROST_LOCATION/resources/standalone_config.json \
        --config-file $BIFROST_LOCATION/packs/packs_standalone_config.json \
        --config-file $INSTALL_LOCATION/ExecutorCustomObjectPackConfig.json \
        --definition-file $BIFROST_LOCATION/sdk/examples/ExecutorCustomObject/src/TranslateBoundingBox.json \
        --graph-name Examples::SDK::TranslateBoundingBox
    ```
