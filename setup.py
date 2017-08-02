#!/usr/bin/env python2
# -*- Python -*-
# -*- coding: utf-8 -*-

from __future__ import print_function

'''rtshell

Copyright (C) 2009-2015
    Geoffrey Biggs
    RT-Synthesis Research Group
    Intelligent Systems Research Institute,
    National Institute of Advanced Industrial Science and Technology (AIST),
    Japan
    All rights reserved.
Licensed under the GNU Lesser General Public License version 3.
http://www.gnu.org/licenses/lgpl-3.0.en.html

File: setup.py

rtshell install script.

'''

# $Source$

from __future__ import print_function

from distutils.command.build import build
from distutils.command.install import install
from distutils.core import Command
from distutils import errors
from distutils import log
import os
import os.path
import setuptools
import shutil
import subprocess
import sys


scripts_build_dir = os.path.join('data')
scripts_install_dir = os.path.join('rtshell', 'data')
doc_build_dir = os.path.join('doc')
doc_install_dir = os.path.join('rtshell', 'data', 'doc')


class BuildDocumentation(Command):
    description = 'build the manpage, HTML and PDF documentation'
    user_options = [
            ('no-man', 'm', 'do not generate man pages'),
            ('no-html', 'h', 'do not generate HTML documentation'),
            ('pdf', 'p', 'do generate PDF documentation (disabled on Windows)'),
            ('no-english', 'e', 'do not generate English documentation'),
            ('no-japanese', 'j', 'do not generate Japanese documentation'),
            ('build-dir=', 'd', 'directory to build in'),
            ]
    boolean_options = ['no-man', 'no-html', 'pdf', 'no-english',
            'no-japanese']

    def initialize_options(self):
        self.no_man = False
        self.no_html = False
        self.pdf = False
        self.no_english = False
        self.no_japanese = False
        self.build_dir = None

    def finalize_options(self):
        if 'win' in sys.platform:
            self.pdf = False
        self.set_undefined_options('build', ('build_base', 'build_dir'))

    def source_dir(self, lang):
        return os.path.join(os.getcwd(), 'doc', 'rest', lang)

    def dest_dir(self, t, lang):
        return os.path.join(self.build_dir, 'doc', t, lang)

    def check_timestamps_in_dir(self, lang, lhs, rhs, verb=False):
        log.info('Checking documentation timestamps for directory {}'.format(rhs))
        for f in os.listdir(lhs):
            lhs_f = os.path.join(lhs, f)
            if not os.path.isfile(lhs_f):
                continue
            rhs_f = os.path.join(rhs, f)
            if not os.path.isfile(rhs_f):
                log.warn('Documentation file {} missing for language '
                    '{1}.'.format(f, lang))
                continue
            lhs_time = os.path.getmtime(lhs_f)
            rhs_time = os.path.getmtime(rhs_f)
            if lhs_time > rhs_time:
                log.warn('Documentation file {} for language {} is out of '
                    'date.'.format(f, lang))


    def check_timestamps(self, lang):
        # Base documentation files
        base_dir = os.path.join(os.getcwd(), 'doc', 'rest', 'en')
        check_dir = os.path.join(os.getcwd(), 'doc', 'rest', lang)
        self.check_timestamps_in_dir(lang, base_dir, check_dir)
        # Shared content
        base_dir = os.path.join(os.getcwd(), 'doc', 'common', 'en')
        check_dir = os.path.join(os.getcwd(), 'doc', 'common', lang)
        self.check_timestamps_in_dir(lang, base_dir, check_dir)


    def compile_docs(self, s, d, comp_cmd, ext):
        if os.path.exists(d):
            # Remove the destination to clear out any existing junk
            shutil.rmtree(d)
        self.mkpath(d)
        for f in os.listdir(s):
            src = os.path.join(s, f)
            if not os.path.isfile(src):
                log.warn('Skipping non-file {}'.format(src))
                continue
            dest = os.path.join(d, os.path.splitext(f)[0] + ext)
            log.debug('Compiling {} to {}'.format(src, dest))
            cmd = [comp_cmd, src, dest]
            try:
                if sys.platform == 'win32':
                    cmd.insert(0, 'python')
                p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE)
                stdout, stderr = p.communicate()
                if p.returncode != 0:
                    raise errors.DistutilsFileError(
                        'Failed to compile {} to {}.\nStdout:\n{}\n---\n'
                        'Stderr:\n{}'.format(src, dest, stdout, stderr))
            except OSError as e:
                if e.errno == 2:
                    # The non-.py version of the command was not found; try it
                    # with the .py extension (for platforms like Gentoo)
                    cmd[0] = cmd[0] + '.py'
                    if sys.platform == 'win32':
                        cmd.insert(0, 'python')
                    p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE)
                    stdout, stderr = p.communicate()
                    if p.returncode != 0:
                        raise errors.DistutilsFileError(
                            'Failed to compile {} to {}.\nStdout:\n{}\n---\n'
                            'Stderr:\n{}'.format(src, dest, stdout, stderr))
                else:
                    raise

    def compile_tex(self, s, d):
        if os.path.exists(d):
            # Remove the destination to clear out any existing junk
            shutil.rmtree(d)
        self.mkpath(d)
        tex_files = [os.path.join(s, f) for f in os.listdir(s) \
                if os.path.splitext(f)[1] == '.tex']
        for src in tex_files:
            dest = os.path.join(d, os.path.splitext(os.path.basename(src))[0] + '.pdf')
            log.debug('Compiling {} to {}'.format(src, dest))
            p = subprocess.Popen(['rubber', '-d', '--into', d, src],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = p.communicate()
            if p.returncode != 0:
                raise errors.DistutilsFileError(
                    'Failed to compile {} to {}.\nStdout:\n{}\n---\n'
                    'Stderr:\n{}'.format(src, dest, stdout, stderr))
        # Clear up the auxiliary files
        log.debug('Cleaning temporary files from {}'.format(d))
        for f in [f for f in os.listdir(d) if os.path.splitext(f)[1] \
                in ['.aux', '.log', '.out']]:
            os.remove(os.path.join(d, f))

    def clean_tex(self):
        for l in ['en', 'ja']:
            tex_dir=self.dest_dir('latex', l)
            if os.path.exists(tex_dir):
                log.debug('Removing latex directory {}'.format(tex_dir))
                shutil.rmtree(tex_dir)

    def compile_man(self, lang):
        log.info('Compiling manpage documentation for language {}'.format(lang))
        cmd = 'rst2man'
        if sys.platform == 'win32':
            cmd = os.path.join(sys.prefix, 'Scripts', cmd + '.py')
        self.compile_docs(self.source_dir(lang),
                os.path.join(self.dest_dir('man', lang), 'man1'), cmd, '.1')

    def compile_html(self, lang):
        log.info('Compiling HTML documentation for language {}'.format(lang))
        cmd = 'rst2html'
        if sys.platform == 'win32':
            cmd = os.path.join(sys.prefix, 'Scripts', cmd + '.py')
        self.compile_docs(self.source_dir(lang),
                self.dest_dir('html', lang), cmd, '.html')

    def compile_pdf(self, lang):
        log.info('Compiling PDF documentation for language {}'.format(lang))
        cmd = 'rst2latex'
        if sys.platform == 'win32':
            cmd = os.path.join(sys.prefix, 'Scripts', cmd + '.py')
        tex_dir = self.dest_dir('latex', lang)
        self.compile_docs(self.source_dir(lang), tex_dir, cmd, '.tex')
        self.compile_tex(tex_dir, self.dest_dir('pdf', lang))
        self.clean_tex()

    def run(self):
        msg = 'Compiling documentation in formats '
        if not self.no_man:
            msg += 'man, '
        if not self.no_html:
            msg += 'html, '
        if self.pdf:
            msg += 'pdf'
        if msg[-2] == ',':
            msg = msg[:-2]
        msg += ' for languages '
        if not self.no_english:
            msg += 'English, '
        if not self.no_japanese:
            msg += 'Japanese, '
        if msg[-2] == ',':
            msg = msg[:-2]
        log.info(msg)

        langs = []
        if not self.no_english:
            langs.append('en')
        if not self.no_japanese:
            langs.append('ja')
            self.check_timestamps('ja')
        for l in langs:
            if not self.no_man:
                self.compile_man(l)
            if not self.no_html:
                self.compile_html(l)
            if self.pdf:
                self.compile_pdf(l)

        log.info('Documentation compilation complete')


class InstallDocumentation(Command):
    description = 'install documentation'
    user_options = [
        ('install-dir=', 'd', 'directory to install documentation to'),
        ('build-dir=', 'b', 'build directory (where to install from)'),
        ('force', 'f', 'force installation (overwrite existing files)'),
        ('skip-build', None, 'skip the build steps'),
        ]
    boolean_options = ['force', 'skip-build']

    def initialize_options(self):
        self.install_dir = None
        self.build_dir = None
        self.force = None
        self.skip_build = None

    def finalize_options(self):
        self.set_undefined_options('build', ('build_base', 'build_dir'))
        self.set_undefined_options('install', ('force', 'force'),
                ('skip_build', 'skip_build'))
        # Documentation gets installed into the module's data directory.
        # This is <install_lib>/rtshell/data
        # This is necessary to ensure consistent and correct placement of the
        # data files on Windows and Unix. Installing the docs as data causes
        # the wheel to put them in the right place (under the install prefix,
        # e.g. /usr/share/doc) on Unix but on Windows they end up in the Python
        # installation's root directory, which is dirty.
        self.set_undefined_options('install', ('install_lib', 'install_dir'))

    def run(self):
        if not self.skip_build:
            self.run_command('build_documentation')
        self.outfiles = self.copy_tree(
                os.path.join(self.build_dir, doc_build_dir),
                os.path.join(self.install_dir, doc_install_dir))

    def get_outputs(self):
        return self.outfiles or []


class BuildShellSupport(Command):
    description = '"build" the shell support scripts'
    user_options = [
            ('build-dir=', 'd', 'directory to build in'),
            ]

    def initialize_options(self):
        self.build_dir = None

    def finalize_options(self):
        self.set_undefined_options('build', ('build_base', 'build_dir'))

    def config_bash_compl(self):
        COMPOPT_NOSPACE = 'compopt -o nospace'
        COMPOPT_FILENAME = 'compopt -o filenames'
        COMPLETE_NOSPACE = '-o nospace'
        with open(os.path.join('data', 'bash_completion.in'), 'rt') as f:
            bash_comp = f.read()
        if sys.platform == 'darwin':
            bash_comp = bash_comp.replace('@COMPOPT_NOSPACE@', ':')
            bash_comp = bash_comp.replace('@COMPOPT_FILENAMES@', ':')
            bash_comp = bash_comp.replace('@COMPLETE_NOSPACE@',
                    COMPLETE_NOSPACE)
        else:
            bash_comp = bash_comp.replace('@COMPOPT_NOSPACE@', COMPOPT_NOSPACE)
            bash_comp = bash_comp.replace('@COMPOPT_FILENAMES@',
                    COMPOPT_FILENAME)
            bash_comp = bash_comp.replace('@COMPLETE_NOSPACE@', '')
        bash_completion_dir = os.path.join(self.build_dir, scripts_build_dir)
        bash_completion_path = os.path.join(bash_completion_dir,
                'bash_completion')
        if not os.path.isdir(bash_completion_dir):
            self.mkpath(bash_completion_dir)
        with open(bash_completion_path, 'w') as f:
            f.write(bash_comp)

    def copy_shell_support(self):
        shutil.copy(os.path.join('data', 'shell_support'),
                os.path.join(self.build_dir, scripts_build_dir))

    def copy_batch_files(self):
        shutil.copy(os.path.join('data', 'rtcwd.bat'),
                os.path.join(self.build_dir, scripts_build_dir))

    def run(self):
        # Configure the shell support scripts
        self.config_bash_compl()
        self.copy_shell_support()
        self.copy_batch_files()


class InstallShellSupport(Command):
    description = 'install the shell support scripts'
    user_options = [
        ('install-dir=', 'd', 'directory to install shell support scripts to'),
        ('build-dir=', 'b', 'build directory (where to install from)'),
        ('force', 'f', 'force installation (overwrite existing files)'),
        ('skip-build', None, 'skip the build steps'),
        ]
    boolean_options = ['force', 'skip-build']

    def initialize_options(self):
        self.install_dir = None
        self.build_dir = None
        self.force = None
        self.skip_build = None

    def finalize_options(self):
        self.set_undefined_options('build', ('build_base', 'build_dir'))
        self.set_undefined_options('install', ('force', 'force'),
                ('skip_build', 'skip_build'))
        # Shell scripts get installed into the module's data directory.
        # This is <install_lib>/rtshell/data
        # This is necessary to ensure consistent and correct placement of the
        # data files on Windows and Unix. Installing them as data causes the
        # wheel to put them in the right place (under the install prefix, e.g.
        # /usr/share/doc) on Unix but on Windows they end up in the Python
        # installation's root directory, which is dirty.
        self.set_undefined_options('install', ('install_lib', 'install_dir'))

    def run(self):
        if not self.skip_build:
            self.run_command('build_shell_support')
        self.outfiles = self.copy_tree(
                os.path.join(self.build_dir, scripts_build_dir),
                os.path.join(self.install_dir, scripts_install_dir))

    def get_outputs(self):
        return self.outfiles or []



class CustomInstall(install):
    def run(self):
        install.run(self)


build.sub_commands.append(('build_shell_support', None))
install.sub_commands.append(('install_shell_support', None))
build.sub_commands.append(('build_documentation', None))
install.sub_commands.append(('install_documentation', None))
# Setuptools/distutils has a bug where the install command does not consider
# entry points to be scripts. This means that if entry points are specified but
# no scripts are directly installed (using the scripts parameter to setup()),
# the entry points will not be installed.
# This does not apply when using pip with a wheel because pip will create the
# entry point scripts separately.
# To get around this bug, the below lines remove the has_scripts predicate used
# to determine if the install_scripts sub-command should be run, ensuring that
# it is always run.
install.sub_commands = [c for c in install.sub_commands \
        if c[0] != 'install_scripts']
install.sub_commands.insert(2, ('install_scripts', None))


setuptools.setup(name='rtshell',
    version='4.2.1',
    description='Shell commands for managing RT Components and RT Systems.',
    author='Geoffrey Biggs and contributors',
    author_email='geoffrey.biggs@aist.go.jp',
    url='http://github.com/gbiggs/rtshell',
    license='LGPL3',
    long_description='Shell commands for managing RT-Middleware.',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development',
        'Topic :: Utilities'
        ],
    packages=setuptools.find_packages(),
    install_requires=['rtctree>=4', 'rtsprofile>=4'],
    cmdclass={'build_shell_support': BuildShellSupport,
        'install_shell_support': InstallShellSupport,
        'build_documentation': BuildDocumentation,
        'install_documentation': InstallDocumentation,
        'install': CustomInstall,
        },
    entry_points = {
        'console_scripts': [
            'rtshell_post_install = rtshell.post_install:main',
            'rtact = rtshell.rtact:main',
            'rtcat = rtshell.rtcat:main',
            'rtcheck = rtshell.rtcheck:main',
            'rtcomp = rtshell.rtcomp:main',
            'rtcon = rtshell.rtcon:main',
            'rtconf = rtshell.rtconf:main',
            'rtcryo = rtshell.rtcryo:main',
            'rtdeact = rtshell.rtdeact:main',
            'rtdel = rtshell.rtdel:main',
            'rtdis = rtshell.rtdis:main',
            'rtdoc = rtshell.rtdoc:main',
            'rtexit = rtshell.rtexit:main',
            'rtfind = rtshell.rtfind:main',
            'rtinject = rtshell.rtinject:main',
            'rtlog = rtshell.rtlog:main',
            'rtls = rtshell.rtls:main',
            'rtmgr = rtshell.rtmgr:main',
            'rtprint = rtshell.rtprint:main',
            'rtpwd = rtshell.rtpwd:main',
            'rtreset = rtshell.rtreset:main',
            'rtresurrect = rtshell.rtresurrect:main',
            'rtstart = rtshell.rtstart:main',
            'rtstodot = rtshell.rtstodot:main',
            'rtstop = rtshell.rtstop:main',
            'rtteardown = rtshell.rtteardown:main',
            'rtvlog = rtshell.rtvlog:main',
            'rtwatch = rtshell.rtwatch:main',
            'rtfsm = rtshell.rtfsm:main',
            ],
        }
    )

#  vim: set expandtab tabstop=8 shiftwidth=4 softtabstop=4 textwidth=79
