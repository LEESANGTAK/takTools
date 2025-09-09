# `Auto Layout`
This node will automatically place 2D (x,y) panels with 4 different layouts.<br>
The goal is to have the printed panels side by side and not to have to move them around individually.


## Inputs

### `Panels`
Any kind of "panel", usually the output of the print nodes.

### `Stacking Method`
There are four different methods for the layout:
- **Auto**: tries to place all panels in a rectangle (see also "Auto Layout WH Ratio").
- **Along X**: horizontal layout
- **Along Y**: vertical layout
- **Quadrants**: layout around the origin for up to four panels

### `Auto Layout WH Ratio`
Ratio of the rectangle in "Auto" layout.<br>
Values <1 stretch the rectangle in X, values >1 stretch it in Y.

### `Distance`
Distance between the panels.

### `Placement Type`
Placement of the resulting layout around the origin.<br>
Has no effect for the "Quadrants" layout.

### `Draw Frames`
Draws a frame around every panel.

### `Translate/Rotate/Scale`
Additional translation.

### `Shift Order`
Positive values will shift the order of the panels right/down/clockwise.<br>
Negative values will REVERSE the order and shift left/up/counter clockwise.<br>
Has no effect when "Stacking Method" is set to "Auto".


## Outputs

### `Auto Layout`
The resulting layout.<br>
The panels can be displayed using the "D" terminal switch.<br>


<br>


## Tutorial

https://youtu.be/6lsu-Nk6zJs
<br><br>
