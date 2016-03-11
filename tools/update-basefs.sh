#!/bin/sh

## WARNING
## This sript is just for for my own convenience 
## It may not function corrently on your basefs image
##


if [ "$1" != "-y" ] ; then 
    echo "This script will update your basefs. backup it first."
    echo "then run:  $0 -y"
    exit 1
fi 


# READ docklet.conf

FS_PREFIX=/opt/docklet

BASEFS=$FS_PREFIX/local/basefs

CONF=../conf/docklet.conf

echo "Reading $CONF"

if [ -f $CONF ] ; then
    . $CONF
    BASEFS=$FS_PREFIX/local/basefs
    echo "$CONF exit, basefs=$BASEFS"
else
    echo "$CONF not exist, default basefs=$BASEFS" 
fi

if [ ! -d $BASEFS ] ; then
    echo "Checking $BASEFS: not exist, FAIL"
    exit 1
else
    echo "Checking $BASEFS: exist. "
fi

echo "[*] Copying start_jupyter.sh to $BASEFS/home/jupyter"

mkdir -p $BASEFS/home/jupyter

cp start_jupyter.sh $BASEFS/home/jupyter

echo ""

echo "[*] Changing $BASEFS/etc/network/interfaces using static"

echo "Original network/interfaces is"

cat $BASEFS/etc/network/interfaces | sed 's/^/OLD    /'

sed -i -- 's/dhcp/static/g' $BASEFS/etc/network/interfaces 

echo "[*] Setting $BASEFS/etc/resolv.conf"
cp resolv.conf $BASEFS/etc/resolvconf/resolv.conf.d/base

echo "[*] Masking console-getty.service"
chroot $BASEFS systemctl mask console-getty.service

echo "[*] Masking system-journald.service"
chroot $BASEFS systemctl mask systemd-journald.service

echo "[*] Masking system-logind.service"
chroot $BASEFS systemctl mask systemd-logind.service

echo "[*] Disabling apache2 service(if installed)"
chroot $BASEFS update-rc.d apache2 disable

echo "[*] Disabling mysql service(if installed)"
chroot $BASEFS update-rc.d mysql disable

echo "[*] Disabling nginx service(if installed)"
chroot $BASEFS update-rc.d nginx disable

echo "[*] Copying vimrc.local to $BASEFS/etc/vim/"
cp vimrc.local $BASEFS/etc/vim

echo "[*] Copying pip.conf to $BASEFS/root/.pip/"
mkdir -p $BASEFS/root/.pip/
cp pip.conf $BASEFS/root/.pip

echo "[*] Copying npmrc to $BASEFS/.npmrc"
cp npmrc $BASEFS/root/.npmrc
