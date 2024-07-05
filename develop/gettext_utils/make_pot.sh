#!/bin/bash

# Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
# Copyleft - 2024 Gianluca Pernigotto <jeanlucperni@gmail.com>
# license: GPL3
# Rev: July.05.2024
#
# PORPOSE: Create a new `videomass.pot` file with the latest strings.
# USAGE: ~$ make_pot.sh '/path/to/videomass/package'

TARGET=$1  # Python package directory
POTFILE="$TARGET/data/locale/videomass.pot"  # store the new .pot file here

if [ -z "$1" ]; then
    echo 'Missing argument: Requires the absolute Python package directory path name'
    exit 1
fi

if [ -d "${TARGET}" ] ; then
    echo "Package directory: '${TARGET}'";
else
    if [ -f "${TARGET}" ]; then
        echo "'${TARGET}' is a file";
        exit 1
    else
        echo "'${TARGET}' is not valid";
        exit 1
    fi
fi

xgettext -d videomass "${TARGET}/gui_app.py" \
"${TARGET}/vdms_dialogs/audioproperties.py" \
"${TARGET}/vdms_dialogs/epilogue.py" \
"${TARGET}/vdms_dialogs/filter_crop.py" \
"${TARGET}/vdms_dialogs/filter_deinterlace.py" \
"${TARGET}/vdms_dialogs/filter_denoisers.py" \
"${TARGET}/vdms_dialogs/filter_scale.py" \
"${TARGET}/vdms_dialogs/filter_stab.py" \
"${TARGET}/vdms_dialogs/filter_transpose.py" \
"${TARGET}/vdms_dialogs/list_warning.py" \
"${TARGET}/vdms_dialogs/wizard_dlg.py" \
"${TARGET}/vdms_dialogs/about_dialog.py" \
"${TARGET}/vdms_dialogs/setting_profiles.py" \
"${TARGET}/vdms_dialogs/set_timestamp.py" \
"${TARGET}/vdms_dialogs/preferences.py" \
"${TARGET}/vdms_dialogs/videomass_check_version.py" \
"${TARGET}/vdms_dialogs/mediainfo.py" \
"${TARGET}/vdms_dialogs/widget_utils.py" \
"${TARGET}/vdms_dialogs/showlogs.py" \
"${TARGET}/vdms_dialogs/renamer.py" \
"${TARGET}/vdms_dialogs/ffmpeg_help.py" \
"${TARGET}/vdms_dialogs/filter_colorcorrection.py" \
"${TARGET}/vdms_dialogs/ffmpeg_conf.py" \
"${TARGET}/vdms_dialogs/ffmpeg_codecs.py" \
"${TARGET}/vdms_dialogs/ffmpeg_formats.py" \
"${TARGET}/vdms_dialogs/shownormlist.py" \
"${TARGET}/vdms_dialogs/while_playing.py" \
"${TARGET}/vdms_dialogs/queuedlg.py" \
"${TARGET}/vdms_dialogs/queue_edit.py" \
"${TARGET}/vdms_dialogs/singlechoicedlg.py" \
"${TARGET}/vdms_miniframes/timeline.py" \
"${TARGET}/vdms_io/checkup.py" \
"${TARGET}/vdms_io/io_tools.py" \
"${TARGET}/vdms_utils/presets_manager_utils.py" \
"${TARGET}/vdms_main/main_frame.py" \
"${TARGET}/vdms_panels/av_conversions.py" \
"${TARGET}/vdms_panels/audio_encoders/acodecs.py" \
"${TARGET}/vdms_panels/video_encoders/av1_aom.py" \
"${TARGET}/vdms_panels/video_encoders/av1_svt.py" \
"${TARGET}/vdms_panels/video_encoders/avc_x264.py" \
"${TARGET}/vdms_panels/video_encoders/hevc_x265.py" \
"${TARGET}/vdms_panels/video_encoders/mpeg4.py" \
"${TARGET}/vdms_panels/video_encoders/video_encodercopy.py" \
"${TARGET}/vdms_panels/video_encoders/video_no_enc.py" \
"${TARGET}/vdms_panels/video_encoders/vp9_webm.py" \
"${TARGET}/vdms_panels/miscellaneous/miscell.py" \
"${TARGET}/vdms_panels/choose_topic.py" \
"${TARGET}/vdms_panels/concatenate.py" \
"${TARGET}/vdms_panels/filedrop.py" \
"${TARGET}/vdms_panels/long_processing_task.py" \
"${TARGET}/vdms_panels/presets_manager.py" \
"${TARGET}/vdms_panels/sequence_to_video.py" \
"${TARGET}/vdms_panels/video_to_sequence.py" \
"${TARGET}/vdms_threads/ffplay_file.py" \
"${TARGET}/vdms_threads/image_extractor.py" \
"${TARGET}/vdms_threads/slideshow.py" \
"${TARGET}/vdms_ytdlp/formatcode.py" \
"${TARGET}/vdms_ytdlp/long_task_ytdlp.py" \
"${TARGET}/vdms_ytdlp/main_ytdlp.py" \
"${TARGET}/vdms_ytdlp/playlist_indexing.py" \
"${TARGET}/vdms_ytdlp/textdrop.py" \
"${TARGET}/vdms_ytdlp/ydl_downloader.py" \
"${TARGET}/vdms_ytdlp/ydl_extractinfo.py" \
"${TARGET}/vdms_ytdlp/ydl_mediainfo.py" \
"${TARGET}/vdms_ytdlp/youtubedl_ui.py" \
"${TARGET}/vdms_ytdlp/ydl_preferences.py" \
"${TARGET}/vdms_ytdlp/subtitles_editor.py" \
"${TARGET}/vdms_utils/queue_utils.py" \

if [ $? != 0 ]; then
    echo 'Failed!'
else
    mv videomass.po "${POTFILE}"
    echo "A new file 'videomass.pot' has been created successfully."
    echo "Done!"
fi
