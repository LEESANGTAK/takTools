# `Print Object Properties`
Prints all properties of the object as a nice table.<br>


## Inputs

### `Object`
The object.

### `Offset`
The values of the properties are listed starting from this index.<br>
This can be used to "scroll" through long lists of values.

### `Number of Lines`
Total number of lines to display.<br>
The columns can be shorter if there are less values in a property.

### `Properties Expression`
Space separated list of expressions to choose which properties are displayed.<br>
The asterisk (**\***) is a wildcard (e.g. **\*** displays ALL properties, while **\*point\*** displays only those properties that have "point" in their name)<br>
An exclamation mark (**!**) at the start of an expression will exclude these matches.<br>
Example: **face\* !\*index\*** will list all properties that start with "face" but will exclude all that contain "index".

### `Display Array Sizes`
Displays the array size of the propertiy after its name.

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

### `Columns`
Number of characters in a line. If the text is longer, it is simply wrapped (no word wrap).

### `Line Space`
Height of a line.

### `Float Precision`
Controls the number of decimal places in float to string conversion.<br>
Enter ONLY values in the power of ten = 10, 100, 1000, etc.

### `X Gap`
Size of the gapp between the columns.

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
<br>
### `Point Indices`
Simple point labels for the point ID can be desplayed by turning on the "Proxy" flag of the terminal.<br>
In this group you find some settings for the point labels.<br>
There is a "print_points" node built in.<br>
If you like more complex point labels use "print_point_properties".


## Tutorial

https://youtu.be/6lsu-Nk6zJs
<br><br>

