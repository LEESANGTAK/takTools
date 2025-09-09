# `Highlight Array Elements`
Helper to highlight array elements in lists.
Converts an array of any type to a string array and adds commands to chosen elements.<br>
Elements can be chosen with a boolean array.


## Inputs

### `Highlight elements`
Boolean array to choose which elements are surrounded by the commands in "Prefix" and "Postfix".

### `Array`
The input array can be of these types: all integers, float(2/3/4), double(2/3/4), boolean, string.
All other types will be ignored.
Support for additional types needs to be done in the compounds "any_to_string" and "array_info_string".

### `Prefix`
The string that is inserted at the beginning of selected elements.
This should be a command that formats or colors the element.

### `Postfix`
The string that is appended to selected elements.
This should be a command to reset the formatting/coloring.

### `Float Precision`
Precision when converting floats, doubles, float2, float3 and float4.

### `Max Elements`
Max number of array elements that are processed.<br>
A large number of elements will slow down the printing.



<br>


## Tutorial

https://youtu.be/6lsu-Nk6zJs
<br><br>
