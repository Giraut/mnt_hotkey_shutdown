#!/bin/sh

# Directories and files
BUILDSCRIPTPATH=$(realpath "$0")
BUILDSCRIPTDIR=$(dirname ${BUILDSCRIPTPATH})
SRC=$(realpath ${BUILDSCRIPTDIR}/../..)
PKGSRC=${BUILDSCRIPTDIR}/mnt-hotkey-shutdown
VERSION=$(grep -E "^.*Version [0-9]+\.[0-9]+\.[0-9]$" ${SRC}/README.md | sed -e "s/^.*Version //")
PKGBUILD=${PKGSRC}-${VERSION}-0_all
PKG=${PKGBUILD}.deb

echo VERSION: ${VERSION}

# Create a fresh skeleton package build directory
rm -rf ${PKGBUILD}
cp -a ${PKGSRC} ${PKGBUILD}

# Create empty directory structure
mkdir -p ${PKGBUILD}/lib/systemd/system
mkdir -p ${PKGBUILD}/usr/local/bin
mkdir -p ${PKGBUILD}/usr/share/doc/mnt_hotkey_shutdown/images

# Populate the package build directory with the source files
install -m 644 ${SRC}/README.md ${PKGBUILD}/usr/share/doc/mnt_hotkey_shutdown
install -m 644 ${SRC}/images/mnt_hotkey_shutdown-bezel_foam_pads.jpg ${PKGBUILD}/usr/share/doc/mnt_hotkey_shutdown/images
install -m 644 ${SRC}/LICENSE ${PKGBUILD}/usr/share/doc/mnt_hotkey_shutdown
install -m 755 ${SRC}/mnt_hotkey_shutdown.py ${PKGBUILD}/usr/local/bin
install -m 644 ${SRC}/mnt_hotkey_shutdown.service ${PKGBUILD}/lib/systemd/system

# Set the version in the control file
sed -i "s/^Version:.*\$/Version: ${VERSION}/" ${PKGBUILD}/DEBIAN/control

# Fixup permissions
find ${PKGBUILD} -type d -exec chmod 755 {} \;
chmod 644 ${PKGBUILD}/DEBIAN/conffiles
chmod 644 ${PKGBUILD}/DEBIAN/control
chmod 755 ${PKGBUILD}/DEBIAN/postinst
chmod 755 ${PKGBUILD}/DEBIAN/postrm
chmod 755 ${PKGBUILD}/DEBIAN/preinst
chmod 755 ${PKGBUILD}/DEBIAN/prerm
chmod 644 ${PKGBUILD}/usr/share/doc/mnt_hotkey_shutdown/copyright

# Build the .deb package
fakeroot dpkg -b ${PKGBUILD} ${PKG}
