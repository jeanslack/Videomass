#!/bin/bash
#
# Description: Build from scratch a Videomass-*-x86_64.AppImage starting
#              from a python3.8.5-cp38-cp38m-manylinux1_x86_64.AppImage
#              or from python3.8.5-x86_64.AppImage
#
# Ideally run this inside the manylinux Docker container
# so that dependencies get bundled from that very container

set -e  # stop if error

SELF="$(readlink -f -- $0)"  # this file
MACHINE_ARCH=$(arch)
PYVERSION="python3.8.5"
OPT="squashfs-root/opt/python3.8"
USR_SHARE="squashfs-root/usr/share"

# check for architecture
if [ "${MACHINE_ARCH}" != 'x86_64' ] ; then
    echo "ERROR: architecture not supported $MACHINE_ARCH, supports x86_64 only"
    exit 1
fi

# Make directory for building
if [ -d $PWD/VIDEOMASS_APPIMAGE ]; then
    cd $PWD/VIDEOMASS_APPIMAGE
    if [ -d squashfs-root ]; then
        echo "ERROR: another 'squashfs-root' dir exists!"
        exit 1
    fi
else
    mkdir -p -m 0775 $PWD/VIDEOMASS_APPIMAGE
    cd $PWD/VIDEOMASS_APPIMAGE
fi

# Download an AppImage of Python 3.8 built for manylinux if not exist
if [ ! -f ${PYVERSION}*x86_64.AppImage ]; then
     wget -c https://github.com/jeanslack/AppImage-utils/releases/download/v1.1/python3.8.5-x86_64.AppImage
fi

# Extract this AppImage
if [ ! -x ${PYVERSION}*x86_64.AppImage ]; then
    chmod +x ${PYVERSION}*x86_64.AppImage
fi
./${PYVERSION}*x86_64.AppImage --appimage-extract

# Download required shared library
if [ ! -f libs.tar.xz ]; then
    wget -c https://github.com/jeanslack/Videomass/blob/master/develop/tools/AppImage/libs.tar.xz
fi

# extract libs archive
if [ ! -d libs ]; then
    tar -xf libs.tar.xz
fi

# copy shared libraries
cp -r libs/libpng12-0/lib squashfs-root/
cp -r libs/libjpeg-turbo8/usr/lib/x86_64-linux-gnu squashfs-root/usr/lib/
cp -r libs/libpng12-0/usr/lib/x86_64-linux-gnu squashfs-root/usr/lib/
cp -r libs/libSDL2/usr/lib/x86_64-linux-gnu squashfs-root/usr/lib/
cp -r libs/libsndio6.1/usr/lib/x86_64-linux-gnu squashfs-root/usr/lib/

# update pip
./squashfs-root/AppRun -m pip install -U pip

# Install videomass and its dependencies (excluding youtube-dl) into the extracted AppDir
if [ -f videomass-*.whl ]; then
    ./squashfs-root/AppRun -m pip install --no-deps videomass-*.whl
else
    ./squashfs-root/AppRun -m pip install --no-deps videomass
fi

# installing pypubsub
./squashfs-root/AppRun -m pip install PyPubSub

# installing wxPython4.1 binary wheel
if [ -f wxPython-4.1.0-cp38-cp38-linux_x86_64.whl ]; then
    ./squashfs-root/AppRun -m pip install wxPython-4.1.0-cp38-cp38-linux_x86_64.whl
else
    ./squashfs-root/AppRun -m pip install -U -f https://github.com/jeanslack/AppImage-utils/releases/download/v1.1/wxPython-4.1.0-cp38-cp38-linux_x86_64.whl wxPython
fi

# Change AppRun so that it launches videomass and export shared libraries dir
sed -i -e 's|/opt/python3.8/bin/python3.8|/usr/bin/videomass|g' ./squashfs-root/AppRun
sed -i -e '/export TKPATH/a # required shared libraries to run Videomass' squashfs-root/AppRun
sed -i -e '/# required shared libraries to run Videomass/a export LD_LIBRARY_PATH="${here}/usr/lib/x86_64-linux-gnu/":$LD_LIBRARY_PATH' squashfs-root/AppRun
sed -i -e '/export LD_LIBRARY_PATH=/a export LD_LIBRARY_PATH="${here}/lib/x86_64-linux-gnu/":$LD_LIBRARY_PATH' squashfs-root/AppRun

# set new metainfo
cat <<EOF > $USR_SHARE/metainfo/$PYVERSION.appdata.xml
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
mv $USR_SHARE/applications/$PYVERSION.desktop $USR_SHARE/applications/videomass.desktop

# set new .desktop
sed -i -e 's|^Name=.*|Name=Videomass|g' $USR_SHARE/applications/*.desktop
sed -i -e 's|^Exec=.*|Exec=videomass|g' $USR_SHARE/applications/*.desktop
sed -i -e 's|^Icon=.*|Icon=videomass|g' $USR_SHARE/applications/*.desktop
sed -i -e 's|^Comment=.*|Comment=Graphical user interface for FFmpeg and youtube-dl|g' $USR_SHARE/applications/*.desktop
sed -i -e 's|^Terminal=.*|Terminal=false|g' $USR_SHARE/applications/*.desktop
sed -i -e 's|^Categories=.*|Categories=AudioVideo;|g' $USR_SHARE/applications/*.desktop

# del unused *.png and *.desktop
rm -Rf $USR_SHARE/icons/hicolor/256x256
rm squashfs-root/python.png squashfs-root/*.desktop

# Add the new icon
mkdir -p $USR_SHARE/icons/hicolor/128x128/apps/
cp $OPT/share/pixmaps/videomass.png $USR_SHARE/icons/hicolor/128x128/apps/videomass.png

# make simlink
cd squashfs-root
ln -s usr/share/icons/hicolor/128x128/apps/videomass.png videomass.png
ln -s usr/share/applications/videomass.desktop videomass.desktop
cd ..

# Test that it works
#./squashfs-root/AppRun

# Convert back into an AppImage
export VERSION=$(cat $OPT/lib/python3.8/site-packages/videomass-*.dist-info/METADATA | grep "^Version:.*" | cut -d " " -f 2)

#./linuxdeploy-x86_64.AppImage --appdir squashfs-root/ --output appimage

if [ ! -f appimagetool-x86_64.AppImage ]; then
    wget -c https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage
fi

if [ ! -x appimagetool-x86_64.AppImage ]; then
    chmod +x appimagetool-x86_64.AppImage
fi

./appimagetool-x86_64.AppImage squashfs-root/

echo "exit status: " $?
