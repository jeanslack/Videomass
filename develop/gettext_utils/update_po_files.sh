#!/bin/bash

# Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
# Copyleft - 2024 Gianluca Pernigotto <jeanlucperni@gmail.com>
# license: GPL3
# Rev: July.04.2024
#
# PORPOSE: Updates all translation strings of videomass.po files contained in
#          a given directory (usually "videomass/data/locale"). It accept
#          absolute or relative path names. If the optional `compile=true` 
#          argument is given, it also compiles the MO bin files .
#
# USAGE: ~$ update_po_files.sh "/path/to/locale/directory" [compile=true]

TARGET=$1
POTFILE="$TARGET/videomass.pot"
COMPILE_MO_BIN=$2

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

if [ ! -f "${POTFILE}" ]; then
    echo "File not found: videomass.pot"
    exit 1
fi

for langdirs in $(ls -d ${TARGET}/*/)
do
    PO="${langdirs}LC_MESSAGES/videomass.po"
    msgmerge --update $PO $POTFILE
    if [ "${COMPILE_MO_BIN}" = 'compile=true' ]; then
        echo "Now compile videomass.mo file because compile=true"
        msgfmt -c "${PO}" -o "${langdirs}LC_MESSAGES/videomass.mo"
    fi
done

if [ $? != 0 ]; then
    echo 'Failed!'
else
    echo "All PO files was updated successfully."
    echo "Done!"
fi
