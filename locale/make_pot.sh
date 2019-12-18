#!/bin/bash
# Make a file po/pot with the current state of files

CWD=$(pwd)


xgettext -d videomass "../videomass3/Videomass3.py" \
"../videomass3/vdms_DIALOGS/audiodialogs.py" \
"../videomass3/vdms_DIALOGS/video_filters.py" \
"../videomass3/vdms_DIALOGS/time_selection.py" \
"../videomass3/vdms_DIALOGS/first_time_start.py" \
"../videomass3/vdms_DIALOGS/infoprg.py" \
"../videomass3/vdms_DIALOGS/presets_addnew.py" \
"../videomass3/vdms_DIALOGS/settings.py" \
"../videomass3/vdms_FRAMES/ffmpeg_conf.py" \
"../videomass3/vdms_FRAMES/ffmpeg_codecs.py" \
"../videomass3/vdms_FRAMES/ffmpeg_formats.py" \
"../videomass3/vdms_FRAMES/shownormlist.py" \
"../videomass3/vdms_FRAMES/while_playing.py" \
"../videomass3/vdms_FRAMES/ffmpeg_search.py" \
"../videomass3/vdms_FRAMES/mediainfo.py" \
"../videomass3/vdms_FRAMES/ydl_mediainfo.py" \
"../videomass3/vdms_IO/filenames_check.py" \
"../videomass3/vdms_IO/IO_tools.py" \
"../videomass3/vdms_IO/presets_manager_properties.py" \
"../videomass3/vdms_MAIN/main_frame.py" \
"../videomass3/vdms_PANELS/av_conversions.py" \
"../videomass3/vdms_PANELS/choose_topic.py" \
"../videomass3/vdms_PANELS/downloader.py" \
"../videomass3/vdms_PANELS/filedrop.py" \
"../videomass3/vdms_PANELS/long_processing_task.py" \
"../videomass3/vdms_PANELS/presets_manager.py" \
"../videomass3/vdms_PANELS/textdrop.py" \
"../videomass3/vdms_THREADS/ffplay_reproduction.py" \
"../videomass3/vdms_THREADS/ffprobe_parser.py" \
"../videomass3/vdms_THREADS/one_pass.py" \
"../videomass3/vdms_THREADS/picture_exporting.py" \
"../videomass3/vdms_THREADS/two_pass_EBU.py" \
"../videomass3/vdms_THREADS/two_pass.py" \
"../videomass3/vdms_THREADS/volumedetect.py" \
"../videomass3/vdms_THREADS/ydl_extract_info.py" \



