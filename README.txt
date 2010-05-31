rtresurrect, rtteardown, rtcryo, rtstart, rtstop
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
Systems. They use an RTSProfile file to determine what components to activate
or deactivate, the order to activate or deactivate them in, and any
preconditions for activation or deactivation of the components (for example,
activating one component after another has completed activation).

This software is developed at the National Institute of Advanced Industrial
Science and Technology. Approval number H22PRO-1088. The development was
financially supported by the New Energy and Industrial Technology Development
Organisation Project for Strategic Development of Advanced Robotics Elemental
Technologies.  This software is licensed under the Eclipse Public License -v
1.0 (EPL). See LICENSE.txt.


Requirements
------------

These tools require the rtctree-2.0 and rtsprofile-2.0 libraries.

These tools use the new string formatting operations that were introduced in
Python 2.6. It will not function with an earlier version of Python. It has not
been tested with Python 3 and it is likely that several changes will be
necessary to make it function using this version of Python.

For Ubuntu users, if you are using a version of Ubuntu prior to 9.04, you will
need to install a suitable Python version by hand. You may want to consider
upgrading to Ubuntu 9.04 or later (10.04 offers LTS).


Installation
------------

There are several methods of installation available:

1. Download the source from either the repository (see "Repository," below) or
a source archive, extract it somewhere, and run the commands from that
directory.

2. Download the source from either the repository (see "Repository," below) or
a source archive, extract it somewhere, and install it into your Python
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
   add paths to your environment variables (see step c, above).


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


State-change plans
------------------

The RTSProfile specification includes facilities for managing the change of
state of an RT System. It is possible to control the order in which components
are altered, and specify dependencies between components that prevent one
component starting before another that it may require has started.

rtstart and rtstop use this information when they start and stop systems.
rtstart uses the information contained in an "Activation" block. rtstop uses
the information contained in a "Deactivation" block. When executed, they will
build and execute a plan for changing the state of the entire system. They will
not exit until the plan completes or an error occurs.

Appending the --dry-run option will display the plan but not execute it. The
output looks similar to that shown below.

{1} Activate /localhost/ConfigSample0.rtc in execution context 0 (Required)
{2} [Order 1] Activate /localhost/Motor0.rtc in execution context 0 (Required)
{4} [Order 3/Wait 5000ms] Activate /localhost/Controller0.rtc in execution
        context 0 (Required)
{3} [Order 2/Sync to Motor0, Order 5/Sync to Controller0] Activate
        /localhost/Sensor0.rtc in execution context 0 (Required)
{5} [Order 4/After ConfigSample0's action] Activate /localhost/ConsoleIn0.rtc
        in execution context 0 (Required)

The number in braces at the beginning of each line is the action ID. These are
also displayed during execution and allow easy identification of individual
actions.

Following this there may be a value in square brackets. This indicates any
pre-conditions on the action being executed:

"Order" pre-conditions are simple sequencing. When no other conditions are
    present, actions will be executed in order of their sequence number.

"Wait" pre-conditions indicate that the specified time must pass before the
    action will be executed.

"Sync" pre-conditions prevent the action executing until the specified
    component has reached the target state. A timeout can be set on this
    occurring, to account for errors.

"After" pre-conditions are similar to "Sync" pre-conditions. The difference is
    that they wait for the specified action to be performed on the other
    component first; in other words, the action will be executed after the
    other component's action, but before confirmation that it has reached the
    target state.

The remainder of the line is a description of the action to perform.


Shell completion
----------------

If you are using a Bash-compatible shell, you can use the included completion
script to make using the commands easier. The script is installed in
${prefix}/share/rtsshell. Run the following command to load it:

 $ source bash_completion

You can add this to your ~/.bashrc file to have it loaded in every new shell
instance.


Repository
----------

The latest source is stored in a Git repository at github, available at
http://github.com/gbiggs/rtsshell. You can download it as a zip file or
tarball by clicking the "Download Source" link in the top right of the page.
Alternatively, use Git to clone the repository. This is better if you wish to
contribute patches.

 $ git clone git://github.com/gbiggs/rtsshell.git


Changelog
---------

2.0:
- Added bash-completion script.
- Added planning capability.
