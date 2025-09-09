# `Print Array`
Prints the start and end part of an array as a strand object in 3D.
A header will be printed that contains a description, the type of the array, the number of elements and min/max information.

## Inputs

### `Description`
First line of the printed description.

### `Array`
The input array can be of these types: all integers, float, double, float3, float4, boolean, string.
All other types will be ignored.
Support for additional types needs to be done in the compounds "any_to_string" and "array_info_string".

### `Offset`
Offset from the start of the array.
<br>This is useful for very large arrays if you need to see values other that start and end.
<br>Use together with "number_of_lines" and "number_of_columns" to restrict the total number of values displayed.


## Layout

### `Columns`
Number of characters in a line. If the text is longer, it is simply wrapped (no word wrap).

### `Number of Lines`
Number of lines in one column of text.

### `Line Space`
Height of a line.

### `Number of Columns`
Number of columns for each the start and the end of the array.

### `Horizontal Gap`
The gap between the header and the array.

### `Vertical Gap`
The distance between the text columns.

### `Float Precision`
Controls the number of decimal places in float to string conversion.<br>
Enter ONLY values in the power of ten = 10, 100, 1000, etc.

### `Colored Indices`
Prints the indices of the table in the color of the header (Font->Line Color).<br>
If you turn this off, printing large arrays will be around 30% faster.

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

## Columns

### `Print Start of Array`
Whether to print the beginning of the array.

### `Color Start`
Color for the start part of the array.

### `Print End of Array`
Whether to print the end of the array.

### `Color End`
Color for the end part of the array.

## Transform

### `Transform`
A matrix for the transformation.

### `Translate`
### `Rotate`
### `Scale`
Additional transform if there's no matrix available.
<br>


## Tutorial

https://youtu.be/6lsu-Nk6zJs
<br><br>

