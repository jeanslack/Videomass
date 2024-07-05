#!/bin/bash

# Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
# Copyleft - 2024 Gianluca Pernigotto <jeanlucperni@gmail.com>
# license: GPL3
# Rev: July.05.2024
#
# PORPOSE: Create a new `videomass.pot` file with the latest strings.
# USAGE: ~$ make_pot.sh '/path/to/locale/directory'

TARGET=$1  # locale directory
POTFILE="$TARGET/videomass.pot"  # store the new .pot file here
self="$(readlink -f -- $0)"  # this file
HERE="${self%/*}"  # dirname of this file
FILE_CATALOG=$(<"${HERE}/Translation_Catalog.txt")

if [ -z "$1" ]; then
    echo 'Missing argument: Path to directory named "locale" is required (e.g "videomass/data/locale")'
    exit 1
fi

if [ -d "${TARGET}" ] ; then
    echo "Target directory: '${TARGET}'";
else
    if [ -f "${TARGET}" ]; then
        echo "'${TARGET}' is a file";
        exit 1
    else
        echo "'${TARGET}' is not valid";
        exit 1
    fi
fi

cd "${TARGET}"
xgettext --width=400 --default-domain videomass ${FILE_CATALOG}

if [ $? != 0 ]; then
    echo 'Failed!'
else
    mv videomass.po videomass.pot
    echo "A new file 'videomass.pot' has been created successfully."
    echo "Done!"
fi
