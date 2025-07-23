#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
""""
Porpose: Manage the translation message catalog independently
         of the GNU-xgettext utilities.
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2025 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: Distributed under the terms of the GPL3 License.
Rev: July.23.2025
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


def description():
    """
    print description of the program
    """
    descr = ('Encapsulates the main functionalities for managing '
             'the translation message catalog based on babel.')

    return descr


def long_description():
    """
    print a long description of the program
    """
    descr = ('Encapsulates the main functionalities for managing '
             'the translation message catalog based on babel.\n'
             'Please note that these functionalities are mutually '
             'exclusive, use one at a time.\n')

    return descr


def exit_from_prog(nameprogram, args=None):
    """
    print message error and exit from program
    """

    print(f"\nIMPORTANT: This script is semi-automatic, in order to use "
          f"the default directories it is encouraged to call this script "
          f"from the source directory location.\n\n"
          f"usage: {nameprogram} [-h] (--extract-msg | --new-catalog | "
          f"--update-catalogs | --compile-catalogs)\n\n{long_description()}")
    if args:
        print(args)

    sys.exit()


def build_translation_catalog(nameprogram, def_locdir, def_domain):
    """
    Compile MO files for this macchine using babel.
    """
    parser = argparse.ArgumentParser(prog=f'{nameprogram}',
                                     description=description(),
                                     add_help=True,
                                     )
    parser.add_argument('--compile-catalogs',
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
    args = parser.parse_args()
    try:
        cmd = compile_catalog()
        cmd.directory = args.locale_directory
        cmd.domain = args.domain_name
        cmd.statistics = True
        cmd.finalize_options()
        cmd.run()
    except Exception as err:
        return err

    return None


def create_pot_file(nameprogram, here, def_locdir, def_domain, def_pypkg):
    """
    Extract messages from the catalog, similarly to what
    the GNU gettext program does.
    """
    parser = argparse.ArgumentParser(prog=f'{nameprogram}',
                                     description=description(),
                                     add_help=True,
                                     )

    parser.add_argument('--extract-msg',
                        help=("Extracts messages from the catalog and adds "
                              "them to a new POT file."),
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
    parser.add_argument("-p", "--package-dir",
                        action="store",
                        dest="python_package_dir",
                        help=(f'Absolute or relative destination path to '
                              f'the Python modules/package dir to extract '
                              f'recursively all messages from *.py files, '
                              f'default is "{def_pypkg}".'),
                        required=False,
                        default=def_pypkg,
                        )
    args = parser.parse_args()
    makeabs_locdir = os.path.abspath(args.locale_directory)
    makeabs_pydir = os.path.abspath(args.python_package_dir)
    os.chdir(args.locale_directory)
    pydir = os.path.relpath(makeabs_pydir)
    try:
        cmd = extract_messages()
        cmd.input_dirs = pydir  # path to Pytohn package
        cmd.output_file = os.path.join(makeabs_locdir,
                                       args.domain_name.lower() + ".pot")
        cmd.no_wrap = True
        cmd.finalize_options()
        cmd.run()
    except Exception as err:
        os.chdir(here)
        return err
    os.chdir(here)
    return None


def update_po_files(nameprogram, def_locdir, def_domain, def_potfile):
    """
    Updates all existing translation catalogs based on a
    PO template file (POT), basically equivalent to the GNU
    msgmerge program.
    """
    parser = argparse.ArgumentParser(prog=f'{nameprogram}',
                                     description=description(),
                                     add_help=True,
                                     )
    parser.add_argument('--update-catalogs',
                        help=("Updates all existing translation catalogs "
                              "found on the given locale directory based on "
                              "a POT template file."),
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
    parser.add_argument("-f", "--pot-file",
                        action="store",
                        dest="pot_file",
                        help=(f'POT filename location, default is '
                              f'"{def_potfile}".'),
                        required=False,
                        default=def_potfile,
                        )
    args = parser.parse_args()
    try:
        cmd = update_catalog()
        cmd.input_file = args.pot_file
        cmd.domain = args.domain_name
        cmd.output_dir = args.locale_directory
        cmd.no_wrap = True
        cmd.no_fuzzy_matching = True
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
                                     description=description(),
                                     add_help=True,
                                     )
    parser.add_argument('--new-catalog',
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
    args = parser.parse_args()
    try:
        cmd = init_catalog()
        cmd.domain = args.domain_name.lower()
        cmd.locale = args.locale_code
        cmd.input_file = os.path.join(args.locale_directory,
                                      args.domain_name.lower() + ".pot")
        cmd.output_dir = args.locale_directory
        cmd.finalize_options()
        cmd.run()
    except Exception as err:
        return err

    return None


if __name__ == '__main__':
    prgname = os.path.basename(__file__)
    heredir = os.getcwd()  # must be source directory
    locdir = os.path.join(heredir, 'videomass', 'data', 'locale')
    domain = 'videomass'
    pypkgdir = os.path.join(heredir, 'videomass')
    potfilename = os.path.join(locdir, 'videomass.pot')

    mode = ('--new-catalog', '--extract-msg',
            '--update-catalogs', '--compile-catalogs')
    arg = sys.argv
    appendact = [a for a in sys.argv if a in mode]
    status = None

    if not appendact:
        exit_from_prog(prgname)

    if len(appendact) > 1:
        msg = (f"ERROR: {prgname}: the following arguments "
               f"are mutually exclusive: {mode} "
               f"go for > {' '.join(appendact)}")
        exit_from_prog(prgname, msg)

    if appendact[0] == "--new-catalog":
        status = init_new_catalog(prgname, locdir, domain)

    elif appendact[0] == "--extract-msg":
        status = create_pot_file(prgname, heredir, locdir, domain, pypkgdir)

    elif appendact[0] == "--update-catalogs":
        status = update_po_files(prgname, locdir, domain, potfilename)

    elif appendact[0] == "--compile-catalogs":
        status = build_translation_catalog(prgname, locdir, domain)

    if status:
        print(f"ERROR: babel: {status}")
    else:
        print("COMPLETED SUCCESSFULLY!")
