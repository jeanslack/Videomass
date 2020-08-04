#!/bin/bash
#
# Description: Build from scratch a Videomass-*-x86_64.AppImage starting
#              from a python3.7.8-cp37-cp37m-manylinux1_x86_64.AppImage
#
# Ideally run this inside the manylinux Docker container
# so that dependencies get bundled from that very container

set -e  # stop if error

MACHINE_ARCH=$(arch)
PYVERSION="python3.7.8"
OPT="squashfs-root/opt/python3.7"
USR_SHARE="squashfs-root/usr/share"

if [ "${MACHINE_ARCH}" != 'x86_64' ] ; then
    echo "ERROR: architecture not supported $MACHINE_ARCH, supports x86_64 only"
    exit 1
fi

if [ -d "squashfs-root" ]; then
    echo "ERROR: another 'squashfs-root' dir exists!"
    exit 1
fi

# Download an AppImage of Python 3.7 built for manylinux if not exist
if [ ! -f "$PYVERSION-cp37-cp37m-manylinux1_x86_64.AppImage" ]; then
    wget -c https://github.com/niess/python-appimage/releases/download/python3.7/${PYVERSION}-cp37-cp37m-manylinux1_x86_64.AppImage
fi

# Extract this AppImage
if [ ! -x "python*-manylinux1_x86_64.AppImage" ]; then
    chmod +x python*-manylinux1_x86_64.AppImage
fi
./python*-manylinux1_x86_64.AppImage --appimage-extract

# Make directory for shared library
mkdir -p -m 0775 squashfs-root/usr/lib/x86_64-linux-gnu/

# Download required shared library
wget https://github.com/jeanslack/AppImage-utils/releases/download/\
v1.0/libjbig.so.0 -P squashfs-root/usr/lib/x86_64-linux-gnu/
wget https://github.com/jeanslack/AppImage-utils/releases/download/\
v1.0/libjpeg.so.62 -P squashfs-root/usr/lib/x86_64-linux-gnu/

# download wxPython4.1 binary wheel
if [ ! -f "wxPython-4.1.0-cp37-cp37m-linux_x86_64.whl" ]; then
    wget -c https://github.com/jeanslack/AppImage-utils/releases/download/\
    v1.0/wxPython-4.1.0-cp37-cp37m-linux_x86_64.whl
fi

# Install videomass and its dependencies (excluding youtube-dl) into the extracted AppDir
./squashfs-root/AppRun -m pip install --no-deps videomass
./squashfs-root/AppRun -m pip install PyPubSub
./squashfs-root/AppRun -m pip install wxPython-4.1.0-cp37-cp37m-linux_x86_64.whl

# Change AppRun so that it launches videomass and export shared libraries dir
sed -i -e 's|/opt/python3.7/bin/python3.7|/usr/bin/videomass|g' ./squashfs-root/AppRun
sed -i -e '/export TKPATH/a export LD_LIBRARY_PATH="${here}/usr/lib/x86_64-linux-gnu/":$LD_LIBRARY_PATH' squashfs-root/AppRun

# set new metainfo
cat <<EOF > $USR_SHARE/metainfo/$PYVERSION.appdata.xml
<?xml version="1.0" encoding="UTF-8"?>
<component type="desktop-application">
    <id>videomass</id>
    <metadata_license>MIT</metadata_license>
    <project_license>Python-2.0</project_license>
    <name>Videomass</name>
    <summary>A Python 3.7 runtime with videomass, PyPubSub and wxPython</summary>
    <description>
        <p>  A relocated Python 3.7 installation containing
             the videomass packages suite (videomass, PyPubSub and wxPython)
             and running from an AppImage.
        </p>
    </description>
    <launchable type="desktop-id">videomass.desktop</launchable>
    <url type="homepage">http://jeanslack.github.io/Videomass</url>
    <provides>
        <binary>python3.7</binary>
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
ln -s ../../opt/python3.7/share/pixmaps usr/share/pixmaps
cd ..

# Test that it works
#./squashfs-root/AppRun

# Convert back into an AppImage
export VERSION=$(cat $OPT/lib/python3.7/site-packages/videomass-*.dist-info/METADATA | grep "^Version:.*" | cut -d " " -f 2)

if [ ! -f "appimagetool-x86_64.AppImage" ]; then
    wget -c https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage
fi

if [ ! -x "appimagetool-x86_64.AppImage" ]; then
    chmod +x appimagetool-x86_64.AppImage
fi

#./appimagetool-x86_64.AppImage squashfs-root/
