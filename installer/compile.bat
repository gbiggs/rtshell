@echo off

rem Do this first if necessary: pip install rtshell

echo --- Building RTCTree WiX module ---
cd ../../rtctree/installer
echo --- Compiling and linking module ---
candle -pedantic -o rtctree_module.wixobj rtctree_module.wxs
light -pedantic -b ..\ rtctree_module.wixobj -out ../../rtshell/installer/rtctree.msm
del rtctree_module.wixobj

echo --- Building RTSProfile WiX module ---
cd ../../rtsprofile/installer
echo --- Compiling and linking module ---
candle -pedantic -o rtsprofile_module.wixobj rtsprofile_module.wxs
light -pedantic -b ..\ rtsprofile_module.wixobj -out ../../rtshell/installer/rtsprofile.msm
del rtsprofile_module.wixobj

echo --- Building RTShell WiX module ---
cd ../../rtshell/installer
echo --- Compiling and linking module ---
candle -ext WiXUtilExtension -pedantic -o rtshell_module.wixobj rtshell_module.wxs
light -ext WiXUtilExtension -pedantic -b ..\ rtshell_module.wixobj -out rtshell.msm
del rtshell_module.wixobj

echo --- Building RTShell installer ---
candle -ext WiXUtilExtension -pedantic -o rtshell.wixobj rtshell.wxs
light -ext WiXUtilExtension -pedantic -b ..\ rtshell.wixobj
del rtshell.wixpdb
del rtshell.wixobj
rem Do this last if necessary: pip uninstall rtshell rtctree rtsprofile
