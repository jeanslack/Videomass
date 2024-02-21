### This preset is already included on [Videomass Default Presets](https://github.com/jeanslack/Videomass-presets/tree/master/Videomass%20Default%20Presets)

As suggested in this [issue](https://github.com/jeanslack/Videomass-presets/issues/2), I have created a new preset for Videomass that allows you to encode/convert video to MPEG2 in the best possible quality for DVD making. The original source and full discussion can be found in this forum: https://forum.doom9.org/showthread.php?t=174620

Given the possible range of settings, the many combinations for different use cases and the interesting information content, I thought it appropriate to create a script in bash starting from the original one on this page: https://forum.doom9.org/showthread.php?p=1809116#post1809116

Save the following script (for example `GMJCZP.sh`) and give it execute permissions. You can use the script to convert directly but you can also use it to generate the code to paste on the Videomass preset manager (please see USAGE on script).

In this script you can find a lot of settings for different quality targets that you can adapt to specific profiles. There are currently 13 combinations for matrices.

```bash
#!/bin/bash
#
# Porpose: Coding to DVD with FFMPEG.
# Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
#
# DESCRITION:
#     This Script encodes MPEG2 video with FFMPEG. It allow you to convert mp4
#     videos to MPEG2 with best quality possible while still fitting on single
#     layer DVDs. The file obtained in m2v format will have to be subsequently
#     worked with a DVD authoring application.
#
#     The original one was written in DOS language and can be found on this
#     web page: <https://forum.doom9.org/showthread.php?p=1809116#post1809116>
#
#     Script based in "DVDs do you think your encoder is the best THEN PROVE IT!!!
#     (version 2.0)" page 2, and tests of Fishman0919, manolito and mine
#     Thanks to GMJCZP, ALEX-KID, manono, Didée, hank315, Fishman0919 and manolito!
#
# USAGE: 
#    To generate the code for the Viodeomass preset manager, type
#    ./GMJCZP.sh
#
#    Use this script to start the conversion directly, type
#    ./GMJCZP.sh 'inputvideo' 'outputname'
#
###################################################################

# set -x  # Print commands and their arguments as they are executed.
set -e  # Exit immediately if a command exits with a non-zero status.

#---------------------------------------------------------------
#                      Source and target files
#---------------------------------------------------------------
SOURCEFILE="$1"  # source video

if [ "$2" == "" ]; then
    TARGETFILE=""  # target file
    echo -e '----------------------------------------------------------------------'
    echo -e '              FFMPEG MPEG2 Profile (video output only)'
    echo -e '                  GMJCZP, version 4.2, 27/06/2021'
    echo -e '     Please, Copy and paste code for Videomass preset manager'
    echo -e '----------------------------------------------------------------------'
else
    TARGETFILE="$2.m2v"  # target file
    echo -e '----------------------------------------------------------------------'
    echo -e '              FFMPEG MPEG2 Profile (video output only)'
    echo -e '                  GMJCZP, version 4.2, 27/06/2021'
    echo -e '----------------------------------------------------------------------'
fi

#---------------------------------------------------------------
#                      Rate control settings
#---------------------------------------------------------------
# Medium bitrate (b)
E_BR=3000k

# Maximum Bitrate (maxrate) (Use 9800k max for DVD compatibility)
VBV_MBR=9800k

# Maximum buffer size (bufsize) (Use 1835k max for DVD compatibility)
VBV_MBS=1835k

# Fixed quality VBR (q) (Fishman0919's suggestion)
E_FQ=2.0

# Minimum quantizer (qmin) (2 is good value for low bitrate, b<=1800k)
E_MQ=1.0

# Minimum frame-level Lagrange multiplier (lmin) [0.01;255.0] (Fishman0919
# suggests a value of 0.75)
E_MLM=0.75

# Minimum macroblock-level Lagrange multiplier (mblmin) [0.01;255.0]
# (Fishman0919 suggests a value of 50.0)
E_MBL=50.0

# Quantizer variability (qcomp) [0.00;1.00] (0.75 is good value) (Fishman0919
# suggests a value of 0.7)
E_VQ=0.70

#---------------------------------------------------------------
#                      GOP structure
#---------------------------------------------------------------
# Maximum interval of I-frames or Keyframes (g) (Use 15 for DVD PAL, 18 for
# DVD NTSC, 12 for Pulldown)
E_MIK=12

# Maximum number of B-frames (bf) [0;4] (Use 2 for DVD compatibility)
E_MBF=2

# Adaptive B-Frames strategy (b_strategy) [0;2] (Pass one only, 0 is
# deactivated, 1 is fast and 2 is slow. Fishman0919 suggests a value of 2)
E_ABF=2

# Slow adaptive refinement of B-frames (brd_scale) [0;3] (0 is full search,
# higher is faster; only valid if b_strategy=2. Fishman0919 suggests a value of 2)
E_SBF=2

# Motion detection for B-frames (b_sensitivity) [>0] (Only valid if b_strategy=1)
E_DBF=40

# Threshold for scene change detection (sc_threshold) [−1000000000;1000000000]
# (Negative values indicate that it is more likely to insert an I-frame when it
# detects a scene change)
E_TSD=-30000

#---------------------------------------------------------------
#                      Motion estimation settings
#---------------------------------------------------------------
# Range for motion estimation (me_range) [0;9999]
E_RME=0

# Optimization of rate distortion (mbd) [0;2] (2 is the best value)
E_RDO=2

# Diamond size (and pre-pass too) (dia_size, pre_dia_size) [-99;6] (Negative
# values are for adaptive diamond)
E_DIA=-4

# Comparison function for the macroblock decision (mbcmp) [0;2000] (0 is SAD, 1
# is SSE2, 2 is SADT, +256 for chroma motion estimation, currently does not work
# (correctly) with B-frames)
E_CMB=2

# Comparison function for pre pass, full, and sub motion estimation (precmp,
# subcmp, cmp) [0;2000] (0 is SAD, 1 is SSE2, 2 is SADT, +256 for chroma motion
# estimation, currently does not work (correctly) with B-frames)
E_CMP=2

# Comparison function for frame skip (skip_cmp) [0;2000] (0 is SAD, 1 is SSE2,
# 2 is SADT, +256 for chroma motion estimation, currently does not work
# (correctly) with B-frames)
E_CMS=2

# Amount of motion predictors (last_pred) [0;99]
E_AMP=2

#---------------------------------------------------------------
#                      Other settings
#---------------------------------------------------------------
# Aspect Ratio (aspect) (4/3 or 16/9 for DVD compatibility)
E_DAR=4/3

# Frame size (s) (b up to 2500 kbps =>s=704x480 (NTSC), b greater than 2500
# kbps =>s=720x480 (NTSC))
E_SZE=720x480

# Frame rate (r) (use 25 for PAL, 24000/1001 or 30000/1001 para NTSC)
E_FPS=24000/1001

# DC precision (dc) [8;10] (b up to 1800k =>dc=8, between 1800k and 3500k =>dc=9,
# greater than 3500k =>dc=10)
E_DC=9

#---------------------------------------------------------------
#                      Matrices
#---------------------------------------------------------------
# MPEG (default matrix for any bitrate)
E_INTRA=8,16,19,22,26,27,29,34,16,16,22,24,27,29,34,37,19,22,26,27,29,34,34,38,22,22,26,27,29,34,37,40,22,26,27,29,32,35,40,48,26,27,29,32,35,40,48,58,26,27,29,34,38,46,56,69,27,29,35,38,46,56,69,83
E_INTER=16,17,18,19,20,21,22,23,17,18,19,20,21,22,23,24,18,19,20,21,22,23,24,25,19,20,21,22,23,24,26,27,20,21,22,23,25,26,27,28,21,22,23,24,26,27,28,30,22,23,24,26,27,28,30,31,23,24,25,27,28,30,31,33

# MPEG Standard (for any bitrate, the default matrix of FFMPEG, there are matrices better than this)
E_INTRA=08,16,19,22,26,27,29,34,16,16,22,24,27,29,34,37,19,22,26,27,29,34,34,38,22,22,26,27,29,34,37,40,22,26,27,29,32,35,40,48,26,27,29,32,35,40,48,58,26,27,29,34,38,46,56,69,27,29,35,38,46,56,69,83
E_INTER=16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16

# FOX New Matrix (manolito's suggestion, for bitrate>=3000k)
E_INTRA=08,08,09,09,10,10,11,11,08,09,09,10,10,11,11,12,09,09,10,10,11,11,12,12,09,10,10,11,11,12,13,13,10,10,11,11,12,13,13,14,10,11,11,12,13,13,14,15,11,11,12,13,13,14,15,15,11,12,12,13,14,15,15,16
E_INTER=08,08,09,09,10,10,11,11,08,09,09,10,10,11,11,12,09,09,10,10,11,11,12,12,09,10,10,11,11,12,13,13,10,10,11,11,12,13,13,14,10,11,11,12,13,13,14,15,11,11,12,13,13,14,15,15,11,12,12,13,14,15,15,16

# FOX Home Entertainment
E_INTRA=08,08,09,11,13,13,14,17,08,08,11,12,13,14,17,18,09,11,13,13,14,17,17,16,11,11,13,13,13,17,18,20,11,13,13,13,16,17,20,24,13,13,13,16,17,20,24,29,13,12,13,17,19,23,28,34,12,13,17,19,23,28,34,41
E_INTER=08,08,08,09,09,09,09,10,08,08,09,09,09,09,10,10,08,09,09,09,09,10,10,10,09,09,09,09,10,10,10,10,09,09,09,10,10,10,10,11,09,09,10,10,10,10,11,11,09,10,10,10,10,11,11,11,10,10,10,10,11,11,11,11

# FOX1
E_INTRA=08,08,09,11,13,13,14,17,08,08,11,12,13,14,17,18,09,11,13,13,14,17,17,19,11,11,13,13,14,17,18,20,11,13,13,14,16,17,20,24,13,13,14,16,17,20,24,29,13,13,14,17,19,23,28,34,13,14,17,19,23,28,34,41
E_INTER=08,08,08,09,09,09,09,10,08,08,09,09,09,09,10,10,08,09,09,09,09,10,10,10,09,09,09,09,10,10,10,10,09,09,09,10,10,10,10,11,09,09,10,10,10,10,11,11,09,10,10,10,10,11,11,11,10,10,10,10,11,11,11,11

# FOX2
E_INTRA=08,08,09,11,13,13,14,17,08,08,11,12,13,14,17,18,09,11,13,13,14,17,17,19,11,11,13,13,14,17,18,20,11,13,13,14,16,17,20,24,13,13,14,16,17,20,24,29,13,13,14,17,19,23,28,34,13,14,17,19,23,28,34,41
E_INTER=08,08,09,09,10,10,11,11,08,09,09,10,10,11,11,12,09,09,10,10,11,11,12,12,09,10,10,11,11,12,13,13,10,10,11,11,12,13,13,14,10,11,11,12,13,13,14,15,11,11,12,13,13,14,15,15,11,12,12,13,14,15,15,16

# FOX3
E_INTRA=08,08,09,11,13,13,14,17,08,08,11,12,13,14,17,18,09,11,13,13,14,17,17,19,11,11,13,13,14,17,18,20,11,13,13,14,16,17,20,24,13,13,14,16,17,20,24,29,13,13,14,17,19,23,28,34,13,14,17,19,23,28,34,41
E_INTER=16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16

# Didée's SixOfNine-HVS (HVS:Human Visual System, for bitrate>=3000k)
E_INTRA=08,11,12,12,13,15,16,17,11,11,12,12,14,15,16,17,12,12,13,14,15,16,17,18,12,12,14,16,17,18,19,19,13,14,15,17,19,20,20,20,15,15,16,18,20,21,22,22,16,16,17,19,21,22,23,24,17,17,18,19,20,22,24,24
E_INTER=12,11,12,12,13,14,15,16,11,11,12,12,13,14,14,16,12,12,12,13,14,15,16,17,12,12,13,15,16,17,18,18,13,13,14,16,18,19,19,20,14,14,15,17,19,20,22,22,15,14,16,18,19,22,23,24,16,16,17,18,20,22,24,24

# manono1 (the manono's favorite matrix)
E_INTRA=08,08,08,09,11,13,14,17,08,08,09,11,13,13,14,17,08,08,11,12,13,14,17,94,09,11,13,13,14,17,17,94,11,11,13,13,14,17,94,94,13,13,14,16,17,20,94,94,13,13,14,17,94,94,94,94,13,14,17,94,94,94,94,94
E_INTER=12,12,13,14,15,16,22,26,12,13,14,15,16,22,26,32,13,14,15,16,22,26,32,41,14,15,16,22,26,32,41,53,15,16,22,26,32,41,53,94,16,22,26,32,41,53,70,94,22,26,32,41,53,70,94,94,26,32,41,53,94,94,94,94

# manono2
E_INTRA=08,12,13,14,15,16,19,22,12,13,14,15,16,19,22,26,13,14,15,16,19,22,26,32,14,15,16,19,22,26,32,41,15,16,19,22,26,32,41,53,16,19,22,26,32,41,53,70,19,22,26,32,41,53,70,94,22,26,32,41,53,70,94,127
E_INTER=12,12,13,14,15,16,19,22,12,13,14,15,16,19,22,26,13,14,15,16,19,22,26,32,14,15,16,19,22,26,32,41,15,16,19,22,26,32,41,53,16,19,22,26,32,41,53,70,19,22,26,32,41,53,70,94,22,26,32,41,53,70,94,127

# manono3 (according to manono, for cases when the movie doesn't compress well at all)
E_INTRA=08,10,10,12,13,15,16,20,10,10,12,15,17,19,20,20,10,12,15,17,19,20,20,23,12,15,17,19,20,20,25,25,13,17,19,20,23,25,25,27,15,19,20,23,25,27,27,30,16,20,20,25,25,27,30,35,20,20,23,25,27,30,35,45
E_INTER=12,14,17,18,19,20,24,28,14,16,17,18,19,23,27,32,17,17,18,19,20,27,30,37,18,18,19,20,27,30,35,37,19,19,20,27,30,35,37,40,20,23,27,30,35,37,40,44,24,27,30,35,37,40,40,44,28,32,37,37,40,44,44,48

# HVS Best (for low bitrate)
E_INTRA=08,16,16,16,17,18,21,24,16,16,16,16,17,19,22,25,16,16,17,18,20,22,25,29,16,16,18,21,24,27,31,36,17,17,20,24,30,35,41,47,18,19,22,27,35,44,54,65,21,22,25,31,41,54,70,88,24,25,29,36,47,65,88,115
E_INTER=18,18,18,18,19,21,23,27,18,18,18,18,19,21,24,29,18,18,19,20,22,24,28,32,18,18,20,24,27,30,35,40,19,19,22,27,33,39,46,53,21,21,24,30,39,50,61,73,23,24,28,35,46,61,79,98,27,29,32,40,53,73,98,129

# AVAMAT7 (for low bitrate, also called AUTO-Q2)
E_INTRA=08,16,19,22,26,28,32,38,16,16,22,24,28,32,38,44,19,22,26,28,32,38,44,48,22,22,26,32,38,44,48,54,22,26,32,38,44,48,54,64,26,32,38,44,48,54,64,74,32,38,44,48,54,64,74,84,38,44,48,54,64,74,84,94
E_INTER=16,20,24,28,36,42,46,52,20,24,28,36,42,46,52,58,24,28,36,42,46,52,58,62,28,36,42,46,52,58,62,68,36,42,46,52,58,62,68,78,42,46,52,58,62,68,78,88,46,52,58,62,68,78,88,99,52,58,62,68,78,88,99,99

#---------------------------------------------------------------
#                      FFmpeg CLI
#---------------------------------------------------------------
if [ "$SOURCEFILE" == "" ] && [ "$TARGETFILE" == "" ]; then
    echo ''
    echo -pass 1 -vcodec mpeg2video -maxrate $VBV_MBR -bufsize $VBV_MBS -g $E_MIK -bf $E_MBF -bidir_refine 0 -b_strategy $E_ABF -brd_scale $E_SBF -b_sensitivity $E_DBF -dc $E_DC -q:v $E_FQ -intra_vlc true -intra_matrix $E_INTRA -inter_matrix $E_INTER -an -f mpeg2video

    echo ''
    echo -pass 2 -vcodec mpeg2video -b:v $E_BR -maxrate $VBV_MBR -bufsize $VBV_MBS -g $E_MIK -bf $E_MBF -bidir_refine 0 -sc_threshold $E_TSD -b_sensitivity $E_DBF -me_range $E_RME -mpv_flags mv0+naq -mv0_threshold 0 -mbd $E_RDO -mbcmp $E_CMB -precmp $E_CMP -subcmp $E_CMP -cmp $E_CMP -skip_cmp $E_CMS -dia_size $E_DIA -pre_dia_size $E_DIA -last_pred $E_AMP -dc $E_DC -lmin $E_MLM -mblmin $E_MBL -qmin $E_MQ -qcomp $E_VQ -intra_vlc true -intra_matrix $E_INTRA -inter_matrix $E_INTER -f mpeg2video -color_primaries 5 -color_trc 5 -colorspace 5 -color_range 1 -aspect $E_DAR -s $E_SZE

else
    # First pass
    ffmpeg -hide_banner -i "${SOURCEFILE}" -pass 1 -vcodec mpeg2video -maxrate $VBV_MBR -bufsize $VBV_MBS -g $E_MIK -bf $E_MBF -bidir_refine 0 -b_strategy $E_ABF -brd_scale $E_SBF -b_sensitivity $E_DBF -dc $E_DC -q:v $E_FQ -intra_vlc true -intra_matrix $E_INTRA -inter_matrix $E_INTER -an -f mpeg2video -y /dev/null

    # Second pass
    ffmpeg -hide_banner -i "${SOURCEFILE}" -pass 2 -vcodec mpeg2video -b:v $E_BR -maxrate $VBV_MBR -bufsize $VBV_MBS -g $E_MIK -bf $E_MBF -bidir_refine 0 -sc_threshold $E_TSD -b_sensitivity $E_DBF -me_range $E_RME -mpv_flags mv0+naq -mv0_threshold 0 -mbd $E_RDO -mbcmp $E_CMB -precmp $E_CMP -subcmp $E_CMP -cmp $E_CMP -skip_cmp $E_CMS -dia_size $E_DIA -pre_dia_size $E_DIA -last_pred $E_AMP -dc $E_DC -lmin $E_MLM -mblmin $E_MBL -qmin $E_MQ -qcomp $E_VQ -intra_vlc true -intra_matrix $E_INTRA -inter_matrix $E_INTER -f mpeg2video -color_primaries 5 -color_trc 5 -colorspace 5 -color_range 1 -aspect $E_DAR -s $E_SZE -y "${TARGETFILE}"
fi

```
