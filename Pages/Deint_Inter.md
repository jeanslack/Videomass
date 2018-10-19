[Back](../videomass2_use.md)

## Deinterlacer filters:

### w3fdif 
stands for Weston 3 Field Deinterlacing Filter.   
Based on the process described by Martin Weston for BBC R&D, and implemented based on the de-interlace algorithm written 
by Jim Easterbrook for BBC R&D, the Weston 3 field deinterlacing filter uses filter coefficients calculated by BBC R&D.

- Advanced Options:
  - **filter**, Set the interlacing filter coefficients. Accepts one of the following values:   
                        *simple*, Simple filter coefficient set.   
                        *complex*, More-complex filter coefficient set.   
                         Default value is *complex*.   
                                                 
  - **deinterlace**, Specify which frames to deinterlace. Accept one of the following values:   
                        *all*, Deinterlace all frames   
                        *interlaced*, Only deinterlace frames marked as interlaced.   
                         Default value is *all*.   


### yadif 
Deinterlace the input video ("yadif" means "(y)et (a)nother (d)e(i)nterlacing (f)ilter").   
For FFmpeg is the best and fastest choice '

- Advanced Options:
  - **Mode**, The interlacing mode to adopt. It accepts one of the following values:   
           *0, send_frame*, - Output one frame for each frame.   
           *1, send_field*, - Output one frame for each field.   
           *2, send_frame_nospatial*, - Like send_frame, but it skips the spatial interlacing check.   
           *3, send_field_nospatial*, - Like send_field, but it skips the spatial interlacing check.   
            Default value is *send_field*.   

  - **Parity**, The picture field parity assumed for the input interlaced video. It accepts one of the following values:   
            *0, tff*, - Assume the top field is first.   
            *1, bff*, - Assume the bottom field is first.   
            *-1, auto*, - Enable automatic detection of field parity.      
             The default value is *auto*. If the interlacing is unknown or the decoder does not export this information, 
             top field first will be assumed.

  - **Deint**, Specify which frames to deinterlace. Accept one of the following values:   
                        *all*, Deinterlace all frames   
                        *interlaced*, Only deinterlace frames marked as interlaced.   
                         Default value is *all*.

-----------------------
## Interlacer Filter:

### interlace (filter)
Simple interlacing filter from progressive contents. This interleaves upper (or lower) lines from odd 
frames with lower (or upper) lines from even frames, halving the frame rate and preserving image height.

- Advanced Options:

  - **scan**, determines whether the interlaced frame is taken from the even (tff - default) or odd (bff) lines of the 
  progressive frame.
  
  - **lowpass**, Enable (default) or disable the vertical lowpass filter to avoid twitter interlacing and reduce moire 
  patterns. Default is no setting.
