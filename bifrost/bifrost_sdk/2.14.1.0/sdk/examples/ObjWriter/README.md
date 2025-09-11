# Description

Based on the [.OBJ file format](https://en.wikipedia.org/wiki/Wavefront_.obj_file), this example shows how to implement a simple .OBJ file writer using the Bifrost SDK.

The Amino operator outputs a simple .OBJ file from an input Bifrost mesh. It supports:
 * Writings points.
 * Writing faces.
 * Writing face vertex normals or point normals, if present.
 * Writing face vertex UVs, if present.

The Bifrost Geometry section of Bifrost's on-line [Developer Help section](https://help.autodesk.com/view/BIFROST/ENU) provides more details about the Bifrost Geometry data structure.

# Building the example with CMake
Directions on how to build this example can be found in the [sdk/examples/README.md file](../README.md) of your Bifrost installation.
