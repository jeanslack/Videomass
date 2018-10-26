[Back](../../../../videomass2_use.md)

## Crop Filter

The crop filter crops specific portions in the frame area. It is used by specifying values in pixels on the coordinates concerning height, width, horizontal distance (Y) and vertical distance (X). The starting point of the X and Y coordinates always starts from 0, which is the upper left end of the frame (the highlighted red corner of the image below). Each of the coordinates can only be disabled with the value -1 independently, which implies the centering of the frame (see image below).

- **Height**, The height of the output video. Set to -1 for disabling.

- **Width**, The width of the output video. Set to -1 for disabling.

- **X**, The horizontal position of the left edge. The value 0 sets the position on the extreme left of the frame. Values above 0 move the position to the right side of the frame. Set to -1 to disable this position and center the frame horizontally.

- **Y**, The vertical position of the top edge of the left corner. Values above 0 move the position towards the bottom side of the frame. Set to -1 to disable this position and center the frame vertically.

![Image](../../../../images/crop.png)

The button clear, restores the values to defaults parameters and disables the filter if you confirm with the Ok button. However, the values equal to -1 set on all input fields disable this filter.

[Back](../../../../videomass2_use.md)
