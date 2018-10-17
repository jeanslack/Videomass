[Back](../videomass2_use.md)

## Scale Filter

Scale (resize) the input video or image, using the libswscale library. If we'd like to keep the aspect ratio, we need to specify 
only one component, either width or height, and set the other component to -1 or to -2.   
Set to 0 value for disabling.   

**Width**, Sets the width of the output video to pixel values. Set to 0 for disabling; set to -1 or -2 keep the same 
aspect ratio of the input video.   

**Height**, Sets the height of the output video to pixel values. Set to 0 for disabling; set to -1 or -2 keep the same 
aspect ratio of the input video.   

**Setdar**, Set the frame (d)isplay (a)spect (r)atio. The setdar filter sets the Display Aspect Ratio for the filter 
output video. This is done by changing the specified Sample (aka Pixel) Aspect Ratio, according to the following equation: 
``` 
DAR = HORIZONTAL_RESOLUTION / VERTICAL_RESOLUTION * SAR
```  
Keep in mind that the setdar filter does not modify the pixel dimensions of the video frame. Also, the display aspect ratio 
set by this filter may be changed by later filters in the filterchain, e.g. in case of scaling or if another "setdar" or a 
"setsar" filter is applied.   
Set to 0 for disabling.   


**Setsar**, The setsar filter sets the Sample (aka Pixel) Aspect Ratio for the filter output video. Note that as a 
consequence of the application of this filter, the output display aspect ratio will change according to the equation 
above. Keep in mind that the sample aspect ratio set by the setsar filter may be changed by later filters in the filterchain, 
e.g. if another "setsar" or a "setdar" filter is applied.   
Set to 0 for disabling.   

The button clear, restores the values to defaults parameters and disables the filter if you confirm with the Ok button. 
However, the values equal to 0 set on all input fields disable this filter.

[Back](../videomass2_use.md)
