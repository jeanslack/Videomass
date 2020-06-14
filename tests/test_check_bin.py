# -*- coding: UTF-8 -*-

# Porpose: Contains test cases for the check_bin object.
# Rev: June.14.2020 *PEP8 compatible*

import sys
import platform
import os.path
import unittest

if sys.version_info[0] != 3:
    sys.exit('\nERROR: You are using an unsupported version of Python. '
             'Please use Python3.\n')

PATH = os.path.realpath(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(PATH)))

try:
    from videomass3.vdms_threads.check_bin import ff_conf
except ImportError as error:
    sys.exit(error)


class CheckFFmpegTestCase(unittest.TestCase):
    """Test case for FFmpeg"""

    def setUp(self):
        """Method called to prepare the test fixture"""
        if platform.system() == 'Windows':
            ffmpeg_url = 'ffmpeg.exe'
        else:
            ffmpeg_url = 'ffmpeg'

        self.out = ff_conf(ffmpeg_url, platform.system())

    def test_invalid_executable(self):
        """
        test error with an invalid or not found ffmpeg executable.

        """
        if 'Not found' in self.out[0]:
            self.assertRaises(AssertionError)
            self.assertEqual(self.out[0], 'Not found')

    def test_available_executable(self):
        """
        test with a valid ffmpeg executable installed on path name
        of the environment variables.
        """
        if 'None' in self.out[0]:
            self.assertEqual(self.out[0], 'None')
            self.assertTrue(self.out)


def main():
    unittest.main()


if __name__ == '__main__':
    main()
