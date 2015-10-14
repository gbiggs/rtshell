@echo off

rem Do this first if necessary: pip install rtshell
candle -ext WiXUtilExtension -pedantic -o rtshell.wixobj rtshell.wxs
light -ext WixUtilExtension -pedantic -b ..\ rtshell.wixobj
del rtshell.wixpdb
del rtshell.wixobj
rem Do this last if necessary: pip uninstall rtshell rtctree rtsprofile
