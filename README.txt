rtshell
==============================================================================

rtshell provides commands used to manage individual RT components and managers,
as well as complete RT Systems. It can be used with the OpenRTM-aist middleware
or middlewares that use a compatible CORBA-based introspection system.

Many of the commands allow components and managers running on nameservers to be
treated like a file system. Directories can be entered, components can be cat'd
and activated/deactivated/reset, connections made and removed, and so on.

Other commands are used in conjunction with RtsProfile XML/YAML files to manage
complete RT Systems. These are rtresurrect, rtteardown, rtcryo, rtstart and
rtstop.

The commands are aimed at users of OpenRTM-aist who wish to manage components
on low-resource systems, systems where a GUI is not available (particularly
where no network connection is available to manage components from another
computer), as well as those who face other difficulties using RTSystemEditor.
Being familiar with using a command-line is a benefit when using these commands
of rtshell.

This software is developed at the National Institute of Advanced Industrial
Science and Technology. Approval number H22PRO-1135/H22PRO-1136. The
development was financially supported by the New Energy and Industrial
Technology Development Organisation Project for Strategic Development of
Advanced Robotics Elemental Technologies.  This software is licensed under the
Eclipse Public License -v 1.0 (EPL). See LICENSE.txt.


Requirements
------------

rtshell requires rtctree 2.0. It must be installed for the commands to
function.

The commands that work with RtsProfile files require rtsprofile 2.0. It must be
installed for these commands to function/

rtshell uses the new string formatting operations that were introduced in
Python 2.6. It will not function with an earlier version of Python. It has not
been tested with Python 3 and it is likely that several changes will be
necessary to make it function using this version of Python.

rtprint and rtinject require the Python version of OpenRTM-aist.

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

 a. Extract the source, e.g. to a directory ~/rtshell
 b. Run setup.py to install rtshell to your default Python installation:

    $ python setup.py install

 c. If necessary, set environment variables. These should be set by default,
    but if not you will need to set them yourself. On Windows, you will need to
    ensure that your Python site-packages directory is in the PYTHONPATH
    variable and the Python scripts directory is in the PATH variable.
    Typically, these will be something like C:\Python26\Lib\site-packages\
    and C:\Python26\Scripts\, respectively (assuming Python 2.6 installed in
    C:\Python26\).

3. Use the Windows installer. This will perform the same job as running
setup.py (see #2), but saves opening a command prompt. You may still need to
add paths to your environment variables (see step c, above).

4. In non-Windows operating systems, you must source the shell support file to
gain full functionaliy. Amongst other things, rtcwd will not work without
sourcing this file. You can find this file at
${prefix}/share/rtshell/shell_support (${prefix} is the directory where you
installed rtshell). You can source it by running the following command
(assuming rtshell has been installed to /usr/local):

 source /usr/local/share/rtshell/shell_support

So that you don't have to run this command every time you open a terminal, you
can add it to your shell's startup file. For example, if you are using a bash
shell and installed rtshell to /usr/local, add the following line to the
.bashrc file in your home directory:

 source /usr/local/share/rtshell/shell_support


Component management tutorial
-----------------------------

This section demonstrates using the component management commands in a variety
of ways. It does not illustrate every feature of every command, but should give
you an idea of what is possible.

Comments begin with a #

# Set the RTCTREE_NAMESERVERS environment variable
# This is not necessary, but it makes things easier when specifying absolute
# paths.
$ export RTCTREE_NAMESERVERS=localhost

# rtpwd prints the current working directory. We are still in the root dir.
$ rtpwd
/

# Only one name server has been added to RTCTREE_NAMESERVERS, so there is
# only one directory in the root dir.
$ rtls
localhost/

# Use rtcwd to change directories.
$ rtcwd localhost

# rtls displays the files and directories in specified path, or the current
# working directory if no path is specified. Just like 'ls'.
$ rtls
Clusterer0.rtc  Hokuyo_AIST0.rtc  kenroke.host_cxt/

# A long listing is available as well, giving more information, such as
# component state. Use this with the 'watch' command on Linux to monitor
# a component continuously (e.g. 'watch -n 10 rtls -l').
$ rtls -l
Inactive  2/0  1/0  1/0  0/0  Clusterer0.rtc
Inactive  4/0  0/0  3/0  1/0  Hokuyo_AIST0.rtc
-         -    -    -    -    kenroke.host_cxt

# Changing directory to a sub-directory of the name server.
$ rtcwd kenroke.host_cxt
$ rtpwd
/localhost/kenroke.host_cxt

# There are lots more components here.
$ rtls
Motor0.rtc  ConfigSample0.rtc  SequenceOutComponent0.rtc  ConsoleIn0.rtc  SequenceInComponent0.rtc  Controller0.rtc  Sensor0.rtc  manager.mgr  MyServiceConsumer0.rtc  MyServiceProvider0.rtc  ConsoleOut0.rtc

# rtcat is used to display component information, such as its profile,
# execution contexts, and ports.
$ rtcat ConsoleIn0.rtc
ConsoleIn0.rtc  Inactive
  Category       example
  Description    Console input component
  Instance name  ConsoleIn0
  Parent
  Type name      ConsoleIn
  Vendor         Noriaki Ando, AIST
  Version        1.0
 +Execution Context 0
 +DataOutPort: out

# Items with a '+' beside them indicate that more information is available if
# a longer listing is used.
$ rtcat ConsoleIn0.rtc -l
ConsoleIn0.rtc  Inactive
  Category       example
  Description    Console input component
  Instance name  ConsoleIn0
  Parent
  Type name      ConsoleIn
  Vendor         Noriaki Ando, AIST
  Version        1.0
 -Execution Context 0
    State  Running
    Kind   Periodic
    Rate   1000.0
 -DataOutPort: out
    dataport.data_type          TimedLong
    dataport.dataflow_type      push
    dataport.interface_type     corba_cdr
    dataport.subscription_type  flush,new,periodic
    port.port_type              DataOutPort

# rtcon is the tool used to connect two ports together. It works for both data
# ports and service ports.
$ rtcon ConsoleIn0.rtc:out ConsoleOut0.rtc:in

# Notice that the 'out' port is now connected to a port on another component.
$ rtcat ConsoleIn0.rtc -l
ConsoleIn0.rtc  Inactive
  Category       example
  Description    Console input component
  Instance name  ConsoleIn0
  Parent
  Type name      ConsoleIn
  Vendor         Noriaki Ando, AIST
  Version        1.0
 -Execution Context 0
    State  Running
    Kind   Periodic
    Rate   1000.0
 -DataOutPort: out
    dataport.data_type          TimedLong
    dataport.dataflow_type      push
    dataport.interface_type     corba_cdr
    dataport.subscription_type  flush,new,periodic
    port.port_type              DataOutPort
   +Connected to  /localhost/kenroke.host_cxt/ConsoleOut0.rtc:in

# Even more information is available using --ll.
$ rtcat ConsoleIn0.rtc --ll
ConsoleIn0.rtc  Inactive
  Category       example
  Description    Console input component
  Instance name  ConsoleIn0
  Parent
  Type name      ConsoleIn
  Vendor         Noriaki Ando, AIST
  Version        1.0
 -Execution Context 0
    State  Running
    Kind   Periodic
    Rate   1000.0
 -DataOutPort: out
    dataport.data_type          TimedLong
    dataport.dataflow_type      push
    dataport.interface_type     corba_cdr
    dataport.subscription_type  flush,new,periodic
    port.port_type              DataOutPort
   -Connected to  /localhost/kenroke.host_cxt/ConsoleOut0.rtc:in
      Name                        out_in
      ID                          cb196ab9-5114-4f0b-9685-29ae86697613
      dataport.subscription_type  flush
      dataport.interface_type     corba_cdr
      dataport.dataflow_type      push
      dataport.data_type          TimedLong

# A data port can be connected to many other ports at once.
$ rtcon ConsoleIn0.rtc:out SequenceInComponent0.rtc:Long
$ rtcat ConsoleIn0.rtc -l
ConsoleIn0.rtc  Inactive
  Category       example
  Description    Console input component
  Instance name  ConsoleIn0
  Parent
  Type name      ConsoleIn
  Vendor         Noriaki Ando, AIST
  Version        1.0
 -Execution Context 0
    State  Running
    Kind   Periodic
    Rate   1000.0
 -DataOutPort: out
    dataport.data_type          TimedLong
    dataport.dataflow_type      push
    dataport.interface_type     corba_cdr
    dataport.subscription_type  flush,new,periodic
    port.port_type              DataOutPort
   +Connected to  /localhost/kenroke.host_cxt/ConsoleOut0.rtc:in
   +Connected to  /localhost/kenroke.host_cxt/SequenceInComponent0.rtc:Long

# The long directory listing shows more than just the component name. It also
# shows the component state and the state of its ports. The columns of numbers
# indicate the total number of ports, number of input ports, number of output
# ports and number of service ports. The number before the slash is the total,
# the number after the slash is the number that are connected. Notice that
# ConsoleIn0.rtc has one connected port.
$ rtls -l
Inactive  2/0  1/0  1/0  0/0  Motor0.rtc
Active    0/0  0/0  0/0  0/0  ConfigSample0.rtc
Inactive  8/0  0/0  8/0  0/0  SequenceOutComponent0.rtc
Inactive  1/1  0/0  1/1  0/0  ConsoleIn0.rtc
Inactive  8/1  8/1  0/0  0/0  SequenceInComponent0.rtc
Inactive  2/0  1/0  1/0  0/0  Controller0.rtc
Inactive  2/0  1/0  1/0  0/0  Sensor0.rtc
-         -    -    -    -    manager.mgr
Inactive  1/0  0/0  0/0  1/0  MyServiceConsumer0.rtc
Inactive  1/0  0/0  0/0  1/0  MyServiceProvider0.rtc
Inactive  1/1  1/1  0/0  0/0  ConsoleOut0.rtc

# rtact is used to activate components. It's siblings are rtdeact and rtreset.
$ rtact ConsoleIn0.rtc
$ rtact ConsoleOut0.rtc
$ rtact SequenceInComponent0.rtc

# The state of these three components has changed to 'Active'. If your
# terminal supports colour, the state will be colourised accordingly.
$ rtls -l
Inactive  2/0  1/0  1/0  0/0  Motor0.rtc
Active    0/0  0/0  0/0  0/0  ConfigSample0.rtc
Inactive  8/0  0/0  8/0  0/0  SequenceOutComponent0.rtc
Active    1/1  0/0  1/1  0/0  ConsoleIn0.rtc
Active    8/1  8/1  0/0  0/0  SequenceInComponent0.rtc
Inactive  2/0  1/0  1/0  0/0  Controller0.rtc
Inactive  2/0  1/0  1/0  0/0  Sensor0.rtc
-         -    -    -    -    manager.mgr
Inactive  1/0  0/0  0/0  1/0  MyServiceConsumer0.rtc
Inactive  1/0  0/0  0/0  1/0  MyServiceProvider0.rtc
Active    1/1  1/1  0/0  0/0  ConsoleOut0.rtc

# To remove a connection, use rtdis. You can remove a connection between two
# specific ports.
$ rtdis ConsoleIn0.rtc:out ConsoleOut0.rtc:in

# Notice that one of the connections shown earlier is now gone.
$ rtcat ConsoleIn0.rtc -l
ConsoleIn0.rtc  Active
  Category       example
  Description    Console input component
  Instance name  ConsoleIn0
  Parent
  Type name      ConsoleIn
  Vendor         Noriaki Ando, AIST
  Version        1.0
 -Execution Context 0
    State  Running
    Kind   Periodic
    Rate   1000.0
 -DataOutPort: out
    dataport.data_type          TimedLong
    dataport.dataflow_type      push
    dataport.interface_type     corba_cdr
    dataport.subscription_type  flush,new,periodic
    port.port_type              DataOutPort
   +Connected to  /localhost/kenroke.host_cxt/SequenceInComponent0.rtc:Long

# You can also disconnect all connections from a component at once.
# Disconnecting all connections to a single port is possible as well by
# specifying that port in the argument, e.g. 'ConsoleIn0.rtc:out'.
$ rtdis ConsoleIn0.rtc

# All connections are now gone.
$ rtcat ConsoleIn0.rtc -l
ConsoleIn0.rtc  Active
  Category       example
  Description    Console input component
  Instance name  ConsoleIn0
  Parent
  Type name      ConsoleIn
  Vendor         Noriaki Ando, AIST
  Version        1.0
 -Execution Context 0
    State  Running
    Kind   Periodic
    Rate   1000.0
 -DataOutPort: out
    dataport.data_type          TimedLong
    dataport.dataflow_type      push
    dataport.interface_type     corba_cdr
    dataport.subscription_type  flush,new,periodic
    port.port_type              DataOutPort

# Deactivate components using rtdeact.
$ rtdeact ConsoleOut0.rtc
$ rtdeact SequenceInComponent0.rtc
$ rtls -l
Inactive  2/0  1/0  1/0  0/0  Motor0.rtc
Active    0/0  0/0  0/0  0/0  ConfigSample0.rtc
Inactive  8/0  0/0  8/0  0/0  SequenceOutComponent0.rtc
Active    1/0  0/0  1/0  0/0  ConsoleIn0.rtc
Inactive  8/0  8/0  0/0  0/0  SequenceInComponent0.rtc
Inactive  2/0  1/0  1/0  0/0  Controller0.rtc
Inactive  2/0  1/0  1/0  0/0  Sensor0.rtc
-         -    -    -    -    manager.mgr
Inactive  1/0  0/0  0/0  1/0  MyServiceConsumer0.rtc
Inactive  1/0  0/0  0/0  1/0  MyServiceProvider0.rtc
Inactive  1/0  1/0  0/0  0/0  ConsoleOut0.rtc

# rtcwd works much like the normal 'cd' command.
$ rtcwd ..
$ rtpwd
/localhost
$ rtcwd
$ rtpwd
/

# rtls works much like the normal 'ls' command. You can give it a path to list
# instead of listing the current directory.
$ rtls localhost
Clusterer0.rtc  Hokuyo_AIST0.rtc  kenroke.host_cxt/

# Paths are relative to the current directory, unless they begin with / (\ on
# Windows). They can be many levels deep and may point to directories,
# managers or components.
$ rtcwd localhost/kenroke.host_cxt
$ rtpwd
/localhost/kenroke.host_cxt

# Manage configuration sets and parameters using rtconf. The default mode is
# to list the configuration sets.
$ rtconf ConfigSample0.rtc
+default*

# The long format lists the parameters of each set, as well.
$ rtconf ConfigSample0.rtc -l
-default*
  double_param0  0.11
  double_param1  9.9
  int_param0     0
  int_param1     1
  str_param0     hoge
  str_param1     dara
  vector_param0  0.0,1.0,2.0,3.0,4.0

# Use the 'set' mode to change a configuration parameter. It normally takes
# three arguments (configuration set, parameter name, new value). If only
# two are given, the configuration set is assumed to be the currently active
# set.
$ rtconf ConfigSample0.rtc set default int_param0 5
$ rtconf ConfigSample0.rtc set int_param1 3
$ rtconf ConfigSample0.rtc list -l
-default*
  double_param0  0.11
  double_param1  9.9
  int_param0     5
  int_param1     3
  str_param0     hoge
  str_param1     dara
  vector_param0  0.0,1.0,2.0,3.0,4.0

# Use the 'act' mode to activate a configuration set. In the list display, the
# currently active set is marked with a '*'.
$ rtconf ConfigSample0.rtc act default

# No arguments to rtcwd moves to the root directory.
$ rtcwd
$ rtls localhost -l
Inactive  2/0  1/0  1/0  0/0  Clusterer0.rtc
Inactive  4/0  0/0  3/0  1/0  Hokuyo_AIST0.rtc
-         -    -    -    -    kenroke.host_cxt

# Sometimes, components break...
$ rtact localhost/Hokuyo_AIST0.rtc
$ rtls localhost -l
Inactive  2/0  1/0  1/0  0/0  Clusterer0.rtc
Error     4/0  0/0  3/0  1/0  Hokuyo_AIST0.rtc
-         -    -    -    -    kenroke.host_cxt

# Use rtreset to move a component from the error state to the inactive state.
$ rtreset localhost/Hokuyo_AIST0.rtc
$ rtls localhost -l
Inactive  2/0  1/0  1/0  0/0  Clusterer0.rtc
Inactive  4/0  0/0  3/0  1/0  Hokuyo_AIST0.rtc
-         -    -    -    -    kenroke.host_cxt

# rtmgr provides control over managers. Use it to load a shared library.
 $ rtcwd kenroke.host_cxt/
 $ rtmgr manager.mgr load ~/share/OpenRTM-aist/examples/rtcs/ConsoleIn.so
   ConsoleInInit
 $ rtcat manager.mgr
 Name: manager
 Instance name: manager
 Process ID: 25256
 Naming format: %h.host_cxt/%n.mgr
 Refstring path: /var/log/rtcmanager.ref
 Components precreate: 
 Modules:
   Load path: ./
   Config path: 
   Preload: 
   Init function prefix: 
   Init function suffix: 
   Download allowed: 
   Absolute path allowed: YES
 OS:
   Version: #1 SMP PREEMPT Mon Nov 30 11:10:37 JST 2009
   Architecture: x86_64
   Release: 2.6.31-gentoo-r6-gb
   Host name: kenroke
   Name: Linux
 Loaded modules:
   Filepath: /home/geoff/share/OpenRTM-aist/examples/rtcs/ConsoleIn.so
 Loadable modules:

Next, create instances of the component contained in that shared library.
 $ rtmgr manager.mgr create ConsoleIn
 $ rtmgr manager.mgr create ConsoleIn
 $ rtcwd manager.mgr
 $ rtls
 ConsoleIn0.rtc  ConsoleIn1.rtc

Component instances created by the manager can be removed by instance name.
 $ rtcwd ..
 $ rtmgr manager.mgr delete ConsoleIn0
 $ rtls manager.mgr/
 ConsoleIn1.rtc 

Loaded shared libraries can be removed from the manager.
 $ rtcwd ..
 $ rtmgr manager.mgr unload ~/share/OpenRTM-aist/examples/rtcs/ConsoleIn.so
 $ rtcat manager.mgr
 Name: manager
 Instance name: manager
 Process ID: 25256
 Naming format: %h.host_cxt/%n.mgr
 Refstring path: /var/log/rtcmanager.ref
 Components precreate: 
 Modules:
   Load path: ./
   Config path: 
   Preload: 
   Init function prefix: 
   Init function suffix: 
   Download allowed: 
   Absolute path allowed: YES
 OS:
   Version: #1 SMP PREEMPT Mon Nov 30 11:10:37 JST 2009
   Architecture: x86_64
   Release: 2.6.31-gentoo-r6-gb
   Host name: kenroke
   Name: Linux
 Loaded modules:
 Loadable modules:

# Use rtinject to inject a single value into an input port of a component.
# Let's try using it on ConsoleOut.
 $ rtinject ConsoleOut0.rtc:in 'RTC.TimedLong({time}, 42)'
# Looking at the output of the running ConsoleOut instance (with some lines
# removed for clarity):
 $ ./ConsoleOutComp
 =================================================
  Component Profile
 [...]
 Port0 (name): ConsoleOut0.in
 [...]
 Received: 42
 TimeStamp: 1266053430[s] 578351020[ns]

# The opposite of injecting data is printing it. Use rtprint to show what data
# is being send over an output port of a component.
 $ rtprint ConsoleIn0.rtc:out
 [0.025029968] 42

# If you have a zombie on one of your name servers, you will get constant
# warnings about it. You can delete zombies or any other registered object
# using rtdel.
 $ rtls
 ConsoleOut0.rtc
 $ rtdel ConsoleOut0.rtc
 $ rtls
 $


Repository
----------

The latest source is stored in a Git repository at github, available at
http://github.com/gbiggs/rtshell. You can download it as a zip file or tarball
by clicking the "Download Source" link in the top right of the page.
Alternatively, use Git to clone the repository. This is better if you wish to
contribute patches.

 $ git clone git://github.com/gbiggs/rtshell.git


Running the tests
-----------------

The command tests can be run from the source directory using a command like the
following:

 ~/src/rtshell $ ./test/test_cmds.py ~/share/OpenRTM-aist/examples/rtcs/

The argument to the test_cmds.py command is a directory containing RTC shared
libraries that can be loaded into a manager. It must contain the libraries for
Motor, Controller and Sensor.

An individual command's tests can be run by specifying those tests after the
command. For example:

 $ ./test/test_cmds.py ~/share/OpenRTM-aist/examples/rtcs/ rtactTests

This will run only the tests for the rtact command.


Changelog
---------

3.0
- Merged rtcshell and rtsshell into a single toolkit.
- Added complete documentation for every command (man pages, HTML, PDF).
- New command: rtdoc (Print component documentation - thanks to Yosuke
  Matsusaka).
- New command: rtexit (Make a component exit).
- New command: rtlog (Log and replay data streams).
- New command: rtcheck (Check a system matches an RtsProfile file).
- New command: rtcomp (Create composite components).
- New command: rtstodot (Visualise RT Systems - thanks to Yosuke Matsusaka).
- New command: rtvis
- rtconf bash completion now completes set names, parameter names and values.
- Merged rtcwd and bash_completion bash files into a single file.
- Overhauled rtconf command line, added option to get a parameter value
  directly.
- Handle zombies properly.
- Display zombies in rtls.
- Delete zombies in rtdel (including all zombies found).
- Support path filters in rtctree to speed up tree creation.
- rtcat: Option to print a single port's information.
- rtcat: Changes --ll to -ll.
- rtcat: Display information about composite components.
- rtcryo: Print RtsProfile to standard output by default.
- rtdis: Disconnect-by-ID allows removing only one connection.
- rtinject/rtprint: Added support for user data types.
- rtprint: Option to exit after receiving one round of data.
- rtprint: Added support for user-defined formatters.
- rtprint: Added ability to print raw Python code.
- rtinject: Accept raw Python input from stdin.
- rtresurrect: Don't recreate existing connections.
- rtteardown: Fail if the connector ID doesn't match.
- rtresurrect/rtstart/rtstop/rtteardown: Accept input from standard input.
- Refactored former rtsshell commands into rtshell-style libraries.
- Added tests.

rtcshell-2.0
- Fixes for Windows
- Fixed problems handling paths referencing parent directories
- New command: rtdel
- New command: rtinject
- New command: rtprint
- rtcat: Print the number of unknown connections
- Major refactoring: all commands can now be imported and called from Python
  scripts easily
- New Bash completion script (thanks to Keisuke Suzuki)
- Support csh in rtcwd
- rtcat: Print new information available from rtctree for execution contexts
- rtls: Change recurse option from -r to -R to match ls
- rtls: Handle unknown objects; display them like dead files

rtsshell-2.0
- Added bash-completion script.
- Added planning capability.

