[Back](../../../../videomass_use.md)

## Scale:

Scale (resize) the input video or image to change the resolution result. If we'd like to keep the aspect ratio, we need to specify only one component, either width or height, and set the other component to -1 or to -2.   
Set to 0 value for disabling.   

**width**, Sets the width of the output video to pixel values. Set to 0 for disabling; set to -1 or -2 keep the same 
aspect ratio of the input video.   

**height**, Sets the height of the output video to pixel values. Set to 0 for disabling; set to -1 or -2 keep the same 
aspect ratio of the input video. 

## Setdar:

**setdar**, Set the frame (d)isplay (a)spect (r)atio. The setdar filter sets the Display Aspect Ratio for the filter 
output video.   
The result to be inserted corresponds to the fractional unit of a numerator and a denominator, for example: 16/9 .   
Set to 0 for disabling.

## Setsar:

**setsar**, The setsar filter sets the (S)ample (aka Pixel) (A)spect (R)atio for the filter output video.   
The result to be inserted corresponds to the fractional unit of a numerator and a denominator, for example: 1/1 .   
Set to 0 for disabling.

## Examples:

To reduce a video in 1280X720 to 640X360, then keeping the same aspect ratio to 16/9 there are 3 ways:

1) set width to 640 and set heigth to 360   
2) set width to 640 and set height to -1 or -2   
3) set heigth to 360 and set width to -1 or -2   

setdar/setsar (aspect ratio) should not need to be changed.   

To reduce the same video to a resolution of 640X480, we should also set the 4/3 sedar filter.   

To change the resolution on undefined aspect ratio (400X200), you can use setsar filter:
setsar to 1:1   

----------------------
Confirm your choices with the **OK** button.
The **Clear** button, restores the values to defaults parameters and disables the filter if you confirm with the Ok button. 
However, the values equal to 0 set on all input fields disable this filter.

[Back](../../../../videomass_use.md)
