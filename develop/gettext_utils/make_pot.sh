#!/bin/bash

# Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
# Copyleft - 2024 Gianluca Pernigotto <jeanlucperni@gmail.com>
# license: GPL3
# Rev: July.05.2024
#
# PORPOSE: Create a new `videomass.pot` file with the latest strings.
#
# USAGE: ~$ cd /Videomass/source/directory
#        ~$ develop/gettext_utils/make_pot.sh

TARGET="videomass/data/locale"  # relative path to "locale" directory
POTFILE="$TARGET/videomass.pot"  # store the new .pot file here
self="$(readlink -f -- $0)"  # this file
HERE="${self%/*}"  # dirname of this file
CATALOG=$(<"${HERE}/Translation_Catalog.txt")  # read catalog file

echo -e "\nTarget directory: \033[34m\e[1m'${TARGET}'\e[0m"

cd "${TARGET}"
xgettext --width=400 --default-domain videomass ${CATALOG}

if [ $? != 0 ]; then
    echo -e '\e[1m\033[31mFailed!\e[0m'
else
    mv videomass.po videomass.pot
    echo -e "\e[1m«videomass.pot» was successfully created.\e[0m"
    echo -e "\033[32mDone!\e[0m"
fi
