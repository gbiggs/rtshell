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
from distutils.command.install_data import install_data
from distutils.core import setup
import os
import os.path
import subprocess
import sys


# Hacky method of installing the documentation. Need a nice hook for this.
def get_files(dir):
    return [os.path.join(dir, f) for f in os.listdir(dir) \
            if os.path.isfile(os.path.join(dir, f))]

cwd = os.path.join(os.getcwd(), 'doc')
s = raw_input('Generate documentation? ')
if s.lower() == 'y' or s.lower() == 'YES':
    print 'Generating documentation'
    p = subprocess.Popen(['./make_docs', 'man', 'html', 'pdf', '-v'],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd)
    stdout, stderr = p.communicate()
    if p.returncode != 0:
        print 'Failed to generate documentation. Check docutils are installed.'
        print stderr
try:
    man_files_en = get_files(os.path.join(os.getcwd(), 'doc/man/man1'))
    html_files_en = get_files(os.path.join(os.getcwd(), 'doc/html'))
    pdf_files_en = get_files(os.path.join(os.getcwd(), 'doc/pdf'))
    man_files_ja = get_files(os.path.join(os.getcwd(), 'doc/man/ja/man1'))
    html_files_ja = get_files(os.path.join(os.getcwd(), 'doc/html/ja'))
    pdf_files_ja = get_files(os.path.join(os.getcwd(), 'doc/pdf/ja'))
except OSError:
    man_files_en = []
    html_files_en = []
    pdf_files_en = []
    man_files_ja = []
    html_files_ja = []
    pdf_files_ja = []


base_scripts = ['rtact',
                'rtcat',
                'rtcheck',
                'rtcomp',
                'rtcon',
                'rtconf',
                'rtcryo',
                'rtdeact',
                'rtdel',
                'rtdis',
                'rtexit',
                'rtfind',
                'rtinject',
                'rtlog',
                'rtls',
		'rtdoc',
                'rtmgr',
                'rtprint',
                'rtpwd',
                'rtreset',
                'rtresurrect',
                'rtstart',
                'rtstodot',
                'rtstop',
                'rtteardown']
if sys.platform == 'win32':
    batch_files = ['rtact.bat',
                   'rtcat.bat',
                   'rtcheck.bat',
                   'rtcomp.bat',
                   'rtcon.bat',
                   'rtconf.bat',
                   'rtcryo.bat',
                   'rtcwd.bat',
                   'rtdeact.bat',
                   'rtdel.bat',
                   'rtdis.bat',
                   'rtexit.bat',
                   'rtfind.bat',
                   'rtinject.bat',
                   'rtlog.bat',
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
    scripts = base_scripts
    data_files = [('share/rtshell', ['bash_completion', 'shell_support.in']),
            ('share/man/man1', man_files_en),
            ('share/man/ja/man1', man_files_ja),
            ('share/doc/rtshell', html_files_en + pdf_files_en),
            ('share/doc/rtshell/ja', html_files_ja + pdf_files_ja)]


class InstallRename(install_scripts):
    def run(self):
        install_scripts.run(self)
        if sys.platform == 'win32':
            # Rename the installed scripts to add .py on the end for Windows
            print 'Renaming scripts'
            for s in base_scripts:
                self.move_file(os.path.join(self.install_dir, s),
                               os.path.join(self.install_dir, s + '.py'))


class InstallConfigure(install_data):
    def run(self):
        install_data.run(self)
        cmd = 'echo $SHELL | grep -q bash && source {dir}/bash_completion\n'
        dest = os.path.join(self.install_dir, 'share/rtshell', 'shell_support')
        if os.path.isfile(dest):
            os.remove(dest)
        self.move_file(os.path.join(self.install_dir, 'share/rtshell',
                'shell_support.in'), dest)
        with open(dest, 'a') as f:
            f.writelines((cmd.format(dir=os.path.join(self.install_dir,
                'share/rtshell')), '\n'))


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
      cmdclass={'install_scripts':InstallRename,
          'install_data':InstallConfigure}
      )


# vim: tw=79

