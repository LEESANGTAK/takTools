# `Print Object Dump`
Prints information about the connected object.<br>
The information contains all sub objects and their values - it is basically a "dump_object" directly on the screen.

## Inputs

### `Object`
The object.

### `Properties Expression`
Space separated list of expressions to choose which properties are displayed.<br>
The asterisk (**\***) is a wildcard (e.g. **\*** displays ALL properties, while **\*point\*** displays only those properties that have "point" in their name)<br>
An exclamation mark (**!**) at the start of an expression will exclude these matches.<br>
Example: **\* !xyz\*** will list ALL properties but will exclude all names that start with "xyz" and all of their children.<br>

### `Hierarchy Level`
This will collapse all sub-objects deeper than "Hierarchy Level".
A "Detail Level" of 0 means that only the direct sub-object names are visible.<br>
Try it out. Its great for a clearer view.<br>
Default is 255 to show all levels.


### `Mute Object Arrays`
Arrays of large sub objects can be very distracting.<br>
This will mute (collapse) only those object arrays.<br>


### `Color Level`
Displays random colors for all objects at this level of the hierarchy.<br>
This helps to highlight the extent of objects in a confusing hierarchy.


### `Color All Levels`
Displays random colors for ALL objects, regardless of their hierarchy level.<br>


### `Display Data Elements`
Number of data fields to process.<br>
Objects with very large data fields (e.g. points) make the compound slow.<br>
Keep this setting low unless you need to see more data.<br>
You can also filter the field "data" from being displayed.<br>
Use "print_object_properties" to better see the data.

### `Indent Size`
Size of the indentation for each new level.

## Highlight Values

### Prefix
A formatting command to START the highlighting of the property values (e.g. "\cq3").

### Postfix
A formatting command to END the highlighting of the property values (e.g. "cp").

## Layout

### `Cutoff`
Number of characters in a line. If the text is longer, it is simply cut.

### `Line Space`
Height of a line.

### `Draw Frame`
Draws a Frame.

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

### `Camera`
A matrix for the aim-at feature.<br>
This will just copy the ORIENTATION of the camera to the printed text so that the text is always facing the camera.

<br>


## Tutorial

https://youtu.be/6lsu-Nk6zJs
<br><br>

