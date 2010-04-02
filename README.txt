rtresurrect, rtteardown, rtcryo
===============================================================================

rtresurrect is a command-line tool for restoring an RT system as described
using the RTSProfile specification. It can restore all connections, restore
configuration settings, and set the active configuration sets. It is able to
ignore missing components that are not explicitly marked as required, as well
as not make any connections involving missing components.

rtteardown is a command-line tool that uses an RTSProfile to destroy an RT
System. It removes all connections specified in the RTSProfile.

rtcryo is a command-line tool for preserving an existing RT System in an
RTSProfile file. It will examine all the components it finds and preserve them,
their connections and their configurations into a single RTSProfile-format
file.

rtstart and rtstop are command-line tools for starting and stopping entire RT
Systems. They use an RTSProfile file to determine what components to start or
stop, the order to start or stop them in, and any preconditions for starting
and stopping the components (for example, starting one component five seconds
after another has completed activation).

This software is developed at the National Institute of Advanced Industrial
Science and Technology. Approval number H22PRO-1088. The development was
financially supported by the New Energy and Industrial Technology Development
Organisation Project for Strategic Development of Advanced Robotics Elemental
Technologies.  This software is licensed under the Eclipse Public License -v
1.0 (EPL). See LICENSE.txt.


Requirements
------------

These tools require the rtctree and rtsprofile libraries.

These tools use the new string formatting operations that were introduced in
Python 2.6. It will not function with an earlier version of Python. It has not
been tested with Python 3 and it is likely that several changes will be
necessary to make it function using this version of Python.


Installation
------------

There are several methods of installation available:

1. Download the source (either from the repository or a source archive),
extract it somewhere, and run the commands from that directory.

2. Download the source (either from the repository or a source archive),
extract it somewhere, and use distutils to install it into your Python
distribution:

 a. Extract the source, e.g. to a directory /home/blag/src/rtsshell

 b. Run setup.py to install rtsshell to your default Python installation:

    $ python setup.py install

 c. If necessary, set environment variables. These should be set by default,
    but if not you will need to set them yourself. On Windows, you will need to
    ensure that your Python site-packages directory is in the PYTHONPATH
    variable and the Python scripts directory is in the PATH variable.
    Typically, these will be something like C:\Python26\Lib\site-packages\ and
    C:\Python26\Scripts\, respectively (assuming Python 2.6 installed in
    C:\Python26\).

3. Use the Windows installer. This will perform the same job as running
   setup.py (see #2), but saves opening a command prompt. You may still need to
   add paths to your environment variables.


Usage - rtresurrect
-------------------

Run rtresurrect.py, passing it the location of an RTSProfile specification
file in a format understood by the rtsprofile library (typically XML or YAML):

./rtresurrect.py my_rtsystem.xml

To preview what actions will be taken before performing them, use the --dry-run
option. This will cause the actions to be printed, but not performed, so you
can check that they are correct.


Usage - rtstart
-------------------

Run rtstart.py, passing it the location of an RTSProfile specification file in
a format understood by the rtsprofile library (typically XML or YAML):

./rtstart.py my_rtsystem.xml

To preview what actions will be taken before performing them, use the --dry-run
option. This will cause the actions to be printed, but not performed, so you
can check that they are correct.


Usage - rtstop
-------------------

Run rtstop.py, passing it the location of an RTSProfile specification file in a
format understood by the rtsprofile library (typically XML or YAML):

./rtstop.py my_rtsystem.xml

To preview what actions will be taken before performing them, use the --dry-run
option. This will cause the actions to be printed, but not performed, so you
can check that they are correct.


Usage - rtteardown
------------------

Run rtteardown.py, passing it the location of an RTSProfile specification file
in a format understood by the rtsprofile library (typically XML or YAML):

./rtteardown.py my_rtsystem.xml

To preview what actions will be taken before performing them, use the --dry-run
option. This will cause the actions to be printed, but not performed, so you
can check that they are correct.


Usage - rtcryo
--------------

Run rtcryo.py, passing it the name of the file to save the system to:

./rtcryo.py my_new_rtsystem.xml

rtcryo will examine the RTCTree that it creates in order to find the system to
save. See the rtctree documentation for details on how that library finds
components.


Shell completion
----------------

If you are using a Bash-compatible shell, you can use the included completion
script to make using the commands easier. The script is installed in
${prefix}/share/rtsshell. Run the following command to load it:

 $ source bash_completion

You can add this to your ~/.bashrc file to have it loaded in every new shell
instance.

