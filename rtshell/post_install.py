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

Post-install actions for running after wheel-based installs

'''


import argparse
import logging
import os
import os.path
import pkg_resources
import pkgutil
import platform
import shutil
import sys


def create_and_link_dir(source, dest, dir_type='', remove=False):
    # Confirm the source is correct
    if not os.path.exists(source) or not os.path.isdir(source):
        sys.exit('Source {} directory does not exist or is not a directory: '
            '{}'.format(dir_type, source))
    if os.path.exists(dest):
        if remove:
            if os.path.islink(dest):
                os.remove(dest)
            else:
                shutil.rmtree(dest)
        else:
            logging.info('Destination {} directory already exists; skipping: '
                '{}'.format(dir_type, dest))
            return
    # Make the destination parent directory if necessary
    parent_dir = os.path.dirname(dest)
    if not os.path.exists(parent_dir):
        logging.info('Making {} parent directory: {}'.format(dir_type,
            parent_dir))
        os.makedirs(parent_dir)
    elif not os.path.isdir(parent_dir):
        sys.exit('Destination {} parent directory exists but is not a '
            'directory: {}'.format(dir_type, parent))
    # Create the link
    logging.info('Creating symbolic link from {} to {}'.format(source, dest))
    os.symlink(source, dest)


def create_and_link_dir_content(source, dest, dir_type='', remove=False):
    logging.info('Creating symbolic links from {} to {}'.format(source, dest))
    # Confirm the source is correct
    if not os.path.exists(source) or not os.path.isdir(source):
        sys.exit('Source {} directory does not exist or is not a directory: '
            '{}'.format(dir_type, source))
    # Make the destination path if necessary
    if os.path.exists(dest):
        if remove:
            if os.path.islink(dest):
                os.remove(dest)
            else:
                shutil.rmtree(dest)
        else:
            logging.info('Destination {} directory already exists; skipping: '
                '{}'.format(dir_type, dest))
    os.makedirs(dest)
    # Link all files in source
    for f in [f for f in os.listdir(source) if
            os.path.isfile(os.path.join(source, f))]:
        s = os.path.join(source, f)
        d = os.path.join(dest, f)
        logging.info('Creating symbolic link from {} to {}'.format(s, d))
        try:
            os.symlink(s, d)
        except OSError as e:
            if e.errno == 17:
                logging.info('Skipping existing symbolic link {}'.format(d))
            else:
                raise


def doc_source_dir(t, l, postfix=''):
    r = pkg_resources.resource_filename('rtshell.data',
            os.path.join('doc', t, l))
    if postfix:
        # Done separately to prevent a trailing slash for empty postfixes,
        # which messes with os.path.basename, etc.
        r = os.path.join(r, postfix)
    return r


# Symlink the man pages from share/doc/rtshell/man/man1/* into # <prefix>/share/man/man1
# If there is a Japanese manpage dir, symlink share/doc/rtshell/man/ja/man1 to there
def link_man_pages(prefix, remove=False):
    man_source_en = doc_source_dir('man', 'en', 'man1')
    man_source_ja = doc_source_dir('man', 'ja', 'man1')
    man_path_en = os.path.join(prefix, 'share', 'man', 'man1')
    man_path_ja = os.path.join(prefix, 'share', 'man', 'ja', 'man1')
    if os.path.exists(man_source_en):
        create_and_link_dir_content(man_source_en, man_path_en,
                'default manpage', remove)
    if os.path.exists(man_source_ja):
        create_and_link_dir_content(man_source_ja, man_path_ja,
                'Japanese manpage', remove)
    man_path = os.path.join(prefix, 'share', 'man')
    print('Linked manpage documentation to', man_path)
    print('***** IMPORTANT *****')
    print('You may need to add the following line or similar to your shell '
            'setup scripts ' '(e.g. $HOME/.bashrc) to enable the manpage '
            'documentation:')
    print('\texport MANPATH={}:$MANPATH'.format(man_path))
    print('*********************')


# Symlink the html/pdf documentation to prefix/share/doc/rtshell
def link_documentation(prefix, remove=False):
    doc_dir = os.path.join(prefix, 'share', 'doc', 'rtshell')
    html_source_en = doc_source_dir('html', 'en')
    html_source_ja = doc_source_dir('html', 'ja')
    if os.path.exists(html_source_en):
        create_and_link_dir(html_source_en, os.path.join(doc_dir, 'html',
            'en'), 'English HTML documentation', remove)
    if os.path.exists(html_source_ja):
        create_and_link_dir(html_source_ja, os.path.join(doc_dir, 'html',
            'ja'), 'Japanese HTML documentation', remove)
    pdf_source_en = doc_source_dir('pdf', 'en')
    pdf_source_ja = doc_source_dir('pdf', 'ja')
    if os.path.exists(pdf_source_en):
        create_and_link_dir(pdf_source_en, os.path.join(doc_dir, 'pdf', 'en'),
                'English PDF documentation', remove)
    if os.path.exists(pdf_source_ja):
        create_and_link_dir(pdf_source_ja, os.path.join(doc_dir, 'pdf', 'ja'),
                'Japanese PDF documentation', remove)
    print('Linked documentation to', doc_dir)


def add_shell_support(prefix, bashrc_path=None):
    script_path = pkg_resources.resource_filename('rtshell.data',
            'shell_support')
    source_line = 'source {}'.format(os.path.abspath(script_path))
    if not bashrc_path:
        bashrc_path = os.path.expanduser('~/.bashrc')
    else:
        bashrc_path = os.path.expanduser(bashrc_path)
    if os.path.exists(bashrc_path) and os.path.isfile(bashrc_path):
        # Check if the source line already exists
        with open(bashrc_path, 'r') as f:
            content = f.read()
            if source_line in content:
                print('Shell support already installed in', bashrc_path)
                return
    with open(bashrc_path, 'a') as bashrc_f:
        bashrc_f.write('\n' + source_line)
    print('Added "{}" to {}'.format(source_line, bashrc_path))

def post_install_unix(prefix, bashrc, interactive, remove=False):
    # Link the manpages to the manpage directory under the prefix
    ans = raw_input('Link man pages? ') if interactive else 'y'
    if ans.lower() == 'y' or ans.lower() == 'yes':
        link_man_pages(prefix, remove)
    # Link documentation to <prefix>/share/doc/rtshell
    ans = raw_input('Link documentation? ') if interactive else 'y'
    if ans.lower() == 'y' or ans.lower() == 'yes':
        link_documentation(prefix, remove)
    # Add sourcing of share/rtshell/shell_support to .bashrc or .bash_profile
    ans = raw_input('Add shell support to .bashrc? ') if interactive else 'y'
    if ans.lower() == 'y' or ans.lower() == 'yes':
        add_shell_support(prefix, bashrc_path=bashrc)


def copy_batch_files(prefix, remove=False):
    # Copy the rtcwd batch file to the Python scripts directory
    bf_src = pkg_resources.resource_filename('rtshell.data', 'rtcwd.bat')
    if not os.path.exists(bf_src) or not os.path.isfile(bf_src):
        sys.exit('Source batch file does not exist or is not a file:'.format(
            bf_src))
    bf_dest = os.path.join(prefix, 'Scripts', 'rtcwd.bat')
    if os.path.exists(bf_dest):
        if remove:
            os.remove(bf_dest)
        else:
            logging.info('Destination file already exists; skipping: '
                '{}'.format(bf_dest))
            return
    shutil.copy(bf_src, bf_dest)
    print('Copied {} to {}'.format(bf_src, bf_dest))


def post_install_windows(prefix, interactive, remove=False):
    ans = raw_input('Copy batch files? ') if interactive else 'y'
    if ans.lower() == 'y' or ans.lower() == 'yes':
        copy_batch_files(prefix, remove)


def main():
    p = argparse.ArgumentParser(description='Post-install actions for RTShell')
    if platform.system() != 'Windows':
        p.add_argument('-b', '--bashrc-path', type=str, default='~/.bashrc',
                help='Path to an alternative file to install shell support in')
        p.add_argument('-p', '--prefix', type=str, default='/usr/local',
                help='Prefix to install to [Default: %(default)s]')
    else:
        p.add_argument('-p', '--prefix', type=str, default=sys.exec_prefix,
                help='Prefix to install to [Default: %(default)s]')
    p.add_argument('-n', '--non-interactive', action='store_true',
            default=False, help='Do not ask before performing each action')
    p.add_argument('-r', '--remove', action='store_true', default=False,
            help='Remove existing files [Default: %(default)s]')
    p.add_argument('-v', '--verbose', action='store_true', default=False,
            help='Enable verbose output')
    args = p.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG,
                format='%(levelname)s: %(message)s)')

    print('Running post-install actions for', platform.system())
    if platform.system() == 'Linux':
        post_install_unix(args.prefix, args.bashrc_path, not
                args.non_interactive, args.remove)
    elif platform.system() == 'Darwin':
        post_install_unix(args.prefix, args.bashrc_path, not
                args.non_interactive, args.remove)
    elif platform.system() == 'Windows':
        post_install_windows(args.prefix, not args.non_interactive, args.remove)
    else:
        print('No post-install actions for', platform.system())


#  vim: set expandtab tabstop=8 shiftwidth=4 softtabstop=4 textwidth=79
