# -*- coding: UTF-8 -*-

# Porpose: Contains test cases for the utils.py object.
# Rev: April.06.2020 *PEP8 compatible*

import sys
import os.path
import unittest

#print(sys.path)

PATH = os.path.realpath(os.path.abspath(__file__))

sys.path.insert(0, os.path.dirname(os.path.dirname(PATH)))



#print(PATH, sys.path.insert(0, os.path.dirname(os.path.dirname(PATH))))

try:
    from videomass3.Videomass3 import main as videomass
except ImportError as error:
    sys.exit(error)


class TestWxApp(unittest.TestCase):
    """Test case for the format_bytes function."""

    def test_main(self):
        #self.assertEqual(videomass, True)
        videomass()


def main():
    unittest.main()


if __name__ == '__main__':
    main()
