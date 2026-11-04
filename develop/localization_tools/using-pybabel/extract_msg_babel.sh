#!/bin/bash

# Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
# Copyleft - 2026 Gianluca Pernigotto <jeanlucperni@gmail.com>
# license: GPL3
# Rev: Nov.02.2026
#
# PORPOSE: Extract all messages and update the .*pot file using pybabel cmd line.
#
# USAGE: ~$ cd /Videomass/source/directory
#        ~$ develop/localization_tools/using-pybabel//extract_msg_babel.sh

echo "Type the version of Videomass you intend to work with, (i.e 6.1.22): "
read version

PROJECT="Videomass"
TARGET="videomass/data/locale"  # relative path to "locale" directory
INPUTDIRS="videomass"
POTFILE="$TARGET/videomass.pot"  # store the new .pot file here
#self="$(readlink -f -- $0)"  # this file
#THERE=`realpath --relative-to=${PWD} "${self%/*}"`  # relative dirname of this file
VERSION="$version"

echo -e "\nTarget directory: \033[34m\e[1m'${TARGET}'\e[0m"

if [ ! -d "${TARGET}" ]; then
    echo -e "\033[31mERROR:\e[0m Directory does not exist: '${TARGET}'"
    exit 1
fi

pybabel extract --width 400 --project $PROJECT --version $VERSION --input-dirs=$INPUTDIRS --output-file=$POTFILE

# post-operation
if [[ $? -ne 0 ]]; then
    echo -e '\e[1m\033[31mFailed!\e[0m'
    exit $?
fi
echo "Create '${TARGET}/videomass.pot' ...OK"

echo -e "\n\e[1mPOT file created successfully.\e[0m"
echo -e "\033[32mDone!\e[0m"

