# -*- coding: UTF-8 -*-

# Porpose: Contains test cases for the ffprobe_parser object.
# Rev: Oct.04.2020 *PEP8 compatible*

import sys
import os.path
import unittest

if sys.version_info[0] != 3:
    sys.exit('\nERROR: You are using an unsupported version of Python. '
             'Python3 is required.\n')

PATH = os.path.realpath(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(PATH)))

try:
    from videomass.vdms_threads.ffprobe import ffprobe
except ImportError as error:
    sys.exit(error)


class FFprobeTestCase(unittest.TestCase):
    """Test case for FFProbe"""

    def setUp(self):
        """Method called to prepare the test fixture"""

        filename_url = 'url'
        ffprobe_url = ''

        self.data = ffprobe(filename_url,
                            ffprobe_url,
                            hide_banner=None,
                            pretty=None
                            )

    def test_invalid_urls(self):
        """
        test error with an invalid url filename and/or
        invalid executable.

        """
        if self.data[1]:
            self.assertRaises(AssertionError)
            self.assertEqual(self.data[0], None)

    def test_available_urls(self):
        """
        test with an existing filename such video, audio, picture
        and a valid link to the installed executable.
        Specifically, the basename of the executable must be ffprobe
        or ffprobe.exe for MS

        """
        if not self.data[1]:
            self.assertEqual(self.data[1], None)
            self.assertTrue(self.data[0])


def main():
    unittest.main()


if __name__ == '__main__':
    main()
