# `Array Info String`
Helper for text functions.
Converts an array of any type to a string array.
Outputs also a "type" string and an "info" string.


## Inputs

### `Float Precision`
Precision when converting floats, doubles, float3 and float4

### `Array`
The input array can be of these types: all integers, float, double, float3, float4, boolean, string.
All other types will be ignored.
Support for additional types needs to be done in the compounds "any_to_string" and "array_info_string".

## Outputs

### `String Array`
The converted array.

### `Type`
A string that describes the type of the input value.

### `Info String`
For numerical values this will be the "array_bounds" in the form of "Min: xxx, Max: xxx".
For strings it will return "Min Length: xxx, Max Length: xxx".
<br>


## Tutorial

https://youtu.be/6lsu-Nk6zJs
<br><br>
