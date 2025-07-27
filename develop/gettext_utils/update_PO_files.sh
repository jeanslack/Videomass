#!/bin/bash

# Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
# Copyleft - 2025 Gianluca Pernigotto <jeanlucperni@gmail.com>
# license: GPL3
# Rev: July.10.2024
#
# PORPOSE: Updates all translation strings of videomass.po files
#          located in "videomass/data/locale" .
#
# USAGE: ~$ cd /Videomass/source/directory
#        ~$ develop/gettext_utils/update_po_files.sh

TARGET="videomass/data/locale"  # relative path to "locale" directory
POT="$TARGET/videomass.pot"  # pot file

echo -e "\nTarget directory: \033[34m\e[1m'${TARGET}'\e[0m"

if [ ! -d "${TARGET}" ]; then
    echo -e "\033[31mERROR:\e[0m Directory does not exist: '${TARGET}'"
    exit 1
fi

if [ ! -f "${POT}" ]; then
    echo -e "\033[31mERROR:\e[0m File not found: '${POT}'"
    exit 1
fi

for langdirs in $(ls -d ${TARGET}/*/)
do
    PO="${langdirs}LC_MESSAGES/videomass.po"
    msgmerge --update --no-fuzzy-matching --width=400 --no-wrap --quiet --no-location $PO $POT
    if [[ $? -ne 0 ]]; then
        echo -e '\e[1m\033[31mFailed!\e[0m'
        exit $?
    fi
    # remove obsolete strings
    msgattrib --no-obsolete --width=400 --no-wrap --no-location $PO > temp.po
    \cp -rf temp.po $PO
    \rm test.po
    echo "Update '${langdirs}LC_MESSAGES/videomass.po' ...OK"
done

echo -e "\n\e[1mSuccessful update from POT file.\e[0m"
echo -e "\033[32mDone!\e[0m"
