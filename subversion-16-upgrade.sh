#!/bin/bash
# -*- coding:utf-8 -*-

# Upgrade Subversion 1.4 to 1.6 for CentOS 5.x
# This scirpt is experimental.

export KANON_HOME=/opt/kanon

function not_supported {
    echo "サポートされていないOSです。"
    echo "現在サポートされいているOSは、"
    echo ""
    echo "  * CentOS 5.x (Experimental)"
    echo ""
    echo "です。"
    exit 1
}

function check_os {
    if [ ! -f /etc/redhat-release ]
    then
        not_supported
    else
        CHK=`egrep "CentOS release 5|Red Hat Enterprise Linux .* 5" /etc/redhat-release`
        if [ "$CHK" == '' ]
        then
            not_supported
        fi
    fi
}

check_os

# remove old subversion packages.
yum -y remove subversion mod_dav_svn

# Install required packages to build subversion1.6.
yum -y install autoconf libtool apr-devel apr-util-devel openssl-devel httpd-devel

# download source code and deps.
wget http://subversion.tigris.org/downloads/subversion-1.6.16.tar.bz2
wget http://subversion.tigris.org/downloads/subversion-deps-1.6.16.tar.bz2
tar -jxf subversion-1.6.16.tar.bz2
tar -jxf subversion-deps-1.6.16.tar.bz2

cd subversion-1.6.16

# set env.
source ${KANON_HOME}/bin/activate

sh ./autogen.sh

./configure \
--prefix=/opt/kanon \
--with-apr=/usr/bin/apr-1-config \
--with-apr-util=/usr/bin/apu-1-config \
--with-apxs=/usr/sbin/apxs

# Make subversion commands and libs.
make
make install

# Make python bindings for subversion.
make swig-py
make install-swig-py

# Remove old python bindings for subversion from kanon's python libs.
KANON_PYTHON_LIB=$KANON_HOME/lib/python2.6/site-packages
rm -rf $KANON_PYTHON_LIB/libsvn*
rm -rf $KANON_PYTHON_LIB/svn*

# Install new python bindings for subversion.
ln -sf $KANON_HOME/lib/svn-python/libsvn $KANON_PYTHON_LIB/libsvn
ln -sf $KANON_HOME/lib/svn-python/svn $KANON_PYTHON_LIB/svn

# settings to exclude subverion and mod_dav_svn from yum.conf.
YUM_CONF=/etc/yum.conf

SVN_PACKAGE="subversion"
MOD_DAV_SVN_PACKAGE="mod_dav_svn"
PACKAGES="${SVN_PACKAGE}, ${MOD_DAV_SVN_PACKAGE}"

EXCLUDE=`grep "^exclude=" ${YUM_CONF}`
if [ "${EXCLUDE}" = '' ]
then
    NEW_EXCLUDE="exclude=${PACKAGES}"
    echo ${NEW_EXCLUDE} >> ${YUM_CONF}
else
    EXCLUDE_SVN=`echo $EXCLUDE | grep "${SVN_PACKAGE}"`
    EXCLUDE_MOD_DAV_SVN=`echo $EXCLUDE | grep "${MOD_DAV_SVN_PACKAGE}"`
    if [ "${EXCLUDE_SVN}" = '' -a "${EXCLUDE_MOD_DAV_SVN}" = '' ]
    then
        # no exclude subversion and mod_dav_svn.
        NEW_EXCLUDE=${EXCLUDE}", ${PACKAGES}"
    elif [ "${EXCLUDE_SVN}" = '' -a "${EXCLUDE_MOD_DAV_SVN}" != '' ]
    then
        # already exclude mod_dav_svn.
        NEW_EXCLUDE=${EXCLUDE}", ${SVN_PACKAGE}"
    elif [ "${EXCLUDE_SVN}" != '' -a "${EXCLUDE_MOD_DAV_SVN}" = '' ]
    then
        # already exclude subversion.
        NEW_EXCLUDE=${EXCLUDE}", ${MOD_DAV_SVN_PACKAGE}"
    else
        # already exclude subversion and mod_dav_svn.
        exit
    fi
    sed -i -e "s/^exclude=.*/${NEW_EXCLUDE}/" ${YUM_CONF}
fi

