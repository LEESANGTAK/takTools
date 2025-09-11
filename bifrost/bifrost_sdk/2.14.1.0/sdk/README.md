# Getting Started
SDK tutorials can be found at https://help.autodesk.com/view/BIFROST/ENU/ under `Bifrost Developer Help`.

# CMake Files
The following complements the tutorials' quick overview of the CMake directory content.

The directory `bifrost/sdk/cmake` contains CMake files that provide tools and targets to build Bifrost operators, packs, and applications.

## Setup
The environment variable `BIFROST_LOCATION` should be defined and the Bifrost CMake `setup.cmake` file should be included first. The CMake `find_package` for Bifrost can then be called.

The `CMakeLists.txt` file of each example directory found under `./examples` shows the set-up sequence.  For example `./examples/SimpleString/CMakeLists.txt` starts with:

```
  # BIFROST_LOCATION must be passed-in or defined by an environment variable.
  # Passed-in on the CMake command line overrides the environment variable.
  if( NOT BIFROST_LOCATION )
      if( DEFINED ENV{BIFROST_LOCATION} )
          set( BIFROST_LOCATION $ENV{BIFROST_LOCATION})
      else()
          message( FATAL_ERROR "Bifrost: BIFROST_LOCATION cmake variable must be defined.")
      endif()
  endif()

  # Project Name
  project(
      SimpleString
      VERSION 1.0.0
      LANGUAGES CXX
  )

  # Bifrost setup and utilities...
  include(${BIFROST_LOCATION}/sdk/cmake/setup.cmake)

  # Verbose CMake
  set( CMAKE_VERBOSE_MAKEFILE TRUE)

  # Find Bifrost
  find_package(Bifrost REQUIRED SDK)
```

## CMake Options
The following CMake options are useful when using the Bifrost SDK:
* `BIFROST_LOCATION`(mandatory): The location of the Bifrost SDK.  This can be set as an environment variable or passed-in on the CMake command line.

* `CMAKE_CXX_STANDARD`(should be set): The C++ standard to use (at least C++17). Bifrost is tested with C++17. It should be set on the CMake command line.

* `BIFROST_WARNINGS_AS_ERRORS`: `OFF` by default. If set to `ON`, a set warnings will be treated as errors.
   Consult the file `./cmake/bifrost_warnings_as_errors.cmake` for details. This can be set as an environment variable or passed-in on the CMake command line.

More information on setting up can be found in the [`./examples/README.md`](./examples/README.md)

## CMake Targets
The `find_package(Bifrost REQUIRED SDK)` CMake statement will define a set of targets.

The CMake module file `./cmake/FindBifrost.cmake` is executed and will pull-in the files that define the targets.

* The SDK (host agnostic) targets are listed in the file `./cmake/internal/FindBifrostSDK.cmake`.
* The Maya related targets are listed in the file `./cmake/internal/FindBifrostMaya.cmake`.
