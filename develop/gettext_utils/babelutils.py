# Copyleft (c) Videomass Development Team.
# Distributed under the terms of the GPL3 License.

import os
import sys
from babel.messages.frontend import compile_catalog


def build_translation_catalog(pathtolocale):
    cmd = compile_catalog()
    cmd.directory = pathtolocale
    cmd.domain = "videomass"
    cmd.statistics = True
    cmd.finalize_options()
    cmd.run()

if __name__ == '__main__':
    if not len(sys.argv) > 1:
        sys.exit('ERROR: Please provide path to locale directory.')

    pathtolocale = sys.argv[1]
    if os.path.exists(pathtolocale) and os.path.isdir(pathtolocale):
        build = build_translation_catalog(pathtolocale)
    else:
        sys.exit(f'ERROR: Invalid pathname «{pathtolocale}».')
