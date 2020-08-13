#!/bin/bash

# Author: Gianluca Pernigoto <jeanlucperni@gmail.com>
# Copyright: (c) 2020 Gianluca Pernigoto <jeanlucperni@gmail.com>
# license: GPL3
# Rev: June.30.2020
#
# Make a new `videomass.po` file on '../../videomass3/locale'.
# The previus videomass.po file will be overwrite with new one
# incoming which will update with the current state of strings
# to tralsated .

PLATFORM=$(uname)  # command to show platform
self="$(readlink -f -- $0)"  # this file
here="${self%/*}"  # dirname of this file
rootdir=$(dirname $here)  # base sources directory
target="$rootdir/videomass3/locale"  # location to store new incoming

cd $target

if [ "$PLATFORM" = "Darwin" ]; then
    # On my Macos xgettext is in '/usr/local/Cellar/gettext/0.20.1/bin/xgettext'
    # which is't in $PATH
    XGETTEXT="/usr/local/Cellar/gettext/0.20.1/bin/xgettext"

elif [ "$PLATFORM" = "Linux" ]; then
    XGETTEXT="xgettext"
fi

$XGETTEXT -d videomass "../Videomass3.py" \
"../vdms_dialogs/audiodialogs.py" \
"../vdms_dialogs/video_filters.py" \
"../vdms_dialogs/time_selection.py" \
"../vdms_dialogs/first_time_start.py" \
"../vdms_dialogs/infoprg.py" \
"../vdms_dialogs/presets_addnew.py" \
"../vdms_dialogs/settings.py" \
"../vdms_frames/ffmpeg_conf.py" \
"../vdms_frames/ffmpeg_codecs.py" \
"../vdms_frames/ffmpeg_formats.py" \
"../vdms_frames/shownormlist.py" \
"../vdms_frames/while_playing.py" \
"../vdms_frames/ffmpeg_search.py" \
"../vdms_frames/mediainfo.py" \
"../vdms_frames/ydl_mediainfo.py" \
"../vdms_io/filenames_check.py" \
"../vdms_io/IO_tools.py" \
"../vdms_io/presets_manager_properties.py" \
"../vdms_main/main_frame.py" \
"../vdms_panels/av_conversions.py" \
"../vdms_panels/choose_topic.py" \
"../vdms_panels/youtubedl_ui.py" \
"../vdms_panels/filedrop.py" \
"../vdms_panels/long_processing_task.py" \
"../vdms_panels/presets_manager.py" \
"../vdms_panels/textdrop.py" \
"../vdms_threads/ffplay_file.py" \
"../vdms_threads/ffprobe_parser.py" \
"../vdms_threads/mpv_url.py" \
"../vdms_threads/one_pass.py" \
"../vdms_threads/picture_exporting.py" \
"../vdms_threads/two_pass_EBU.py" \
"../vdms_threads/two_pass.py" \
"../vdms_threads/volumedetect.py" \
"../vdms_threads/ydl_executable.py" \
"../vdms_threads/youtubedlupdater.py"

if [ $? != 0 ]; then
    echo 'Failed!'
else
    mv videomass.po videomass.pot
    echo "Done!"
    echo "'videomass.pot' was created on: '${target}'"
fi
