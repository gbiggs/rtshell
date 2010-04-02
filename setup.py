#!/usr/bin/env python
# -*- Python -*-
# -*- coding: utf-8 -*-

'''rtsshell

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

Install script.

'''

__version__ = '$Revision: $'
# $Source$


from distutils.command.install_scripts import install_scripts
from distutils.core import setup
import os.path
import sys

base_scripts = ['rtcryo',
                'rtresurrect',
                'rtstart',
                'rtstop',
                'rtteardown']
if sys.platform == 'win32':
    batch_files = ['rtcryo.bat',
                   'rtresurrect.bat',
                   'rtstart.bat',
                   'rtstop.bat',
                   'rtteardown']
    scripts =  base_scripts + batch_files
else:
    scripts = base_scripts
    data_files = [('share/rtsshell', ['bash_completion'])]


class InstallRename(install_scripts):
    def run(self):
        install_scripts.run(self)
        if sys.platform == 'win32':
            # Rename the installed scripts to add .py on the end for Windows
            print 'Renaming scripts'
            for s in base_scripts:
                self.move_file(os.path.join(self.install_dir, s),
                               os.path.join(self.install_dir, s + '.py'))


setup(name='rtsshell',
      version='2.0.0',
      description='Collection of tools for managing complete RT Systems.',
      long_description='Collection of tools for managing complete RT Systems.',
      author='Geoffrey Biggs',
      author_email='git@killbots.net',
      url='http://github.com/gbiggs/rtsshell',
      license='BSD',
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: EPL License',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Topic :: Software Development',
          ],
      packages=['rtsshell'],
      scripts=scripts,
      data_files=data_files,
      cmdclass={'install_scripts':InstallRename}
      )


# vim: tw=79

