#!/bin/bash

# Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
# Copyleft - 2025 Gianluca Pernigotto <jeanlucperni@gmail.com>
# license: GPL3
# Rev: July.28.2025
#
# PORPOSE: Create a new `videomass.pot` file with the latest strings.
#
# USAGE: ~$ cd /Videomass/source/directory
#        ~$ develop/gettext_utils/make_pot.sh

TARGET="videomass/data/locale"  # relative path to "locale" directory
POTFILE="$TARGET/videomass.pot"  # store the new .pot file here
self="$(readlink -f -- $0)"  # this file
THERE=`realpath --relative-to=${PWD} "${self%/*}"`  # relative dirname of this file
CATALOG="${THERE}/File_Catalog.txt"

echo -e "\nTarget directory: \033[34m\e[1m'${TARGET}'\e[0m"

if [ ! -d "${TARGET}" ]; then
    echo -e "\033[31mERROR:\e[0m Directory does not exist: '${TARGET}'"
    exit 1
fi

if [ ! -f "${CATALOG}" ]; then
    echo -e "\033[31mERROR:\e[0m File not found: '${CATALOG}'"
    exit 1
fi

DATA=$(<"${CATALOG}")  # read catalog data

cd "${TARGET}"
#xgettext --width=400 --default-domain videomass ${DATA}
pygettext3 --no-location --width=400 -v -o videomass.pot $DATA

# # post-operation
# mv videomass.po videomass.pot
if [[ $? -ne 0 ]]; then
    echo -e '\e[1m\033[31mFailed!\e[0m'
    exit $?
fi
echo "Create '${TARGET}/videomass.pot' ...OK"

echo -e "\n\e[1mPOT file created successfully.\e[0m"
echo -e "\033[32mDone!\e[0m"

