# `Print Points`
Prints per-point information at per-point positions.

## Inputs

### `Point Values`
The information to print.
The input array can be of these types: all integers, float, double, float3, float4, boolean, string.
All other types will be ignored.
Support for additional types needs to be done in the compounds "any_to_string" and "array_info_string".

### `Point Positions`
Positions where the information is printed.

### `Point Colors`
Optional per-point colors for the printed information.
If this array is not connected or does not have the same size as "point_positions", then "line_color" is used.

## Layout

### `Float Precision`
Controls the number of decimal places in float to string conversion.<br>
Enter ONLY values in the power of ten = 10, 100, 1000, etc.

### `Rich Text`
Selects the "Rich Engine" for printing which is a bit slower than the "Fast Engine" but allows for more formatting.


## Font

### `Line Width`
Width of the lines.
Used only when "shape" is set to "ribbon".

### `Line Color`
The color of the text.

### `Shape`
Set to "wire" or "ribbon".
"Ribbon" reacts to "line_thickness".

### `Kerning`
Space between the characters.

### `Font Size`
Overall size of the font.

## Transform

### `Offset`
### `Rotate`
### `Scale`
Transform to offset the printed information from the data points.

## Point Selection

### `Filter Field`
Where the field is 0 no point info is displayed.
Use a "Manipulator Field" do do this.

### `Dropout`
Skips the display of this this number of points.
This is used to thin out very dense point clouds.

### `Dropout Offset`
Shifts the displayed points by this number.
In case you need to see a specific point.

### `Max Points`
Max number of points that will be displayed.

<br>


## Tutorial

https://youtu.be/6lsu-Nk6zJs
<br><br>

