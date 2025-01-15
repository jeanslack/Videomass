#!/bin/bash

# Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
# Copyleft - 2025 Gianluca Pernigotto <jeanlucperni@gmail.com>
# license: GPL3
# Rev: July.10.2024
#
# PORPOSE: Generate a binary catalog for each locale found
#          from the TARGET directory.
#
# USAGE: ~$ cd /Videomass/source/directory
#        ~$ develop/gettext_utils/update_MO_files.sh

TARGET="videomass/data/locale"  # relative path to "locale" directory

echo -e "\nTarget directory: \033[34m\e[1m'${TARGET}'\e[0m"

if [ ! -d "${TARGET}" ]; then
    echo -e "\033[31mERROR:\e[0m Directory does not exist: '${TARGET}'"
    exit 1
fi

for langdirs in $(ls -d ${TARGET}/*/)
do
    PO="${langdirs}LC_MESSAGES/videomass.po"
    msgfmt --check "${PO}" --output-file="${langdirs}LC_MESSAGES/videomass.mo"
    if [[ $? -ne 0 ]]; then
        echo -e '\e[1m\033[31mFailed!\e[0m'
        exit $?
    fi
    echo "Compile '${langdirs}LC_MESSAGES/videomass.mo' ...OK"
done

echo -e "\n\e[1mBinary catalogs successfully generated.\e[0m"
echo -e "\033[32mDone!\e[0m"
