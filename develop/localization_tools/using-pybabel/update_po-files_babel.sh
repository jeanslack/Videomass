#!/bin/bash

# Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
# Copyleft - 2026 Gianluca Pernigotto <jeanlucperni@gmail.com>
# license: GPL3
# Rev: Nov.02.2026
#
# PORPOSE: Update all *.po files using pybabel cmd line.
#
# USAGE: ~$ cd /Videomass/source/directory
#        ~$ develop/localization_tools/using-pybabel//update_po-files_babel.sh

echo "Do you want to delete obsolete messages from po files? [Y/y - N/n] "
read obsolete

case "$obsolete" in
    "y"|"Y")
        IGNORE_OBSOLETE=--ignore-obsolete
        ;;
    "n"|"N")
        IGNORE_OBSOLETE=''
        ;;
    *)
        echo "Unknown response: '$obsolete'"
        exit 1
        ;;
esac

TARGET="videomass/data/locale"  # relative path to "locale" directory
POTFILE="$TARGET/videomass.pot"  # store the new .pot file here
#self="$(readlink -f -- $0)"  # this file
#THERE=`realpath --relative-to=${PWD} "${self%/*}"`  # relative dirname of this file

echo -e "\nTarget directory: \033[34m\e[1m'${TARGET}'\e[0m"

if [ ! -d "${TARGET}" ]; then
    echo -e "\033[31mERROR:\e[0m Directory does not exist: '${TARGET}'"
    exit 1
fi

pybabel update --domain=videomass --input-file=$POTFILE --output-dir=$TARGET --width=400 $IGNORE_OBSOLETE

# post-operation
if [[ $? -ne 0 ]]; then
    echo -e '\e[1m\033[31mFailed!\e[0m'
    exit $?
fi

echo -e "\n\e[1mPO files updated successfully.\e[0m"
echo -e "\033[32mDone!\e[0m"

