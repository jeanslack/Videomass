#!/bin/bash

# Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
# Copyleft - 2018/2023 Gianluca Pernigotto <jeanlucperni@gmail.com>
# license: GPL3
# Rev: March.22.2022
#
# Make a new `videomass.po` file on '../../videomass/locale'.
# The previus videomass.po file will be overwrite with the new
# one incoming which will update latest strings for traslation .

PLATFORM=$(uname)  # command to show platform
self="$(readlink -f -- $0)"  # this file
here="${self%/*}"  # dirname of this file
rootdir=$(dirname $here)  # base sources directory
target="$rootdir/videomass/locale"  # location to store new incoming

cd $target

if [ "$PLATFORM" = "Darwin" ]; then
    # On my Macos xgettext is in '/usr/local/Cellar/gettext/0.20.1/bin/xgettext'
    # which is't in $PATH
    XGETTEXT="/usr/local/Cellar/gettext/0.20.1/bin/xgettext"

elif [ "$PLATFORM" = "Linux" ]; then
    XGETTEXT="xgettext"
fi

$XGETTEXT -d videomass "../gui_app.py" \
"../vdms_dialogs/audiodialogs.py" \
"../vdms_dialogs/epilogue.py" \
"../vdms_dialogs/filter_crop.py" \
"../vdms_dialogs/filter_deinterlace.py" \
"../vdms_dialogs/filter_denoisers.py" \
"../vdms_dialogs/filter_scale.py" \
"../vdms_dialogs/filter_stab.py" \
"../vdms_dialogs/filter_transpose.py" \
"../vdms_dialogs/list_warning.py" \
"../vdms_dialogs/wizard_dlg.py" \
"../vdms_dialogs/about.py" \
"../vdms_dialogs/presets_addnew.py" \
"../vdms_dialogs/set_timestamp.py" \
"../vdms_dialogs/preferences.py" \
"../vdms_dialogs/videomass_check_version.py" \
"../vdms_dialogs/mediainfo.py" \
"../vdms_dialogs/widget_utils.py" \
"../vdms_dialogs/showlogs.py" \
"../vdms_dialogs/renamer.py" \
"../vdms_dialogs/ffmpeg_help.py" \
"../vdms_dialogs/filter_colorcorrection.py" \
"../vdms_dialogs/ffmpeg_conf.py" \
"../vdms_dialogs/ffmpeg_codecs.py" \
"../vdms_dialogs/ffmpeg_formats.py" \
"../vdms_dialogs/shownormlist.py" \
"../vdms_dialogs/while_playing.py" \
"../vdms_miniframes/timeline.py" \
"../vdms_io/checkup.py" \
"../vdms_io/io_tools.py" \
"../vdms_io/presets_manager_prop.py" \
"../vdms_main/main_frame.py" \
"../vdms_panels/av_conversions.py" \
"../vdms_panels/choose_topic.py" \
"../vdms_panels/concatenate.py" \
"../vdms_panels/filedrop.py" \
"../vdms_panels/long_processing_task.py" \
"../vdms_panels/presets_manager.py" \
"../vdms_panels/sequence_to_video.py" \
"../vdms_panels/hevc_avc.py" \
"../vdms_panels/libaom.py" \
"../vdms_panels/webm.py" \
"../vdms_panels/video_to_sequence.py" \
"../vdms_threads/ffplay_file.py" \
"../vdms_threads/one_pass.py" \
"../vdms_threads/picture_exporting.py" \
"../vdms_threads/two_pass_ebu.py" \
"../vdms_threads/two_pass.py" \
"../vdms_threads/slideshow.py" \
"../vdms_ytdlp/formatcode.py" \
"../vdms_ytdlp/long_task_ytdlp.py" \
"../vdms_ytdlp/main_ytdlp.py" \
"../vdms_ytdlp/playlist_indexing.py" \
"../vdms_ytdlp/textdrop.py" \
"../vdms_ytdlp/ydl_downloader.py" \
"../vdms_ytdlp/ydl_extractinfo.py" \
"../vdms_ytdlp/ydl_mediainfo.py" \
"../vdms_ytdlp/youtubedl_ui.py" \


if [ $? != 0 ]; then
    echo 'Failed!'
else
    mv videomass.po videomass.pot
    echo "A new 'videomass.pot' was created on: '${target}'"
    echo "Done!"
fi
