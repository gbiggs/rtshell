#!/bin/bash

BASEDIR=$(dirname $(readlink -f "$0"))

sudo apt install subversion autoconf autotools-bin libpoco-dev
if [ ! -d "$BASEDIR/FSM4RTC" ]; then
    svn co http://svn.openrtm.org/OpenRTM-aist/branches/FSM4RTC $BASEDIR/FSM4RTC
fi
cd $BASEDIR/FSM4RTC
svn update
patch -p0 -E < $BASEDIR/setup-fsm4rtc.patch
cd OpenRTM-aist
./autogen.sh 
./configure
make -j4

## To launch the test component:
# cd src/ext/sdo/fsm4rtc_observer/test/
# ./test.sh 
