# Building with CMake

You need CMake 3.20 and up.

Tested with :

* Microsoft Visual Studio Professional 2019
* XCode 13.4.1+ and MacOS (OSX) architecture arm64 and x86_64
* GNU 9.3.1+

Supporting C++17.

All examples can be built from this directory or each example can be built individually.

The following will go through Setup, CMake configure, CMake build and install, Running tests with CTest, Using the CMake install output.

# Setup
On all platforms, make sure that you have access to the platform's compiler:

    (Win)  open a Visual Studio 2019 x64 shell to set up the compiling environment.
    (Non Win) open a shell and make sure GCC (Linux) or XCode/clang (MacOS) are accessible.

For convenience, set the environment variable `BIFROST_LOCATION`.  The SDK directory is under `BIFROST_LOCATION/sdk`.

## `BIFROST_LOCATION` standard locations

    Windows C:\Program Files\Autodesk\Bifrost\<Maya_version>\<Bifrost_version>\bifrost\
    macOS   /Applications/Autodesk/bifrost/<Maya_version>/<Bifrost_version>/bifrost/
    Linux   /usr/autodesk/bifrost/<Maya_version>/<Bifrost_version>/bifrost/
    
    Note: On Windows, the path can contain spaces, but not quotation marks of any kind.


You can also pass the location of the Bifrost installation to `cmake` on the command line. The location passed to `cmake` from the command line will take precedence over the environment variable (See [CMake configure options](#bifrost-cmake-configure-options) ).

# CMake configure
if you want to make changes to the code, you can copy one example or all examples.  For simplicity, the rest of this document will assume that your source directory is an example's directory and it will be represented as `./`.  It is good practice to specify a build directory that is not in your source directory and it will be referred to as `path/to/build/dir` in the following instructions.  For example, your build directory could be in your home directory:

    (Win)     `path/to/build/dir` : %HOMEDRIVE%%HOMEPATH%/my_build_directory
    (Non Win) `path/to/build/dir` : ~/my_build_directory

Once in the SDK example directory, you can configure, build, and install with CMake.

    cmake -S ./ -B path/to/build/dir -DCMAKE_CXX_STANDARD=17

The build files will be created in the build location directory you passed to the `cmake` command.

`CMAKE_CXX_STANDARD` must be `17` or higher.  Bifrost is tested with C++17 only.

Bifrost for Maya 2024 and up ships as a set of universal binaries that support Apple Silicon (arm64) natively. If you need to build for a specific MacOS architecture you can pass to `cmake` the `CMAKE_OSX_ARCHITECTURES` option (See [CMake configure options](#bifrost-cmake-configure-options) ).

If you need to do a clean rebuild, delete the build directory first and rerun CMake configure.  This will reset all CMake cached variables.

## CMake generators
The CMake configure command above uses the platform's default CMake generator.  That is, no `-G` option is passed to CMake.

On Windows, the default generator is Visual Studio because we are in a `Visual Studio shell`.  On non-Windows, it is `make`.

### Windows
* Visual Studio is a a multi-configuration generator.
* `Debug or Release or ...` variant will need to be specified at build time.
* A Visual Studio solution is generated in your build directory.

### Linux
* Make is a single configuration generator.
* The default build variant is `Debug`.
* A Makefile is generated in your build directory.

### OSX
* Make is a single configuration generator.
* The default build variant is `Debug`.
* A Makefile is generated in your build directory.

### OSX Xcode
* To get an Xcode project the `Xcode` multi-configuration generator must be passed-in.

        cmake -GXcode -S ./ -B path/to/build/dir -DCMAKE_CXX_STANDARD=17

* An Xcode project is generated in your build directory.
* `Debug or Release or ...` variant will need to be specified at build time.

# CMake build and install

## Using CMake to build

### Multi-configuration CMake generators

    cmake --build path/to/build/dir --target install  --config Release

* The extra `--config` is because Visual Studio and XCode generators are multi-configuration generators.
* The default variant is `Debug` if `--config` is not specified.

### Single configuration CMake generators

* The default generator for Linux and MacOS is `make` and the default build variant generated at configure time is `Debug`

        cmake --build path/to/build/dir --target install

## Using the platform's tools to build
After CMake configure and depending on the CMake generator you can use the platform's tools to build and install instead of the CMake command line.

### Windows
* The default generator is Visual Studio.
* A solution file is generated in your build directory.
* Start Visual Studio with it.

### Linux
* The default generator is `make`.
* A `Makefile` is generated in your build directory.
* In a shell, run `make` on the `Makefile`.

### MacOS
#### Make
* The default generator is `make`.
* A `Makefile` is generated in your build directory.
* In a shell, run `make` on the `Makefile`.
#### Xcode
* XCode generator needs to be passed-in at configure time.
* An XCode project file is generated in your build directory.
* Start XCode with it.

# Running tests with CTest

CTest is used to run tests of examples that have built-in tests.
For examples that do not have built-in tests, manual testing can be done by directly using their install after the CMake install step (See [Using the output of CMake install](#using-the-cmake-install-output)).

The `ctest` command comes with your CMake package.  Testing is done on your build directory.

## Multi-configuration CMake generators

    ctest --test-dir path/to/build/dir -C Release -VV

* Option `-C` is necessary to specify the build type of your build.  It is preferable to always pass this option.
* Option `-VV` is for _very verbose_.

## Single configuration CMake generators

Simply run `ctest` on your build directory

    ctest --test-dir path/to/build/dir -VV

* The option `-VV` is for _very verbose_.

# Using the CMake install output
The install directory is named after the project's name and version.  The project is defined in the top CMakeLists.txt file of each directory.
For this directory, that builds all the examples, you will find in `CMakeLists.txt`:

    project(
        BifrostExamples
        VERSION 1.0.0
        LANGUAGES CXX
    )

The install directory will be, by default, `<your build directory>/BifrostExamples-1.0.0`.

Some examples generate executables, others produce Bifrost packs (Bifrost definition JSON files and libraries).

Instructions on how to run an example's generated executable are provided in the `README.md` file of the example's directory.

Examples that generate a Bifrost pack can be tested by loading them into applications that integrate Bifrost, like Autodesk Maya.  Each Bifrost pack has an associated `config file` that serves to load it.

## Bifrost config files
The install directory will contain one config file per example.  Config files are named after an example's project name and have the form  `<project_name>Config.json`, for example: `SimpleStringPackConfig.json`, `IndexSetPackConfig.json`, etc.

Add the full path of each config file to `BIFROST_LIB_CONFIG_FILES` environment variable. `BIFROST_LIB_CONFIG_FILES` can point to multiple config JSON files. Separate each path with a semicolon (`;`) on Windows, or a colon (`:`) on macOS or Linux.

    (Win) BIFROST_LIB_CONFIG_FILES=<your install directory>/SimpleStringPackConfig.json;<your install directory>/IndexSetPackConfig.json
    (Non Win) BIFROST_LIB_CONFIG_FILES=<your install directory>/SimpleStringPackConfig.json:<your install directory>/IndexSetPackConfig.json

If you will be using your nodes with the Bifrost Extension for Maya, you can also set this environment variable in the `Maya.env` file.

Start Maya... Your Bifrost packs will be accessible from the Bifrost graph editor.

# Bifrost CMake configure options
Additional CMake options are available and can be set on the CMake command line to override Bifrost's CMake behavior.

The Bifrost CMake options are controlled by `BIFROST_LOCATION`, `CMAKE_CXX_STANDARD` `CMAKE_INSTALL_PREFIX`, `BIFROST_WARNINGS_AS_ERRORS`.

| Parameter              | Default                      | Command line option to change the default |
| ---------------------- | ---------------------------- | ------------------------- |
| C++ standard           | your compiler's default      | `-DCMAKE_CXX_STANDARD=17` |
| Bifrost location       | `BIFROST_LOCATION` env. var. | `-DBIFROST_LOCATION=<path_to_Bifrost_installation>` |
| Activate warnings      | Default is `OFF`             | `-DBIFROST_WARNINGS_AS_ERRORS=<ON or OFF>` |
| Pack install directory | Build directory              | `-DCMAKE_INSTALL_PREFIX=<target_directory>` |

If you are using MacOS on a machine with an Apple Silicon chip, the default output is `arm64` code.

The `CMAKE_OSX_ARCHITECTURES` option can be used to select the output architecture. Set it to `arm64` for Apple Silicon, `x86_64` for Intel, or `arm64;x86_64` for universal binaries.
  
    cmake  -S  <operator_directory>  -B <build_location> -DCMAKE_OSX_ARCHITECTURES="arm64"
    cmake  -S  <operator_directory>  -B <build_location> -DCMAKE_OSX_ARCHITECTURES="x86_64"
    cmake  -S  <operator_directory>  -B <build_location> -DCMAKE_OSX_ARCHITECTURES="arm64;x86_64"
