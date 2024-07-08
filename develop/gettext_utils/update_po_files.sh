#!/bin/bash

# Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
# Copyleft - 2024 Gianluca Pernigotto <jeanlucperni@gmail.com>
# license: GPL3
# Rev: July.05.2024
#
# PORPOSE: Updates all translation strings of videomass.po files contained in
#          in "videomass/data/locale". If `--compile` argument is given
#          it also compile MO bin files.
#
# USAGE: ~$ cd /Videomass/source/directory
#        ~$ develop/gettext_utils/update_po_files.sh [--compile]

set -e  # Exit immediately if a command exits with a non-zero status.

TARGET="videomass/data/locale"  # relative path to "locale" directory
POT="$TARGET/videomass.pot"  # pot file
COMPILE_MO=$1  # optional positional argument

echo -e "\nTarget directory: \033[34m\e[1m'${TARGET}'\e[0m"

if [ ! -f "${POT}" ]; then
    echo -e "\033[31mERROR:\e[0m File not found: videomass.pot"
    exit 1
fi

for langdirs in $(ls -d ${TARGET}/*/)
do
    PO="${langdirs}LC_MESSAGES/videomass.po"
    msgmerge --update --no-fuzzy-matching --width=400 --no-wrap $PO $POT

    if [ "${COMPILE_MO}" = '--compile' ]; then
        echo 'Now Compile the videomass.mo file because the "--compile" argument is given'
        msgfmt -c "${PO}" -o "${langdirs}LC_MESSAGES/videomass.mo"
    fi
done

echo -e "\n\e[1mSuccessful update.\e[0m"
echo -e "\033[32mDone!\e[0m"
