# `Four Values to String`
This compund helps putting print strings together.
It offers 4 slots of "Description" and "Value"

## Inputs

### `Description`
Text description for the connected value.
<br><b>IMPORTANT</b>: the description/value pair will not be printed, if both values are empty/disconnected.

### `Value`
Any type of value.
<br>accepted types are scalar values, vectors, boolean, string <b><u>and arrays</u></b>.
<br>Support for additional types needs to be done in the compounds "any_to_string" and ""any_array_to_string"".

### `Float Precision`
Precision when converting floating point numbers

### `Separator`
Separate all strings with this string.
<br>Use ", " or "\n" or whatever looks good.
<br>Default is "\n" to create a new line for every string.

### `Auto Feed`
Adds another "\n" (newline) at the end of the the output string.

### `Prefix Description`
A string that is inserted at the start of each "Description" string.<br>
Just to simplify the use.

### `Prefix Value`
A string that is inserted at the start of each "Value" string.<br>
Just to simplify the use.<br>
Example: " = " will display an equal sign between description and value.

### Offset
If an array is plugged in then this is the offset from the start of the array.

### Max String Length
If an array is plugged in then this is the max number of characters displayed (incl. commas, spaces)

## Outputs

### `Joined`
String

<br>


## Tutorial

https://youtu.be/6lsu-Nk6zJs
<br><br>
