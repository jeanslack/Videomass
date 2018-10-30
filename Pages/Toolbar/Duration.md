[Back](../../videomass2_use.md)

## Duration

The Duration tool consists of two different parameters: 
**Seeking** (time position) and **Cut** (duration) both expressed in hours, minutes and seconds (hh,mm,ss).
Note that on Videomass2 the Cut parameter (duration) always refers to the total duration from the set Seeking 
point (if set), and not from the beginning of the first scene of a movie.

![Image](../../images/duration.png) 

When set with time values above zero and then confirmed with the Ok button, the Duration button in the secondary toolbar is turned with a green gradient.   
![Image](../../images/btn_durationOn.png)   
When all time values are reset with the Clear key and then confirmed with the Ok button, the key color will return to default.   
![Image](../../images/btn_durationOff.png)

----------------

### _How can I extract a segment from a media?_
If you need to extract only a specific part of your media file, you will need to use the Seeking parameter to get 
a specific part of the time position.
To extract only a small segment in the middle of a movie, it can be used in conjunction with Cut, which specifies the 
duration.   

Example: if we have a film with a duration of one hour, to extract a segment from the twenty-third to forty-second 
minutes from the beginning of the film, we have to set the Seeking parameter to 00.23.00 and the Cut parameter to 
00.19, 00.  See the graph below.   

![Image](../../images/duration_graphic.png)

----------------

### _Tip_
To find out the overall duration of an imported media file, you can use the [Show Metadata](https://github.com/jeanslack/Videomass2/blob/gh-pages/Pages/Toolbar/Show_metadata.md) tool.

----------------

### _Trick:_ 
To perform conversion tests, you can use the **Cut** parameter to set a short duration without waiting for the end 
of a whole process (which can sometimes be very long).

----------------

### _IMPORTANT NOTES:_ 
On Videomass2 the Duration tool, when set, generates a parameter that is reflected globally throughout the program 
and in all those processes that use it, ie in all conversion processes with _Presets Manager_, _Video Conversions_, _Audio Conversions_ interfaces and _playback_ function.
Keeping this principle in mind you can enable or disable this tool as needed.

----------------

[Back](../../videomass2_use.md)
