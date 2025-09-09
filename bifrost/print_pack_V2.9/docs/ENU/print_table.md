# `Print Table`
Prints a nice table from up to four arrays.<br>


## Inputs

### `Description 1-4`
Description for the respective column.

### `Array 1-4`
The input arrays can be of these types: all integers, float, double, float2, float3, float4, boolean, string.
All other types will be ignored.
Support for additional types needs to be done in the compounds "any_to_string" and "array_info_string".

### `Offset`
The values of the arrays are listed starting from this index.<br>
This can be used to "scroll" through long arrays.

### `Number of Lines`
Total number of lines to display.<br>
The columns can be shorter if there are less values in an array.

### `Display Array Sizes`
Displays the array size after its description.

## Highlight Lines

### Highlight Lines
Boolean array that defines which lines (elements in all columns) will be highlighted.<br>
Ideally this array should be large enough to define the highlight for all lines of the table.<br>
If the array is empty then no highlighting is done.

### Prefix
This string will be inserted before each highlighted element.<br>
The string should turn ON the highlight formatting. By default it is set to "\cq3" (quick color #3 = red).

### Postfix
This string is appended after the highlighted element.<br>
The string should turn OFF the highlight formatting. By default it is set to "\cd" (default color).

## Layout

### `Column Width`
Number of characters in a line (Fast Engine) or total column width (Rich Engine).<br>
If the text is longer, it is simply wrapped (no word wrap).

### `Line Space`
Height of a line.

### `Float Precision`
Precision when converting floats, doubles, float2, float3 and float4.

### `Vertical Column Spacing`
Space between the columns.

### `Colored Lines`
Displays each line of data in a different color, so that it is easier to follow a line across the columns.

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

### `Transform`
A matrix for the transformation.

### `Translate`
### `Rotate`
### `Scale`
Additional transform if there's no matrix available.

### `Camera`
A matrix for the aim-at feature.<br>
This will just copy the ORIENTATION of the camera to the printed text so that the text is always facing the camera.

<br>

## Tutorial

https://youtu.be/6lsu-Nk6zJs
<br><br>

