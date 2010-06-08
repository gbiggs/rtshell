#!/usr/bin/env python
# -*- Python -*-
# -*- coding: utf-8 -*-

'''rtshell

Copyright (C) 2009-2010
    Geoffrey Biggs
    RT-Synthesis Research Group
    Intelligent Systems Research Institute,
    National Institute of Advanced Industrial Science and Technology (AIST),
    Japan
    All rights reserved.
Licensed under the Eclipse Public License -v 1.0 (EPL)
http://www.opensource.org/licenses/eclipse-1.0.txt

File: setup.py

rtshell install script.

'''

# $Source$


from distutils.command.install_scripts import install_scripts
from distutils.core import setup
import os.path
import sys

base_scripts = ['rtact',
                'rtcat',
                'rtcon',
                'rtconf',
                'rtcwd.py',
                'rtcryo',
                'rtdeact',
                'rtdel',
                'rtdis',
                'rtfind',
                'rtinject',
                'rtls',
                'rtmgr',
                'rtprint',
                'rtpwd',
                'rtreset',
                'rtresurrect',
                'rtstart',
                'rtstop',
                'rtteardown']
if sys.platform == 'win32':
    batch_files = ['rtact.bat',
                   'rtcat.bat',
                   'rtcon.bat',
                   'rtconf.bat',
                   'rtcryo.bat',
                   'rtcwd.bat',
                   'rtdeact.bat',
                   'rtdel.bat',
                   'rtdis.bat',
                   'rtfind.bat',
                   'rtinject.bat',
                   'rtls.bat',
                   'rtmgr.bat',
                   'rtprint.bat',
                   'rtpwd.bat',
                   'rtreset.bat',
                   'rtresurrect.bat',
                   'rtstart.bat',
                   'rtstop.bat',
                   'rtteardown.bat']
    scripts = base_scripts + batch_files
    data_files = []
else:
    scripts = base_scripts + ['rtcwd']
    data_files = [('share/rtshell', ['bash_completion'])]


class InstallRename(install_scripts):
    def run(self):
        install_scripts.run(self)
        if sys.platform == 'win32':
            # Rename the installed scripts to add .py on the end for Windows
            print 'Renaming scripts'
            for s in base_scripts:
                self.move_file(os.path.join(self.install_dir, s),
                               os.path.join(self.install_dir, s + '.py'))


setup(name='rtshell',
      version='3.0.0',
      description='Shell commands for managing RT Components and RT Systems.',
      author='Geoffrey Biggs',
      author_email='git@killbots.net',
      url='http://github.com/gbiggs/rtshell',
      license='EPL',
      long_description='Shell commands for managing RT-Middleware.',
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: EPL License',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Topic :: Software Development',
          'Topic :: Utilities'
          ],
      packages=['rtshell'],
      scripts=scripts,
      data_files=data_files,
      cmdclass={'install_scripts':InstallRename}
      )


# vim: tw=79

