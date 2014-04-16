#!/usr/bin/env python
# -*- Python -*-
# -*- coding: utf-8 -*-

'''rtshell

Copyright (C) 2009-2014
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
def get_files(dir, ext=None):
    files = [os.path.join(dir, f) for f in os.listdir(dir) \
            if os.path.isfile(os.path.join(dir, f))]
    if ext:
        return [f for f in files if os.path.splitext(f)[1] == ext]
    else:
        return files

if sys.platform != 'win32':
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
    pdf_files_en = get_files(os.path.join(os.getcwd(), 'doc/pdf'), ext='.pdf')
    man_files_ja = get_files(os.path.join(os.getcwd(), 'doc/man/ja/man1'))
    html_files_ja = get_files(os.path.join(os.getcwd(), 'doc/html/ja'))
    pdf_files_ja = get_files(os.path.join(os.getcwd(), 'doc/pdf/ja'), ext='.pdf')
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
                'rtteardown',
                'rtvlog']
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
                   'rtdoc.bat',
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
                   'rtteardown.bat',
                   'rtvlog.bat']
    scripts = base_scripts + batch_files
    data_files = [('Doc/rtshell', html_files_en + pdf_files_en),
            ('Doc/rtshell/ja', html_files_ja + pdf_files_ja)]
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
                dest = os.path.join(self.install_dir, s + '.py')
                if os.path.exists(dest):
                    os.remove(dest)
                self.move_file(os.path.join(self.install_dir, s), dest)
            # Make links for the docs
            #print 'Creating Start Menu links'
            #rtshell_dir = os.path.join(self._get_start_menu(), 'rtshell')
            #if not os.path.exists(rtshell_dir):
                #os.mkdir(rtshell_dir)
            #docs_en_path = os.path.join(rtshell_dir,
                    #'Documentation (English).url')
            #docs_ja_path = os.path.join(rtshell_dir,
                    #'Documentation (Japanese).lnk')

    def _get_start_menu(self):
        if sys.platform != 'win32':
            return ''
        import ctypes
        import ctypes.wintypes
        SHGetFolderPath = ctypes.windll.shell32.SHGetFolderPathW
        SHGetFolderPath.argtypes = [ctypes.wintypes.HWND, ctypes.c_int,
                ctypes.wintypes.HANDLE, ctypes.wintypes.DWORD,
                ctypes.wintypes.LPCWSTR]
        path = ctypes.wintypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
        SHGetFolderPath(0, 2, 0, 0, path)
        return path.value


class InstallConfigure(install_data):
    def run(self):
        install_data.run(self)
        if sys.platform != 'win32':
            cmd = 'echo $SHELL | grep -q bash && source {dir}/bash_completion\n'
            dest = os.path.join(self.install_dir, 'share/rtshell', 'shell_support')
            if os.path.isfile(dest):
                os.remove(dest)
            self.move_file(os.path.join(self.install_dir, 'share/rtshell',
                    'shell_support.in'), dest)
            with open(dest, 'a') as f:
                f.writelines((cmd.format(dir=os.path.join(self.install_dir,
                    'share/rtshell')), '\n'))
            self.config_bash_compl()

    def config_bash_compl(self):
        COMPOPT_NOSPACE = 'compopt -o nospace'
        COMPOPT_FILENAME = 'compopt -o filenames'
        COMPLETE_NOSPACE = '-o nospace'
        compl_script = '{0}/bash_completion'.format(
                os.path.join(self.install_dir, 'share/rtshell'))
        if sys.platform == 'darwin':
            replace = ['-e', 's/@COMPOPT_NOSPACE@/:/g', '-e',
                    's/@COMPOPT_FILENAME@/:/g', '-e',
                    's/@COMPLETE_NOSPACE@/{0}/g'.format(COMPLETE_NOSPACE)]
        else:
            replace = ['-e', "'s/@COMPOPT_NOSPACE@/{0}/g'".format(
                COMPOPT_NOSPACE), '-e', "'s/@COMPOPT_FILENAME@/{0}/g'".format(
                COMPOPT_FILENAME), '-e', "'s/@COMPLETE_NOSPACE@//g'"]
        p = subprocess.Popen(['sed'] + replace + ['-i', '', compl_script],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd)
        stdout, stderr = p.communicate()
        if p.returncode != 0:
            print 'Failed to filter bash_completion.'
            print stderr


setup(name='rtshell',
      version='4.0.0',
      description='Shell commands for managing RT Components and RT Systems.',
      author='Geoffrey Biggs and contributors',
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

