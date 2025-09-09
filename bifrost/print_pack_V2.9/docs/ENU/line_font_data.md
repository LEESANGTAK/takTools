# `Line Font Data`
Contains the data of the line font for printing in Bifrost.
The font is "Hershey Simplex" and was provided by Paul Bourke.
http://paulbourke.net/dataformats/hershey/
In the node there's a second font that is a bit simpler but not as nice.
It is a font from the HP 1345 and it was provided by Poul-Henning Kamp.
http://phk.freebsd.dk/hacks/Wargames/

The node has feedback ports in order to store the font data once it is converted from its string data.

## Inputs

### `Font Size`
Default should be 1

### `Space Size`
The size of a space character.
Default is 5.245

### `Font Pre-scale`
A pre-scale factor to adapt other fonts with different sizes.
Default for Hershey is 0.04

### `Is First Eval`
Should be ON by default so that the font data gets converted during the first evaluation.

## Outputs

### `Paths`
### `Sizes`
### `Offsets`
Paths are x-y positions of the strands.
Offsets is the array of offsets for each character.
That makes it very easy to create the strands for one character.

Sizes are the x-y size for each character.


<br>


## Tutorial

https://youtu.be/6lsu-Nk6zJs
<br><br>

