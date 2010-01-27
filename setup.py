#!/usr/bin/env python
# -*- Python -*-
# -*- coding: utf-8 -*-

'''rtcshell

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

rtcshell install script.

'''

__version__ = '$Revision: $'
# $Source$


from distutils.core import setup
import sys

scripts = ['rtact',
           'rtcat',
           'rtcon',
           'rtconf',
           'rtcwd.py',
           'rtdeact',
           'rtdis',
           'rtfind',
           'rtls',
           'rtmgr',
           'rtpwd',
           'rtreset']
if sys.platform == 'win32':
    batch_files = ['rtact.bat',
                   'rtcat.bat',
                   'rtcon.bat',
                   'rtconf.bat',
                   'rtcwd.bat',
                   'rtdeact.bat',
                   'rtdis.bat',
                   'rtfind.bat',
                   'rtls.bat',
                   'rtmgr.bat',
                   'rtpwd.bat',
                   'rtreset.bat']
    scripts += batch_files
else:
    scripts.append('rtcwd')

setup(name='rtcshell',
      version='1.0.0',
      description='Shell commands for managing RT-Middleware.',
      author='Geoffrey Biggs',
      author_email='git@killbots.net',
      url='http://github.com/gbiggs/rtcshell',
      license='BSD',
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
      packages=['rtcshell'],
      scripts=scripts
      )


# vim: tw=79

