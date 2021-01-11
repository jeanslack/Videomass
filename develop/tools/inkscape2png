#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
#
# Name: inkscape2png
# Porpose: Wrapper interface to perform batch conversion using the
#          Inkscape library
# Compatibility: Python3
# Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
# Copyright: (c) 2020-2021 Gianluca Pernigotto <jeanlucperni@gmail.com>
# license: GPL3
# Rev: Oct.23.2020 *PEP8 compatible*

# DESCRIPTION:
#   Given a list of pathnames, recursively converts images found in SVG
#   vector format to PNG raster format or to the formats specified in
#   the --format argument.
#
#   Assume that the `inkscape` application is installed on the system:
#
#   Note, from version > 1.0 the inkscape syntax may be differ, e.g.:
#       use: inkscape -w 1024 -h 1024 input.svg --export-filename output.png
#   instead:
#       inkscape -z -w 1024 -h 1024 input.svg -e output.png
#
#########################################################

# This file is part of Videomass.

#    Videomass is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    Videomass is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with Videomass.  If not, see <http://www.gnu.org/licenses/>.
#
#########################################################################
import platform
import subprocess
import os
import glob
import argparse
import sys

def svg2png(delete, paths, parameters, outputdir,
            formatext, recursive: bool=False):
    """
    Iterates on a generator given from `glob.iglob` method.
    glob treats filenames beginning with a dot (.) as special cases,
    so hidden filenames will not be considered. To convert hidden
    filenames use `fnmatch` module instead of `glob` module.

    """
    cmd = ['inkscape', '-z']
    recurs = '**' if recursive else ''

    if formatext == "png":
        outext = ('-e', 'png')
    elif formatext == "svg":
        outext = ('-l', 'svg')
    elif formatext == "ps":
        outext = ('-P', 'ps')
    elif formatext == "eps":
        outext = ('-E', 'eps')
    elif formatext == "pdf":
        outext = ('-A', 'pdf')
    elif formatext == "emf":
        outext = ('-M', 'emf')
    elif formatext == "wmf":
        outext = ('-m', 'wmf')
    else:
        outext = ('-e', 'png')

    for k, v in parameters.items():
        if v:
            cmd.append(k)
            cmd.append(str(v))

    for path in paths:
        for files in glob.iglob(os.path.join(path, recurs, '*.svg'),
                                recursive=recursive
                                ):
            out = outputdir if outputdir else os.path.dirname(files)
            basename = os.path.splitext(os.path.basename(files))
            saveto = os.path.join('%s' % out, '%s.%s' % (basename[0],
                                                         outext[1]))
            if platform.system() == 'Windows':
                command = ' '.join(cmd + [files, outext[0], saveto])
            else:
                command = cmd + [files, outext[0], saveto]
            try:
                p = subprocess.run(command,
                                   capture_output=True,
                                   universal_newlines=True
                                   )
            except FileNotFoundError as err:
                return ("ERROR: 'inkscape': Command not found")

            if p.returncode:
                return "ARGS: %s\nERROR: %s" % (p.args, p.stderr)

            elif delete:
                try:
                    os.remove(files)
                except OSError as err:
                    return "ERROR: %s" % err
    return
    # -------------------------------------------------------------------#


def main():
    """
    Entry-point of the executable (users inputs parser, positional/optional
    arguments)

    """
    parser = argparse.ArgumentParser(
                description='Wrapper interface to perform batch conversion '
                            'using the `Inkscape` library. Given a list of '
                            'pathnames, recursively converts images found in '
                            'SVG vector format to PNG raster format or to '
                            'the formats specified in the --format argument:'
                            )
    parser.add_argument(
                '-W',
                required=False,
                metavar='WIDTH',
                #dest='<int>',
                type=int,
                help="width; defaults to the SVG's width",
                    )
    parser.add_argument(
                '-H',
                required=False,
                metavar='HEIGHT',
                type=int,
                help="height; defaults to the SVG's height",
                    )
    parser.add_argument(
                '-d',
                required=False,
                metavar='DPI',
                type=float,
                help="pixels per inch; defaults to 90dpi",
                    )
    parser.add_argument(
                '-f', '--format',
                choices=['png', 'pdf', 'ps', 'eps', 'svg', 'emf', 'wmf'],
                required=False,
                type=str,
                help="save format; defaults to 'png'",
                    )
    parser.add_argument(
                '-p', '--paths',
                nargs='+',
                metavar='..DIR ..DIR',
                required=True,
                help="Input dirname list separated by spaces",
                    )
    parser.add_argument(
                '-r', '--remove',
                action='store_true',
                required=False,
                help="If successful, remove all SVG source files when "
                     "finished",
                     )
    parser.add_argument(
                '-R', '--recursive',
                action='store_true',
                required=False,
                help="Recursive use (please be careful when used with "
                     "the `-r` argument)",
                     )
    parser.add_argument(
                '-o', '--output',
                metavar='..DIR',
                required=False,
                help="Provide an output directory to save all files",
                    )
    args = parser.parse_args()

    for p in args.paths:
        if not os.path.isdir(p):
            raise NotADirectoryError("Invalid or inexistent pathname for "
                                     "inputdir '%s'" % p)
            break

    if args.output:
        if not os.path.isdir(args.output):
            raise NotADirectoryError("Invalid or inexistent pathname for "
                                     "outputdir '%s'" % args.output)

    if args.format == 'svg' and not args.output:
        raise FileExistsError('Could not overwrite the SVG files themselves. '
                              'You must provide an output pathname using the '
                              '-o argument.')


    param = {'-w' : args.W, '-h' : args.H, '-d' : args.d}

    ret = svg2png(args.remove,
                  args.paths,
                  param,
                  args.output,
                  args.format,
                  args.recursive,
                  )
    if ret:
        sys.exit(ret)
    else:
        print('Done! :-)')
        sys.exit()
    # ----------------------------------------------------------------#


if __name__ == '__main__':
    main()
