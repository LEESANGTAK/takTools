# `Print Static`
Prints given strings as a strands object.

## Inputs

## Four Values

### `Description 1-4`
### `Value 1-4`
Four pairs of description and values.<br>

### `Float Precision`
Controls the number of decimal places in float to string conversion.<br>
Enter ONLY values in the power of ten = 10, 100, 1000, etc.

### `Separator`
This string is placed between the description-value pairs.
By default it is a "\n" which stands for a newline. 

### `Prefix Description`
A string that is inserted at the start of each "Description" string.<br>
Just to simplify the use.

### `Prefix Value`
A string that is inserted at the start of each "Value" string.<br>
Just to simplify the use.<br>
Example: " = " will display an equal sign between description and value.

### Array Offset
If an array is plugged in then this is the offset from the start of the array.

### Max String Length
If an array is plugged in then this is the max number of characters displayed (incl. commas, spaces)

## Input Strings

### `Input Strings`
Strings or arrays of strings. To print numerical value you simply convert them to strings (you should try "value_to_string" and "four_values_to_string").
The node will display this text as strands in 3D.
The strings are automatically separated by the string in the attribute "separator", e.g. ", " or "\n" for a new line
When it finds newlines the function shifts the text upwards to make space for new lines.

## Layout

### `Column Width`
Number of characters in a line (Fast Engine) or total column width (Rich Engine).</br>
If the text is longer, it is simply wrapped (no word wrap).

### `Line Space`
Height of a line.

### `Draw Frame`
Draws a frame around the text.

### `Scroll upwards`
With this option on the text is scriooled upwards, so that the last line printed is close to the origin.<br>
If this is off then the first line is close to the origin and all other text is added below.<br>

### `Rich Text`
Selects the "Rich Engine" for printing which is a bit slower than the "Fast Engine" but allows for more formatting.

### `Tab Size`
Size of a tab stop ("\t").<br>
Tab stops work only with the "Rich Engine" (see "Rich Text").

### `Max Character Limit`
Maximum number of characters.<br>
This is just for safety to prevent lock-up of Bifrost.<br>
Adjust is needed.
<br>

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
Additional transform if there's no matrix avalable


### `Separator`
Separate all incoming strings with this string.
Use ", " or "\n" or whatever looks good.

<br>


## Tutorial

https://youtu.be/6lsu-Nk6zJs
<br><br>


