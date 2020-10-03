#!/bin/bash
#
# Description: Build from scratch a `Videomass-*-x86_64.AppImage` starting
#              from a `python3.8.5-cp38-cp38-manylinux1_x86_64.AppImage`
#              Note that this appimage work on GTK2 toolkit only.
#
# if you plan to install extra packages extract the AppImage, e.g. as:
#
#   ./Videomass*.AppImage --appimage-extract
#   export PATH="$(pwd)/squashfs-root/usr/bin:$PATH"
#
# Ideally run this inside the manylinux Docker container
# so that dependencies get bundled from that very container
#
# Author: Gianluca Pernigoto <jeanlucperni@gmail.com>
# Update: Oct.03.2020

set -e  # stop if error

SELF="$(readlink -f -- $0)" # this file
HERE="${SELF%/*}"  # dirname
MACHINE_ARCH=$(arch)
PYTHON_APPIMAGE=python3.8.5-cp38-cp38-manylinux1_x86_64.AppImage
PYTHON_APPIMAGE_URL=https://github.com/niess/python-appimage/releases/download/python3.8/${PYTHON_APPIMAGE}
WX_PYTHON_WHEEL=wxPython-4.1.0-cp38-cp38-linux_x86_64.whl
WX_PYTHON_URL=https://extras.wxpython.org/wxPython4/extras/linux/gtk2/ubuntu-16.04/${WX_PYTHON_WHEEL}

# check for architecture
if [ "${MACHINE_ARCH}" != 'x86_64' ] ; then
    echo "ERROR: architecture not supported $MACHINE_ARCH, supports x86_64 only"
    exit 1
fi

# Make directory for building
if [ -d "$PWD/VIDEOMASS_APPIMAGE_GTK2" ]; then
    cd "$PWD/VIDEOMASS_APPIMAGE_GTK2"
    if [ -d squashfs-root ]; then
        echo "ERROR: another 'squashfs-root' dir exists!"
        exit 1
    fi
else
    mkdir -p -m 0775 "$PWD/VIDEOMASS_APPIMAGE_GTK2"
    cd "$PWD/VIDEOMASS_APPIMAGE_GTK2"
fi

# Fetch a python relocatable installation
if [ ! -f ${PYTHON_APPIMAGE} ]; then
    wget -c ${PYTHON_APPIMAGE_URL}
fi

# Extract this AppImage
if [ ! -x ${PYTHON_APPIMAGE} ]; then
    chmod +x ${PYTHON_APPIMAGE}
fi
./${PYTHON_APPIMAGE} --appimage-extract

# Download required shared library
if [ ! -d usr ] || [ ! -d lib ]; then
    wget -c http://security.ubuntu.com/ubuntu/pool/main/libp/libpng/libpng12-0_1.2.54-1ubuntu1.1_amd64.deb \
    http://security.ubuntu.com/ubuntu/pool/main/libj/libjpeg-turbo/libjpeg-turbo8_1.4.2-0ubuntu3.4_amd64.deb \
#     http://nl.archive.ubuntu.com/ubuntu/pool/universe/s/sndio/libsndio6.1_1.1.0-2_amd64.deb \
#     http://security.ubuntu.com/ubuntu/pool/universe/libs/libsdl2/libsdl2-2.0-0_2.0.4+dfsg1-2ubuntu2.16.04.2_amd64.deb

    # extract data from .deb files
    ar -x libpng12-0_1.2.54-1ubuntu1.1_amd64.deb data.tar.xz && tar -xf data.tar.xz
    ar -x libjpeg-turbo8_1.4.2-0ubuntu3.4_amd64.deb data.tar.xz && tar -xf data.tar.xz
#     ar -x libsndio6.1_1.1.0-2_amd64.deb data.tar.xz && tar -xf data.tar.xz
#     ar -x libsdl2-2.0-0_2.0.4+dfsg1-2ubuntu2.16.04.2_amd64.deb data.tar.xz && tar -xf data.tar.xz
fi

# copy shared libraries
cp -r lib/ squashfs-root/
cp -r usr/ squashfs-root/

# update pip
./squashfs-root/AppRun -m pip install -U pip

# installing wxPython4.1 binary wheel
if [ -f ${WX_PYTHON_WHEEL} ]; then
    ./squashfs-root/AppRun -m pip install ${WX_PYTHON_WHEEL}
else
    ./squashfs-root/AppRun -m pip install -U -f ${WX_PYTHON_URL} wxPython
fi

# Install videomass and its dependencies, PyPubSub, youtube_dl
if [ -f videomass-*.whl ]; then
    ./squashfs-root/AppRun -m pip install videomass-*.whl
else
    ./squashfs-root/AppRun -m pip install videomass
fi

# Change AppRun so that it launches videomass and export shared libraries dir
sed -i -e 's|/opt/python3.8/bin/python3.8|/usr/bin/videomass|g' ./squashfs-root/AppRun
sed -i -e '/export TKPATH/a # required shared libraries to run Videomass' squashfs-root/AppRun
sed -i -e '/# required shared libraries to run Videomass/a export LD_LIBRARY_PATH="${here}/usr/lib/x86_64-linux-gnu/":$LD_LIBRARY_PATH' squashfs-root/AppRun
sed -i -e '/export LD_LIBRARY_PATH=/a export LD_LIBRARY_PATH="${here}/lib/x86_64-linux-gnu/":$LD_LIBRARY_PATH' squashfs-root/AppRun

# set new metainfo
cat <<EOF > squashfs-root/usr/share/metainfo/python*.appdata.xml
<?xml version="1.0" encoding="UTF-8"?>
<component type="desktop-application">
    <id>videomass</id>
    <metadata_license>MIT</metadata_license>
    <project_license>Python-2.0</project_license>
    <name>Videomass</name>
    <summary>A Python 3.8 runtime with videomass, PyPubSub and wxPython GUI toolkit</summary>
    <description>
        <p>  A relocated Python 3.8 installation containing
             the videomass packages suite (videomass, PyPubSub and wxPython)
             and running from an AppImage.
        </p>
    </description>
    <launchable type="desktop-id">videomass.desktop</launchable>
    <url type="homepage">http://jeanslack.github.io/Videomass</url>
    <provides>
        <binary>python3.8</binary>
    </provides>
</component>
EOF

# Edit the desktop file
mv squashfs-root/usr/share/applications/python*.desktop \
    squashfs-root/usr/share/applications/videomass.desktop

# set new .desktop
sed -i -e 's|^Name=.*|Name=Videomass|g' squashfs-root/usr/share/applications/*.desktop
sed -i -e 's|^Exec=.*|Exec=videomass|g' squashfs-root/usr/share/applications/*.desktop
sed -i -e 's|^Icon=.*|Icon=videomass|g' squashfs-root/usr/share/applications/*.desktop
sed -i -e 's|^Comment=.*|Comment=Graphical user interface for FFmpeg and youtube-dl|g' \
    squashfs-root/usr/share/applications/*.desktop
sed -i -e 's|^Terminal=.*|Terminal=false|g' squashfs-root/usr/share/applications/*.desktop
sed -i -e 's|^Categories=.*|Categories=AudioVideo;|g' squashfs-root/usr/share/applications/*.desktop

# del unused *.png and *.desktop
rm -Rf squashfs-root/usr/share/icons/hicolor/256x256
rm squashfs-root/python.png squashfs-root/*.desktop

# Add the new icon
mkdir -p squashfs-root/usr/share/icons/hicolor/128x128/apps/
cp squashfs-root/opt/python*/share/pixmaps/videomass.png \
    squashfs-root/usr/share/icons/hicolor/128x128/apps/videomass.png

# make simlink
ln -sr squashfs-root/usr/share/icons/hicolor/128x128/apps/videomass.png \
    squashfs-root/videomass.png
ln -sr squashfs-root/usr/share/applications/videomass.desktop \
    squashfs-root/videomass.desktop

# retrieve the Videomass version from the package metadata
export VERSION=$(cat \
    squashfs-root/opt/python*/lib/python3.8/site-packages/videomass-*.dist-info/METADATA \
        | grep "^Version:.*" | cut -d " " -f 2)

# check appimagetool
if [ ! -f appimagetool-x86_64.AppImage ]; then
    wget -c https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage
fi

if [ ! -x appimagetool-x86_64.AppImage ]; then
    chmod +x appimagetool-x86_64.AppImage
fi

# for any updates, copy 'appimagetool*' and 'youtube_dl_update_appimage.sh' script on bin/
cp appimagetool-x86_64.AppImage "$HERE/youtube_dl_update_appimage.sh" squashfs-root/usr/bin

if [ ! -x squashfs-root/usr/bin/youtube_dl_update_appimage.sh ]; then
    chmod +x squashfs-root/usr/bin/youtube_dl_update_appimage.sh
fi

# Convert back into an AppImage with sign
./appimagetool-x86_64.AppImage -s squashfs-root/
