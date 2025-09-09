# `Print Point Properties`
Prints a multiline object property information at the point position.<br>
The properties to be displayed are chosen by just listing the names. Short display names are optional.<br>
Colors are optional.

## Inputs

### `Object`
The object to be inspected.

### `Properties`
A comma separated list of object properties that are to be displayed.<br>
The order counts.

### `Display Names`
Optional short names just for the display.<br>
Comma separated list in the same order as "Properties".

### `Name Value Separator`
Separator between names and values.<br>
Usually something like " = " or ": "

### `Orientation in Degrees`
Converts the float4 point_orientation to Euler degrees.

### `Show Point ID`
Displays the ID of the point as the first line.

### `Use Point Color`
Uses the point_color to colot the text.
Has no effect if the object has no point_color.

## Layout

### `Line Space`
Height of a line.

### `Float Precision`
Controls the number of decimal places in float to string conversion.<br>
Enter ONLY values in the power of ten = 10, 100, 1000, etc.

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
<br>

### `Camera`
A matrix for the aim-at feature.<br>
This will just copy the ORIENTATION of the camera to the printed text so that the text is always facing the camera.


## Tutorial

https://youtu.be/6lsu-Nk6zJs
<br><br>

