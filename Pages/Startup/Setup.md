[Back](../../videomass2_use.md)

## Setup Window

In the setup window you can set some parameters that will be saved for the next program openings. 
Whenever you save these settings, the program must necessarily be restarted to make them effective.

### General Table

**Settings CPU**   
In the Settings CPU box the settings relating to the CPU parameters will be displayed and will be used 
by some FFmpeg encoder.   

- Set the number of threads (from 0 to 32)   
  _FFmpeg always has one main thread which does most of the processing. In case of multiple inputs there are 
  also input threads for demuxing (1 thread per input); for single input demuxing is done on main thread.
  Setting "threads N" (where N > 1) on input enables multithreaded decoding which can spawn N additional threads 
  for each decoder which supports it._
  
 - Quality/Speed ratio modifier(from -16 to 16)   
   _Contrary to its name, cpu-used doesn't actually control how much overall CPU is being used, it controls the 
   quality of the encode (ie. how much cpu is used for each frame in total)._   

**Other Settings**

- Enables writing of command line text   
  _Allows you to make changes to the FFmpeg command line in the 'Command Line FFmpeg' table of the 'Presets Manager' panel. 
  Any parameter changes will not be stored but will still be applied during the process._
  
### Log Table

Each export process involves writing a log file. A log file contains a report showing errors, commands and other 
indications. Videomass2 generates three types of log files:   

1) Videomass_VideoConversion.log
2) Videomass_AudioConversion.log
3) Videomass_PresetsManager.log   

You can save these log files in a specific location on your drive, they will be copied from the Videomass2 configuration directory to a location of your choice.
   

[Back](../../videomass2_use.md)
