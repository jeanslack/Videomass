#!/bin/bash

# Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
# Copyleft - 2024 Gianluca Pernigotto <jeanlucperni@gmail.com>
# license: GPL3
# Rev: June.15.2024
#
# Make a new `videomass.po` file on '../../resources/locale'.
# The previus videomass.po file will be overwrite with the new
# one incoming which will update latest strings for traslation .

PLATFORM=$(uname)  # command to show platform
self="$(readlink -f -- $0)"  # this file
here="${self%/*}"  # dirname of this file
rootdir=$(dirname $here)  # base sources directory
target="$rootdir/videomass/data/locale"  # location to store new incoming

cd $target

if [ "$PLATFORM" = "Darwin" ]; then
    # On my Macos xgettext is in '/usr/local/Cellar/gettext/0.20.1/bin/xgettext'
    # which is't in $PATH
    XGETTEXT="/usr/local/Cellar/gettext/0.20.1/bin/xgettext"

elif [ "$PLATFORM" = "Linux" ]; then
    XGETTEXT="xgettext"
fi

$XGETTEXT -d videomass "../../../videomass/gui_app.py" \
"../../../videomass/vdms_dialogs/audioproperties.py" \
"../../../videomass/vdms_dialogs/epilogue.py" \
"../../../videomass/vdms_dialogs/filter_crop.py" \
"../../../videomass/vdms_dialogs/filter_deinterlace.py" \
"../../../videomass/vdms_dialogs/filter_denoisers.py" \
"../../../videomass/vdms_dialogs/filter_scale.py" \
"../../../videomass/vdms_dialogs/filter_stab.py" \
"../../../videomass/vdms_dialogs/filter_transpose.py" \
"../../../videomass/vdms_dialogs/list_warning.py" \
"../../../videomass/vdms_dialogs/wizard_dlg.py" \
"../../../videomass/vdms_dialogs/about_dialog.py" \
"../../../videomass/vdms_dialogs/setting_profiles.py" \
"../../../videomass/vdms_dialogs/set_timestamp.py" \
"../../../videomass/vdms_dialogs/preferences.py" \
"../../../videomass/vdms_dialogs/videomass_check_version.py" \
"../../../videomass/vdms_dialogs/mediainfo.py" \
"../../../videomass/vdms_dialogs/widget_utils.py" \
"../../../videomass/vdms_dialogs/showlogs.py" \
"../../../videomass/vdms_dialogs/renamer.py" \
"../../../videomass/vdms_dialogs/ffmpeg_help.py" \
"../../../videomass/vdms_dialogs/filter_colorcorrection.py" \
"../../../videomass/vdms_dialogs/ffmpeg_conf.py" \
"../../../videomass/vdms_dialogs/ffmpeg_codecs.py" \
"../../../videomass/vdms_dialogs/ffmpeg_formats.py" \
"../../../videomass/vdms_dialogs/shownormlist.py" \
"../../../videomass/vdms_dialogs/while_playing.py" \
"../../../videomass/vdms_dialogs/queuedlg.py" \
"../../../videomass/vdms_dialogs/queue_edit.py" \
"../../../videomass/vdms_dialogs/singlechoicedlg.py" \
"../../../videomass/vdms_miniframes/timeline.py" \
"../../../videomass/vdms_io/checkup.py" \
"../../../videomass/vdms_io/io_tools.py" \
"../../../videomass/vdms_utils/presets_manager_utils.py" \
"../../../videomass/vdms_main/main_frame.py" \
"../../../videomass/vdms_panels/av_conversions.py" \
"../../../videomass/vdms_panels/audio_encoders/acodecs.py" \
"../../../videomass/vdms_panels/video_encoders/av1_aom.py" \
"../../../videomass/vdms_panels/video_encoders/av1_svt.py" \
"../../../videomass/vdms_panels/video_encoders/avc_x264.py" \
"../../../videomass/vdms_panels/video_encoders/hevc_x265.py" \
"../../../videomass/vdms_panels/video_encoders/mpeg4.py" \
"../../../videomass/vdms_panels/video_encoders/video_encodercopy.py" \
"../../../videomass/vdms_panels/video_encoders/video_no_enc.py" \
"../../../videomass/vdms_panels/video_encoders/vp9_webm.py" \
"../../../videomass/vdms_panels/miscellaneous/miscell.py" \
"../../../videomass/vdms_panels/choose_topic.py" \
"../../../videomass/vdms_panels/concatenate.py" \
"../../../videomass/vdms_panels/filedrop.py" \
"../../../videomass/vdms_panels/long_processing_task.py" \
"../../../videomass/vdms_panels/presets_manager.py" \
"../../../videomass/vdms_panels/sequence_to_video.py" \
"../../../videomass/vdms_panels/video_to_sequence.py" \
"../../../videomass/vdms_threads/ffplay_file.py" \
"../../../videomass/vdms_threads/image_extractor.py" \
"../../../videomass/vdms_threads/slideshow.py" \
"../../../videomass/vdms_ytdlp/formatcode.py" \
"../../../videomass/vdms_ytdlp/long_task_ytdlp.py" \
"../../../videomass/vdms_ytdlp/main_ytdlp.py" \
"../../../videomass/vdms_ytdlp/playlist_indexing.py" \
"../../../videomass/vdms_ytdlp/textdrop.py" \
"../../../videomass/vdms_ytdlp/ydl_downloader.py" \
"../../../videomass/vdms_ytdlp/ydl_extractinfo.py" \
"../../../videomass/vdms_ytdlp/ydl_mediainfo.py" \
"../../../videomass/vdms_ytdlp/youtubedl_ui.py" \
"../../../videomass/vdms_ytdlp/ydl_preferences.py" \
"../../../videomass/vdms_ytdlp/subtitles_editor.py" \
"../../../videomass/vdms_utils/queue_utils.py" \

if [ $? != 0 ]; then
    echo 'Failed!'
else
    mv videomass.po videomass.pot
    echo "A new 'videomass.pot' was created on: '${target}'"
    echo "Done!"
fi
