=======
RTShell
=======

Introduction
============

RTShell provides commands used to manage individual RT components and
managers, as well as complete RT Systems. It can be used with the
OpenRTM-aist middleware or middlewares that use a compatible CORBA-based
introspection system.

Many of the commands allow components and managers running on
nameservers to be treated like a file system. Directories can be
entered, components can be cat'd and activated/deactivated/reset,
connections made and removed, and so on.

Other commands are used in conjunction with RtsProfile XML/YAML files to
manage complete RT Systems. These are rtresurrect, rtteardown, rtcryo,
rtstart and rtstop.

The commands are aimed at users of OpenRTM-aist who wish to manage
components on low-resource systems, systems where a GUI is not available
(particularly where no network connection is available to manage
components from another computer), as well as those who face other
difficulties using RTSystemEditor.  Being familiar with using a
command-line is a benefit when using these commands of RTShell.

This software is developed at the National Institute of Advanced
Industrial Science and Technology. Approval number
H23PRO-1214. The development was financially supported by
the New Energy and Industrial Technology Development Organisation
Project for Strategic Development of Advanced Robotics Elemental
Technologies.

This software is licensed under the GNU Lesser General Public License version 3
(LGPL3). See LICENSE.txt.

Requirements
============

omniORB-py 4.x is required.

RTShell requires rtctree. It must be installed for the commands to function.

The commands that work with RtsProfile files require rtsprofile. It must be
installed for these commands to function/

RTShell requires Python 2.7. It will not function with an earlier version of
Python. It has not been tested with Python 3 and it is likely that several
changes will be necessary to make it function using this version of Python.

rtprint, rtinject and rtlog require the Python version of OpenRTM-aist.

Sphinx must be installed to build the documentation, if installing from source
(method 2).

If RTShell is installed using pip (method 1, below), RTCTree and RTSProfile
will be installed automatically. omniORB-py and OpenRTM-python must still be
installed manually.


Installation
============

There are several methods of installation available:

1. (Preferred method) Use pip to install the PyPi package.

 a. Install pip if it is not already installed.
    See https://pip.pypa.io/en/latest/installing/

 b. Execute the following command to install RTShell::

    $ pip install rtshell

 c. Execute the post-installation setup::

    $ rtshell_post_install

 d. On Windows, you will need to ensure that your Python scripts directory is
    in the PATH variable.  Typically, this will be something like
    ``C:\Python27\Scripts\`` (assuming Python 2.7 installed in
    ``C:\Python27\``).

2. Download the source from either the repository (see "Repository," below) or
   a source archive, extract it somewhere, and install it into your Python
   distribution:

 a. Extract the source, e.g. to a directory ~/rtshell::

    $ cd /home/blurgle/src/
    $ tar -xvzf rtshell.tar.gz

 b. Run setup.py to install RTShell to your default Python installation::

    $ python setup.py install

 c. Execute the post-installation setup::

    $ rtshell_post_install

 d. On Windows, you will need to ensure that your Python scripts directory is
    in the PATH variable.  Typically, this will be something like
    ``C:\Python27\Scripts\`` (assuming Python 2.7 installed in
    ``C:\Python27\``).

3. On Windows, use the Windows installer.


Repository
==========

The latest source is stored in a Git repository at github, available at
``http://github.com/gbiggs/rtshell``. You can download it as a zip file or
tarball by clicking the "Download Source" link on that page. Alternatively, use
Git to clone the repository. This is better if you wish to contribute patches::

  $ git clone git://github.com/gbiggs/rtshell.git


Documentation
=============

Documentation is available in the form of man pages (on Windows, these
are available as HTML files). These will be installed under
``${prefix}/share/man``.  You must add this folder to your system's
``$MANPATH`` environment variable to be able to use them. For example,
if you installed RTShell into /home/blag, add the following line to your
``.bashrc``::

  export MANPATH=/home/blag/share/man:${MANPATH}


Running the tests
=================

The command tests can be run from the source directory using a command
like the following::

  ~/src/rtshell $ ./test/test_cmds.py ~/share/OpenRTM-aist/examples/rtcs/

The argument to the test_cmds.py command is a directory containing RTC
shared libraries that can be loaded into a manager. It must contain the
libraries for Motor, Controller and Sensor.

An individual command's tests can be run by specifying those tests after
the command. For example::

  $ ./test/test_cmds.py ~/share/OpenRTM-aist/examples/rtcs/ rtactTests

This will run only the tests for the rtact command.


Creating wheels
===============

To create a redistributable wheel package, run the following command:

  $ python setup.py bdist_wheel -k


Changelog
=========

4.2
---

- Add "-d" option to rtcon to check for duplicate connections
- Add support for FSM4RTC, with rtwatch and rtfsm commands (@yosuke)
- Add doctests (@yosuke)
- Fix direction of rtstodot graphs (@haudren)

4.1
---

- Switched setup script from distutils to setuptools
- Dropped support for Python 2.6

4.0
---

- Fixed saving and restoring connection properties.
- Fixed disabling output of colour codes on Windows
- Adapt to OpenRTM's new data type specification method.
- Changed all os.sep occurrences to '/' for consistency with URLs.
- New command: rtvlog (Display RT Component log events).
- rtact/rtdeact/rtreset: Allow changing multiple components at once.
- rtcomp: Support managing compositions of remote components.
- rtcon: Support making connections involving three or more ports.
- rtdis: Support removing connections involving three or more ports.
- rtlog: Added end pointer to simpkl log format to speed up searches.
- rtmgr: Support corbaloc:: direct connection to managers.
- rtmgr: Allow multiple occurrences of any commands.
- rtmgr: Execute commands in the order specified.

3.0.1
-----

- Fixed #13: Error with unknown ports when saving systems using rtcryo.
- Fixed #14/#15: Properly handle data types that include versions and IDL
  paths in rtprint.
- Fixed #16: Handle component instance names that include parantheses.

3.0
---

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
- Refactored former rtsshell commands into RTShell-style libraries.
- Added tests.


rtcshell-2.0
------------

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
------------

- Added bash-completion script.
- Added planning capability.

