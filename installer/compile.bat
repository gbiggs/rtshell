@echo off

rem candle -ext WiXUtilExtension -dRTCTreeWheelPath="..\rtctree\dist\rtctree-4.1.0-py2-none-any.whl" -dRTSProfileWheelPath="..\rtsprofile\dist\rtsprofile-4.1.0-py2-none-any.whl" -pedantic -o rtshell.wixobj rtshell.wxs
candle -ext WiXUtilExtension -pedantic -o rtshell.wixobj rtshell.wxs
light -ext WixUtilExtension -pedantic -b ..\ rtshell.wixobj
del rtshell.wixpdb
del rtshell.wixobj
