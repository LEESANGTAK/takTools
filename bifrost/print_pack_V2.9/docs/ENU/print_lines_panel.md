# `Print Lines Panel`
Prints given strings as strands objects and spreads them out as a panel of text.
Outputs the lines as an array and also as a merged object.
Input strings will be joined by "separator" and then split at "\n".

## Inputs

### `Input Strings`
Array of strings. To print numerical values you simply convert them to strings (you should try "value_to_string" or "four_values_to_string").
The strings are automatically joined with the string in the attribute "separator", e.g. ", " or "\n" for a new line

### `Columns`
Number of characters in a line. If the text is longer, it is simply wrapped (no word wrap).

### `Kerning`
Space between the characters.

### `Font Size`
Overall size of the font.

### `Separator`
Join all incoming strings with this string.
Use ", " or "\n" or whatever looks good.

### `X Shift`
If printing columns of text then this value is the X position of the text.

### `Y Shift`
Moves the text in Y.

### `Positive Y`
When on the textblock is placed in positive Y, the bottom of the last line is at Y=0.
When off the textblock is placed in negative Y, the top of the first line is at Y=0.

### `Paths`
### `Sizes`
### `Offsets`
Font data from the node "line_font_data".


<br>


## Tutorial

https://youtu.be/6lsu-Nk6zJs
<br><br>



