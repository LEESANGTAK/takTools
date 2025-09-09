# `Print`
This is a simplified combo of the nodes **print_static** and **print_table**.<br>


## Inputs

## Values

### `Description 1-4`
### `Value 1-4`
Four pairs of description and values.<br>

**NEW**: You can also plug in small arrays that will be displayed in a line

### `Array Offset`
If an array is plugged in then this is the offset from the start of the array.

### `Max String Length`
If an array is plugged in then this is the max number of characters displayed (incl. commas, spaces)

### `Separator`
This string is placed between the description-value pairs.
By default it is a "\n" which stands for a newline. 

### `Input Strings`
Strings or arrays of strings. To print numerical value you simply convert them to strings (you should try "print_to_string").
The node will display this text as strands in 3D.
The strings are automatically separated by the string in the attribute "separator", e.g. ", " or "\n" for a new line
When it finds newlines the function shifts the text upwards to make space for new lines.

## Arrays

### `Description 1-4`
Description for the respective column.

### `Array 1-4`
The input arrays can be of these types: all integers, float, double, float2, float3, float4, boolean, string.
All other types will be ignored.
Support for additional types needs to be done in the compounds "any_to_string" and "array_info_string".

### `Index Color`
The color of the index in the array table.

### `Colored Lines`
Display the data lines in varying colors to make it easier to follow a line.

## Object

### `Object Dump`
Connect a single object here to see an "Object Dump" print.
This will list all properties and sub-objects.
For more information and more display options see "print_object_dump".

### `Object Properties`
Connect a single object to print all its properties as a table.
For more information and more display options see "print_object_properties".

## Settings

### `Text Color`
The color of the text.

### `Column Width`
Number of characters in a line (Fast Engine) or total column width (Rich Engine).</br>
If the text is longer, it is simply wrapped (no word wrap).

### `Float Precision`
Controls the number of decimal places in float to string conversion.<br>
Enter ONLY values in the power of ten = 10, 100, 1000, etc.

### `Obj Prop Expression`
Space separated list of filter expressions for the print of "object_dump" and "object_properties".<br>
Expression can contain asterisks as wildcard.<br>
Precede an expression with a wildcard to exclude matching properties from the display.<br>
For more information see  "object_dump" and "object_properties".


### `Table Offset`
The values of the arrays in the tables "Array" and "Object Properties" are listed starting from this index.<br>
This can be used to "scroll" through long arrays.

### `Table Number of Lines`
Total number of lines to display in the tables "Array" and "Object Properties".<br>
The columns can be shorter if there are less values in an array.

### `Object Dump Data`
Number of data elements that are displayed in "Object Dump".<br>
This is similar to the "Detail" setting in the node "object_dump".

## Transform

### `Translate`
### `Rotate`
### `Scale`
Transformation on top of the "Auto Arrangement" (see below).

## Auto Arrange

### `Stacking Method`
In the default setting "Quadrants" the Print node will automatically arrange all panels (values, array table, object dump, object property table) aroud the origin.<br>
The setting "Auto" will try to place everything in a rectangle.<br>
"Along X" and "Along Y" are self-explanatory.<br>

### `Auto Stack WH Ratio`
Width-height ratio for the "Auto" stacking.

### `Spacing`
Distance between the panels.

### `Draw Frames`
Draw a frame around the panels.

### `Placement`
Placement around the origin for the stacking types "Auto", "Along X" and "Along Y".<br>
"Quadrants" is always around the origin.

### `Shift Order`
Positive values will shift the order of the panels right/down/clockwise.<br>
Negative values will REVERSE the order (-1) and then shift left/up/counter-clockwise.<br>
Has no effect when "Stacking Method" is set to "Auto".


## Tutorial

https://youtu.be/6lsu-Nk6zJs
<br><br>


