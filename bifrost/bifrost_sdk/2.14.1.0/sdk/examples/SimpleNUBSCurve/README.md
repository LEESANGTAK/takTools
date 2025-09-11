# Description
This is a simple NUBS (Non Uniform BSpline) curve example using the Bifrost Geometry APIs.

Note that we did not implement rational BSplines, thus the term NUBS instead of NURBS.

In this example a Bifrost strand's positions are used as control points for simple clamped NUBS curves.

The knot data are added to a strand  using Bifrost Geometry's Component and Data Geo Properties.

The Bifrost Geometry section of Bifrost's on-line [Developer Help section](https://help.autodesk.com/view/BIFROST/ENU) provides more details about the Bifrost Geometry data structure.

# Building the example with CMake
Directions on how to build this example can be found in the [sdk/examples/README.md file](../README.md) of your Bifrost installation.
