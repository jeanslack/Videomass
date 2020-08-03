#!/bin/bash
#
# Description: Build from scratch a Videomass-*-x86_64.AppImage starting
#              from a python3.7.8-cp37-cp37m-manylinux1_x86_64.AppImage
#
# Ideally run this inside the manylinux Docker container
# so that dependencies get bundled from that very container

set -e  # stop if error

PYVERSION="python3.7.8"

# Download an AppImage of Python 3.7 built for manylinux if not exist
if [ ! -e "$PYVERSION-cp37-cp37m-manylinux1_x86_64.AppImage" ];then
    wget -c https://github.com/niess/python-appimage/releases/download/python3.7/$PYVERSION-cp37-cp37m-manylinux1_x86_64.AppImage
fi

# Extract this AppImage
chmod +x python*-manylinux1_x86_64.AppImage
./python*-manylinux1_x86_64.AppImage --appimage-extract


# Make directory for shared library
mkdir -p -m 0775 squashfs-root/usr/lib/x86_64-linux-gnu/

# Download required shared library
wget https://github.com/jeanslack/AppImage-utils/releases/download/v1.0/libjbig.so.0 -P squashfs-root/usr/lib/x86_64-linux-gnu/
wget https://github.com/jeanslack/AppImage-utils/releases/download/v1.0/libjpeg.so.62 -P squashfs-root/usr/lib/x86_64-linux-gnu/

# download wxPython4.1 binary wheel
if [ ! -e "wxPython-4.1.0-cp37-cp37m-linux_x86_64.whl" ];then
    wget -c https://github.com/jeanslack/AppImage-utils/releases/download/v1.0/wxPython-4.1.0-cp37-cp37m-linux_x86_64.whl
fi

# Install videomass and its dependencies (excluding youtube-dl) into the extracted AppDir
./squashfs-root/AppRun -m pip install --no-deps videomass
./squashfs-root/AppRun -m pip install PyPubSub
./squashfs-root/AppRun -m pip install wxPython-4.1.0-cp37-cp37m-linux_x86_64.whl

# Change AppRun so that it launches videomass and export shared libraries dir
sed -i -e 's|/opt/python3.7/bin/python3.7|/usr/bin/videomass|g' ./squashfs-root/AppRun
sed -i -e '/export TKPATH/a export LD_LIBRARY_PATH="${here}/usr/lib/x86_64-linux-gnu/":$LD_LIBRARY_PATH' squashfs-root/AppRun

# Test that it works
#./squashfs-root/AppRun

# set new metainfo
rm squashfs-root/usr/share/metainfo/$PYVERSION.appdata.xml
cat <<EOF > squashfs-root/usr/share/metainfo/$PYVERSION.appdata.xml
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
mv squashfs-root/usr/share/applications/$PYVERSION.desktop squashfs-root/usr/share/applications/videomass.desktop

# set new .desktop
sed -i -e 's|^Name=.*|Name=Videomass|g' squashfs-root/usr/share/applications/*.desktop
sed -i -e 's|^Exec=.*|Exec=videomass|g' squashfs-root/usr/share/applications/*.desktop
sed -i -e 's|^Icon=.*|Icon=videomass|g' squashfs-root/usr/share/applications/*.desktop
sed -i -e 's|^Comment=.*|Comment=Graphical user interface for FFmpeg and youtube-dl|g' squashfs-root/usr/share/applications/*.desktop
sed -i -e 's|^Terminal=.*|Terminal=false|g' squashfs-root/usr/share/applications/*.desktop
sed -i -e 's|^Categories=.*|Categories=AudioVideo;|g' squashfs-root/usr/share/applications/*.desktop

# del unused *.png and *.desktop
rm -Rf squashfs-root/usr/share/icons/hicolor/256x256
rm squashfs-root/python.png squashfs-root/*.desktop

# Add icon
if [ ! -e "videomass.png" ];then
    wget https://raw.githubusercontent.com/jeanslack/Videomass/master/videomass3/art/icons/videomass.png
fi

mkdir -p squashfs-root/usr/share/icons/hicolor/128x128/apps/
mv videomass.png squashfs-root/usr/share/icons/hicolor/128x128/apps/videomass.png

# make simlink
cd squashfs-root
ln -s usr/share/icons/hicolor/128x128/apps/videomass.png videomass.png
ln -s usr/share/applications/videomass.desktop videomass.desktop
ln -s ../../opt/python3.7/share/pixmaps usr/share/pixmaps
cd ..

# Convert back into an AppImage
export VERSION=$(cat squashfs-root/opt/python3.7/lib/python3.7/site-packages/videomass-*.dist-info/METADATA | grep "^Version:.*" | cut -d " " -f 2)
wget -c https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage
chmod +x appimagetool-x86_64.AppImage
./appimagetool-x86_64.AppImage squashfs-root/
