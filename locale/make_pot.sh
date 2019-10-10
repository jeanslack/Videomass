#!/bin/bash
# Make a file po/pot with the current state of files

CWD=$(pwd)


xgettext -d videomass "../videomass3/Videomass3.py" \
"../videomass3/vdms_DIALOGS/audiodialogs.py" \
"../videomass3/vdms_DIALOGS/dialog_tools.py" \
"../videomass3/vdms_DIALOGS/ffmpeg_conf.py" \
"../videomass3/vdms_DIALOGS/ffmpeg_codecs.py" \
"../videomass3/vdms_DIALOGS/ffmpeg_formats.py" \
"../videomass3/vdms_DIALOGS/ffmpeg_search.py" \
"../videomass3/vdms_DIALOGS/first_time_start.py" \
"../videomass3/vdms_DIALOGS/infoprg.py" \
"../videomass3/vdms_DIALOGS/mediainfo.py" \
"../videomass3/vdms_DIALOGS/presets_addnew.py" \
"../videomass3/vdms_DIALOGS/settings.py" \
"../videomass3/vdms_DIALOGS/shownormlist.py" \
"../videomass3/vdms_DIALOGS/while_playing.py" \
"../videomass3/vdms_IO/filedir_control.py" \
"../videomass3/vdms_IO/IO_tools.py" \
"../videomass3/vdms_IO/presets_manager_properties.py" \
"../videomass3/vdms_MAIN/main_frame.py" \
"../videomass3/vdms_PANELS/audio_conv.py" \
"../videomass3/vdms_PANELS/dragNdrop.py" \
"../videomass3/vdms_PANELS/presets_mng_panel.py" \
"../videomass3/vdms_PANELS/video_conv.py" \
"../videomass3/vdms_PROCESS/ffplay_reproduction.py" \
"../videomass3/vdms_PROCESS/ffplay_reproductionWin32.py" \
"../videomass3/vdms_PROCESS/ffprobe_parser.py" \
"../videomass3/vdms_PROCESS/ffprobe_parserWin32.py" \
"../videomass3/vdms_PROCESS/task_processing.py" \
"../videomass3/vdms_PROCESS/task_processingWin32.py" \
"../videomass3/vdms_PROCESS/volumedetect.py" \
"../videomass3/vdms_PROCESS/volumedetectWin32.py"


