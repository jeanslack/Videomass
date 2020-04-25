#!/bin/bash
# Make a file po/pot with the current state of files

CWD=$(pwd)

# macos use /usr/local/Cellar/gettext/0.20.1/bin/xgettext

xgettext -d videomass "../videomass3/Videomass3.py" \
"../videomass3/vdms_dialogs/audiodialogs.py" \
"../videomass3/vdms_dialogs/video_filters.py" \
"../videomass3/vdms_dialogs/time_selection.py" \
"../videomass3/vdms_dialogs/first_time_start.py" \
"../videomass3/vdms_dialogs/infoprg.py" \
"../videomass3/vdms_dialogs/presets_addnew.py" \
"../videomass3/vdms_dialogs/settings.py" \
"../videomass3/vdms_frames/ffmpeg_conf.py" \
"../videomass3/vdms_frames/ffmpeg_codecs.py" \
"../videomass3/vdms_frames/ffmpeg_formats.py" \
"../videomass3/vdms_frames/shownormlist.py" \
"../videomass3/vdms_frames/while_playing.py" \
"../videomass3/vdms_frames/ffmpeg_search.py" \
"../videomass3/vdms_frames/mediainfo.py" \
"../videomass3/vdms_frames/ydl_mediainfo.py" \
"../videomass3/vdms_io/filenames_check.py" \
"../videomass3/vdms_io/IO_tools.py" \
"../videomass3/vdms_io/presets_manager_properties.py" \
"../videomass3/vdms_main/main_frame.py" \
"../videomass3/vdms_panels/av_conversions.py" \
"../videomass3/vdms_panels/choose_topic.py" \
"../videomass3/vdms_panels/youtubedl_ui.py" \
"../videomass3/vdms_panels/filedrop.py" \
"../videomass3/vdms_panels/long_processing_task.py" \
"../videomass3/vdms_panels/presets_manager.py" \
"../videomass3/vdms_panels/textdrop.py" \
"../videomass3/vdms_threads/ffplay_reproduction.py" \
"../videomass3/vdms_threads/ffprobe_parser.py" \
"../videomass3/vdms_threads/one_pass.py" \
"../videomass3/vdms_threads/picture_exporting.py" \
"../videomass3/vdms_threads/two_pass_EBU.py" \
"../videomass3/vdms_threads/two_pass.py" \
"../videomass3/vdms_threads/volumedetect.py" \
"../videomass3/vdms_threads/ydl_executable.py" \
"../videomass3/vdms_threads/youtubedlupdater.py" \



