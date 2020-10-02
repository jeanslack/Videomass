#!/bin/bash
#
# Description: Update pip and youtube-dl on Videomass.AppImage
# Place this script on 'AppDir/usr/bin' with execute permissions.
# Remember, you need 'appimagetool-x86_64.AppImage' inside the same
# directory.
#

#set -x
set -e

# # building in temporary directory to keep system clean
# # use RAM disk if possible (as in: not building on CI system like Travis, and RAM disk is available)
# if [ "$CI" == "" ] && [ -d /dev/shm ]; then
#     TEMP_BASE=/dev/shm
# else
#     TEMP_BASE=/tmp
# fi

TEMP_BASE=/tmp

PYTHON_APPIMAGE=python3.8.5-cp38-cp38-manylinux1_x86_64.AppImage
PYTHON_APPIMAGE_URL=https://github.com/niess/python-appimage/releases/download/python3.8/${PYTHON_APPIMAGE}


BUILD_DIR=$(mktemp -d -p "$TEMP_BASE" videomass-AppImage-build-XXXXXX)
APP_DIR="$BUILD_DIR/AppDir"
#mkdir $APP_DIR

# make sure to clean up build dir, even if errors occur
cleanup () {
    if [ -d "$BUILD_DIR" ]; then
        rm -rf "$BUILD_DIR"
    fi
    }
trap cleanup EXIT

# Store repo root as variable
REPO_ROOT=$(dirname $(dirname $(dirname $(realpath $0))))
OLD_CWD=$(readlink -f .)

# switch to build dir
pushd "$BUILD_DIR"

# Fetch a python relocatable installation
wget -c ${PYTHON_APPIMAGE_URL}
chmod +x ${PYTHON_APPIMAGE}
./${PYTHON_APPIMAGE} --appimage-extract

mv squashfs-root AppDir

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
cp -r lib/ $APP_DIR/
cp -r usr/ $APP_DIR/

# Install requirements
$APP_DIR/AppRun -m pip install -U pip
$APP_DIR/AppRun -m pip install -U \
    -f https://extras.wxpython.org/wxPython4/extras/linux/gtk2/ubuntu-16.04/wxPython-4.1.0-cp38-cp38-linux_x86_64.whl \
        wxPython
$APP_DIR/AppRun -m pip install videomass

# Change AppRun so that it launches videomass and export shared libraries dir
sed -i -e 's|/opt/python3.8/bin/python3.8|/usr/bin/videomass|g' $APP_DIR/AppRun
sed -i -e '/export TKPATH/a # required shared libraries to run Videomass' $APP_DIR/AppRun
sed -i -e '/# required shared libraries to run Videomass/a export LD_LIBRARY_PATH="${here}/usr/lib/x86_64-linux-gnu/":$LD_LIBRARY_PATH' $APP_DIR/AppRun
sed -i -e '/export LD_LIBRARY_PATH=/a export LD_LIBRARY_PATH="${here}/lib/x86_64-linux-gnu/":$LD_LIBRARY_PATH' $APP_DIR/AppRun

# set new metainfo
cat <<EOF > $APP_DIR/usr/share/metainfo/python*.appdata.xml
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
mv $APP_DIR/usr/share/applications/python*.desktop $APP_DIR/usr/share/applications/videomass.desktop

# set new .desktop
sed -i -e 's|^Name=.*|Name=Videomass|g' $APP_DIR/usr/share/applications/*.desktop
sed -i -e 's|^Exec=.*|Exec=videomass|g' $APP_DIR/usr/share/applications/*.desktop
sed -i -e 's|^Icon=.*|Icon=videomass|g' $APP_DIR/usr/share/applications/*.desktop
sed -i -e 's|^Comment=.*|Comment=Graphical user interface for FFmpeg and youtube-dl|g' \
    $APP_DIR/usr/share/applications/*.desktop
sed -i -e 's|^Terminal=.*|Terminal=false|g' $APP_DIR/usr/share/applications/*.desktop
sed -i -e 's|^Categories=.*|Categories=AudioVideo;|g' $APP_DIR/usr/share/applications/*.desktop

# del unused *.png and *.desktop
rm -Rf $APP_DIR/usr/share/icons/hicolor/256x256
rm $APP_DIR/python.png $APP_DIR/*.desktop

# Add the new icon
mkdir -p $APP_DIR/usr/share/icons/hicolor/128x128/apps/
cp $APP_DIR/opt/python*/share/pixmaps/videomass.png \
    $APP_DIR/usr/share/icons/hicolor/128x128/apps/videomass.png

# make simlink
cd $APP_DIR
ln -s usr/share/icons/hicolor/128x128/apps/videomass.png videomass.png
ln -s usr/share/applications/videomass.desktop videomass.desktop
cd ..

# retrieve the Videomass version from the package metadata
export VERSION=$(cat $APP_DIR/opt/python*/lib/python3.8/site-packages/videomass-*.dist-info/METADATA | grep "^Version:.*" | cut -d " " -f 2)

# check appimagetool
wget -c https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage

if [ ! -x appimagetool-x86_64.AppImage ]; then
    chmod +x appimagetool-x86_64.AppImage
fi

# for any updates, copy 'appimagetool*' and 'youtube_dl_update_appimage.sh' script on bin/
cp appimagetool-x86_64.AppImage "$OLD_CWD/develop/tools/youtube_dl_update_appimage.sh" $APP_DIR/usr/bin

if [ ! -x $APP_DIR/usr/bin/youtube_dl_update_appimage.sh ]; then
chmod +x $APP_DIR/usr/bin/youtube_dl_update_appimage.sh
fi

# Convert back into an AppImage
#./appimagetool-x86_64.AppImage -s $APP_DIR/

# Now, build AppImage using linuxdeploy
export ARCH=x86_64
wget -c https://github.com/linuxdeploy/linuxdeploy/releases/download/continuous/linuxdeploy-x86_64.AppImage
chmod +x linuxdeploy*.AppImage
./linuxdeploy-x86_64.AppImage --appdir $APP_DIR --output appimage

# move built AppImage back into original CWD
mv Videomass*.AppImage "$OLD_CWD/"
