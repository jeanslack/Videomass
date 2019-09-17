[Home](index.md)

Parameters for new profiles to be used with Videomass. They need to be added with the appropriate dialog to create new profiles on the Presets Manager panel.   

## Add a new audio stream to a movie
This replaces the current audio stream on the movie. Both streams will not be encoded and the duration of the new movie created will be equivalent to the duration of the added audio stream:   

```shell
-i "ADD_ONE_AUDIO_FILE_HERE" -map 0:v -map 1:a -c copy -shortest
```   

Alternatively, you can only convert the audio stream without encoding the video:

```shell
-i "INSERT ONE AUDIO FILE HERE" -c:v copy -c:a aac -strict experimental -map 0:v:0 -map 1:a:0 -shortest
```   

## Parameters not yet implemented on Videomass

**Add audio stream to a image**   
```shell
ffmpeg -loop 1 -i "IMAGE.png" -i "AUDIO_STREAM.mp3" -c:v libx264 -tune stillimage -c:a aac -b:a 192k -pix_fmt yuv420p -shortest "Output_Result1.mp4"
``` 

**Create a slideshows**   
```shell
ffmpeg -loop 1 -i "IMAGE_1.png" -i "IMAGE_2.png" -i "AUDIO_STREAM.mp3" -c:v libx264 -tune stillimage -c:a aac -b:a 192k -pix_fmt yuv420p -shortest "Output_Result2.mp4"
``` 

**Add more numbered images**   
```shell
ffmpeg -y -framerate 1/10 -start_number 1 -i "image_%0.jpg" -i "an_Audio_stream.mp3" -c:v libx264 -r 25 -pix_fmt yuv420p -c:a aac -strict experimental -shortest "result3.mp4"
``` 

or    

```shell
ffmpeg -y -framerate 1/5 -start_number 1 -i "image_%0.jpg" -c:v libx264 -r 25 -pix_fmt yuv420p -c:a aac -shortest "result4.mp4"
``` 

https://trac.ffmpeg.org/wiki/Slideshow




[Home](index.md)
