@echo off
rem Copyright (C) 2009-2015
rem     Geoffrey Biggs
rem     RT-Synthesis Research Group
rem     Intelligent Systems Research Institute,
rem     National Institute of Advanced Industrial Science and Technology (AIST),
rem     Japan
rem     All rights reserved.
rem Licensed under the GNU Lesser General Public License version 3.
rem http://www.gnu.org/licenses/lgpl-3.0.en.html

python -c "import sys; import rtshell.rtcwd; sys.exit(rtshell.rtcwd.main(['%*']))" > settmp.bat
call settmp
del settmp.bat

