#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
""""
Porpose: Conveniently wraps the Babel API to suit your specific needs,
         independently of the GNU-xgettext utilities.
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2025 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: Distributed under the terms of the GPL3 License.
Rev: July.29.2025
Code checker: flake8, pylint

This file is part of videomass.

    videomass is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    videomass is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with videomass.  If not, see <http://www.gnu.org/licenses/>.
"""

import os
import sys
import argparse
try:
    from babel.messages.frontend import (compile_catalog,
                                         extract_messages,
                                         update_catalog,
                                         init_catalog
                                         )
except ModuleNotFoundError:
    sys.exit('Babel for Python3 is required, please install babel before '
             'launch this script.')


def long_descript():
    """
    print a long description of the program
    """
    descr = ('Encapsulates the babel API for working with message '
             'catalog conveniently.\n'
             'Please note that this script is not intended to replace the '
             '`pybabel` command line.\nIt is intended to study the Babel API '
             'and provide some convenience for the program that uses it.\n')
    return descr


def exit_from_prog(nameprogram, args=None):
    """
    print message error and exit from program
    """

    print(f"Usage: {nameprogram} [-h] (--init | --extract | --update | "
          f"--compile)\n\n{long_descript()}")
    if args:
        print(args)

    sys.exit()


def build_translation_catalog(nameprogram, def_locdir, def_domain):
    """
    Compile MO files for this macchine using babel.
    """
    parser = argparse.ArgumentParser(prog=f'{nameprogram}',
                                     description=long_descript(),
                                     add_help=True,
                                     )
    parser.add_argument('compile',
                        help=("Compile recursively MO (Machine Object) files "
                              "for this macchine."),
                        action="store_true",
                        required=True,
                        )
    parser.add_argument("-o", "--output-dir",
                        action="store",
                        dest="locale_directory",
                        help=(f'Absolute or relative destination path to '
                              f'locale directory, default is "{def_locdir}".'),
                        required=False,
                        default=def_locdir,
                        )
    parser.add_argument("-d", "--domain",
                        action="store",
                        dest="domain_name",
                        help=(f'The name given to the domain of the PO file '
                              f'of any catalogs, default is "{def_domain}".'),
                        required=False,
                        default=def_domain,
                        )
    parsargs = parser.parse_args()
    try:
        cmd = compile_catalog()
        cmd.directory = parsargs.locale_directory
        cmd.domain = parsargs.domain_name
        cmd.statistics = True
        cmd.finalize_options()
        cmd.run()
    except Exception as err:
        return err

    return None


def create_pot_file(*args):
    """
    Extract messages from the catalog, similarly to what
    the GNU gettext program does.
    This is equivalent to pybabel command line:
        pybabel extract --no-location -o /path/videomass.pot  -w 400
        --project Videomass --version 6.1.13 --ignore-dirs="DATA __pycache__"
        --input-dirs="/path/Videomass/videomass"
    """
    parser = argparse.ArgumentParser(prog=f'{args[0]}',
                                     description=long_descript(),
                                     add_help=True,
                                     )
    parser.add_argument('--extract',
                        help=("Extract messages from source files and "
                              "generate a POT file."),
                        action="store_true",
                        required=True
                        )
    parser.add_argument("-o", "--output-dir",
                        action="store",
                        dest="locale_directory",
                        help=(f'Absolute or relative destination path to '
                              f'locale directory, default is "{args[2]}".'),
                        required=False,
                        default=args[2],
                        )
    parser.add_argument("-d", "--domain",
                        action="store",
                        dest="domain_name",
                        help=(f'The name you want to give to the domain, '
                              f'usually coincides with the name of your app '
                              f'or the existing PO/POT file (in lowercase), '
                              f'default is "{args[3]}".'),
                        required=False,
                        default=args[3],
                        )
    parser.add_argument("-p", "--package-dir",
                        action="store",
                        dest="python_package_dir",
                        help=(f'Absolute or relative destination path to '
                              f'the Python modules/package dir to extract '
                              f'recursively all messages from *.py files, '
                              f'default is "{args[4]}".'),
                        required=False,
                        default=args[4],
                        )
    parser.add_argument('-w', "--no-wrap",
                        action="store_true",
                        dest="no_wrap",
                        help=('Do not break long message lines, longer than '
                              'the output line width, into several lines.'),
                        required=False,
                        default=False,
                        )
    parser.add_argument('-W', "--width",
                        action="store",
                        type=int,
                        dest="width",
                        help=('set output line width (default 76)'),
                        required=False,
                        default=76,
                        )
    parser.add_argument('-Nf', "--no-fuzzy-matching",
                        action="store_true",
                        dest="no_fuzzy",
                        help=('do not use fuzzy matching'),
                        required=False,
                        default=False,
                        )
    parser.add_argument('-Nl', "--no-location",
                        action="store_true",
                        dest="no_location",
                        help=('do not include location comments with filename '
                              'and line number'),
                        required=False,
                        default=False,
                        )
    parsargs = parser.parse_args()
    makeabs_locdir = os.path.abspath(parsargs.locale_directory)
    makeabs_pydir = os.path.abspath(parsargs.python_package_dir)
    os.chdir(parsargs.locale_directory)
    pydir = os.path.relpath(makeabs_pydir)
    try:
        cmd = extract_messages()
        cmd.input_dirs = pydir  # path to Pytohn package
        cmd.output_file = os.path.join(makeabs_locdir,
                                       parsargs.domain_name.lower() + ".pot")
        cmd.ignore_dirs = "DATA __pycache__"
        cmd.project = 'Videomass'
        # cmd.version = '6.1.13'
        cmd.width = parsargs.width
        if parsargs.no_wrap:
            cmd.no_wrap = parsargs.no_wrap
        if parsargs.no_fuzzy:
            cmd.no_fuzzy_matching = parsargs.no_fuzzy
        if parsargs.no_location:
            cmd.no_location = parsargs.no_location
        cmd.finalize_options()
        cmd.run()
    except Exception as err:
        os.chdir(args[1])
        return err
    os.chdir(args[1])
    return None


def update_po_files(*args):
    """
    Updates existing message catalogs based on the template
    file (POT). Basically equivalent to the GNU msgmerge program.
    Also equivalent to pybabel command line:
        pybabel update -D videomass -i "videomass/data/locale/videomass.pot"
        -d "videomass/data/locale" -w 400 --ignore-obsolete -N
        --update-header-comment
    """
    parser = argparse.ArgumentParser(prog=f'{args[0]}',
                                     description=long_descript(),
                                     add_help=True,
                                     )
    parser.add_argument('--update',
                        help=("Updates existing message catalogs found "
                              "on the given locale directory from a POT file."
                              ),
                        action="store_true",
                        required=True,
                        )
    parser.add_argument("-o", "--output-dir",
                        action="store",
                        dest="locale_directory",
                        help=(f'Absolute or relative destination path to '
                              f'locale directory, default is "{args[1]}".'),
                        required=False,
                        default=args[1],
                        )
    parser.add_argument("-d", "--domain",
                        action="store",
                        dest="domain_name",
                        help=(f'The name given to the domain of the PO file '
                              f'of any catalogs, default is "{args[2]}".'),
                        required=False,
                        default=args[2],
                        )
    parser.add_argument("-f", "--pot-file",
                        action="store",
                        dest="pot_file",
                        help=(f'POT filename location, default is '
                              f'"{args[3]}".'),
                        required=False,
                        default=args[3],
                        )
    parser.add_argument('-w', "--no-wrap",
                        action="store_true",
                        dest="no_wrap",
                        help=('Do not break long message lines, longer than '
                              'the output line width, into several lines.'),
                        required=False,
                        default=False,
                        )
    parser.add_argument('-W', "--width",
                        action="store",
                        type=int,
                        dest="width",
                        help=('set output line width (default 76)'),
                        required=False,
                        default=76,
                        )
    parser.add_argument('-Nf', "--no-fuzzy-matching",
                        action="store_true",
                        dest="no_fuzzy",
                        help=('do not use fuzzy matching'),
                        required=False,
                        default=False,
                        )
    parser.add_argument('-Nl', "--no-location",
                        action="store_true",
                        dest="no_location",
                        help=('do not include location comments with filename '
                              'and line number'),
                        required=False,
                        default=False,
                        )
    parsargs = parser.parse_args()
    try:
        cmd = update_catalog()
        cmd.input_file = parsargs.pot_file
        cmd.domain = parsargs.domain_name
        cmd.output_dir = parsargs.locale_directory
        cmd.width = parsargs.width
        cmd.update_header_comment = True
        if parsargs.no_wrap:
            cmd.no_wrap = parsargs.no_wrap
        if parsargs.no_fuzzy:
            cmd.no_fuzzy_matching = parsargs.no_fuzzy
        if parsargs.no_location:
            cmd.no_location = parsargs.no_location
        cmd.finalize_options()
        cmd.run()
    except Exception as err:
        return err

    return None


def init_new_catalog(nameprogram, def_locdir, def_domain):
    """
    Basically equivalent to the GNU msginit program: it creates
    a new translation catalog based on a PO template file (POT).
    """
    parser = argparse.ArgumentParser(prog=f'{nameprogram}',
                                     description=long_descript(),
                                     add_help=True,
                                     )
    parser.add_argument('init',
                        help=("It creates a new translation catalog based on "
                              "a POT template file."),
                        action="store_true",
                        required=True
                        )
    parser.add_argument("-o", "--output-dir",
                        action="store",
                        dest="locale_directory",
                        help=(f'Absolute or relative destination path to '
                              f'locale directory, default is "{def_locdir}".'),
                        required=False,
                        default=def_locdir,
                        )
    parser.add_argument("-d", "--domain",
                        action="store",
                        dest="domain_name",
                        help=(f'The name you want to give to the domain, '
                              f'usually coincides with the name of your app '
                              f'or the existing PO/POT file (in lowercase), '
                              f'default is "{def_domain}".'),
                        required=False,
                        default=def_domain,
                        )
    parser.add_argument("-l", "--locale",
                        action="store",
                        dest="locale_code",
                        help=("Enter name of new locale code you want to "
                              "add, e.g 'de_DE' for German language."),
                        required=True,
                        )
    parsargs = parser.parse_args()
    try:
        cmd = init_catalog()
        cmd.domain = parsargs.domain_name.lower()
        cmd.locale = parsargs.locale_code
        cmd.input_file = os.path.join(parsargs.locale_directory,
                                      parsargs.domain_name.lower() + ".pot")
        cmd.output_dir = parsargs.locale_directory
        cmd.finalize_options()
        cmd.run()
    except Exception as err:
        return err

    return None


if __name__ == '__main__':
    prgname = os.path.basename(__file__)
    heredir = os.getcwd()  # must be source directory
    locdir = os.path.join(heredir, 'videomass', 'data', 'locale')
    DOMAIN = 'videomass'
    pypkgdir = os.path.join(heredir, 'videomass')
    potfilename = os.path.join(locdir, 'videomass.pot')

    mode = ('--init', '--extract', '--update', '--compile')
    arg = sys.argv
    appendact = [a for a in sys.argv if a in mode]
    STATUS = None

    if not appendact:
        exit_from_prog(prgname)

    if len(appendact) > 1:
        MSG = (f"ERROR: {prgname}: the following arguments "
               f"are mutually exclusive: {mode} "
               f"go for > {' '.join(appendact)}")
        exit_from_prog(prgname, MSG)

    if appendact[0] == "--init":
        STATUS = init_new_catalog(prgname, locdir, DOMAIN)

    elif appendact[0] == "--extract":
        STATUS = create_pot_file(prgname, heredir, locdir, DOMAIN, pypkgdir)

    elif appendact[0] == "--update":
        STATUS = update_po_files(prgname, locdir, DOMAIN, potfilename)

    elif appendact[0] == "--compile":
        STATUS = build_translation_catalog(prgname, locdir, DOMAIN)

    if STATUS:
        print(f"ERROR: babel: {STATUS}")
    else:
        print("COMPLETED SUCCESSFULLY!")
