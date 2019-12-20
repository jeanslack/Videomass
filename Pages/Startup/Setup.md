[Back](../../videomass_use.md)

## Setup

In the setup dialog you can set some parameters that will be saved for the next program openings. 
Whenever you save these settings the program must necessarily be restarted to make them effective.

------------------
### General (tab)

**FFmpeg threads option**   
Set the number of threads (from 0 to 32). FFmpeg always has one main thread which does most of the processing. 
In case of multiple inputs there are also input threads for demuxing (1 thread per input); for single input 
demuxing is done on main thread. Setting "threads N" (where N > 1) on input enables multithreaded decoding 
which can spawn N additional threads for each decoder which supports it.
  
-------------------  
### Logging level (tab)

By default, FFmpeg logs to stderr with a logging level set to 'info'. This means that the amount of output 
messages we see scrolling (for example on a terminal) depends on it. However, to limit or increase the verbosity 
of these messages it is possible to change the flags of the 'loglevel' option which will also affect the output 
displayed by Videomass and the messages written to the log files.   

By default, Videomass sets the FFmpeg loglevel flag on 'warning' and FFplay's flag on 'error'. This allows a balanced 
level of messages to be displayed and written to the logs useful to understand what is happening during a process.   

During the processes, for example when we reproduce a movie to test the filters or when we start a conversion etc, 
different log files are created, each of which has a specific name that indicates which process has been used. 
These log files are as follows:   

- Videomass_FFplay.log
- Videomass_PresetsManager.log
- Videomass_AV_conversions.log
- Videomass_Volumedected.log
- Youtube_downloader.log

The log files are saved in the Videomass configuration directory which can be opened directly with the appropriate 
function in the menu bar > Tools > Log directory . In each new process the contents of a log file are completely erased 
and rewritten and contain a report showing errors, warnings and commands.

-------------------
### Executables (tab)

In this table you can specify different paths of your choice of ffmpeg, ffprobe and ffplay executables.   
This means that you can use a FFmpeg executable created with a custom configuration or with other enabled features.

[Back](../../videomass_use.md)
