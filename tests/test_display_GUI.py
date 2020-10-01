# -*- coding: UTF-8 -*-

# Porpose: Contains test cases for the Videomass3 object.
# Rev: June.03.2020 *PEP8 compatible*

import sys
import os.path
import unittest

if sys.version_info[0] != 3:
    sys.exit('\nERROR: You are using an unsupported version of Python. '
             'Please use Python3.\n')

PATH = os.path.realpath(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(PATH)))

try:
    import wx
    from videomass3 import Videomass3

except ImportError as error:
    sys.exit(error)


class GuiTestCase(unittest.TestCase):
    """
    Test case for Videomass GUI. It tests the bootstrap of
    the wxPython module by start Videomass app.
    """

    def setUp(self):
        """Method called to prepare the test fixture"""

        self.app = Videomass3.Videomass(redirect=False)

    def tearDown(self):
        """start MainLoop """
        def _cleanup():
            for tlw in wx.GetTopLevelWindows():
                if tlw:
                    #tlw.Close(force=True)
                    tlw.Destroy()
            wx.WakeUpIdle()

        #timer = wx.PyTimer(_cleanup)
        #timer.Start(100)
        wx.CallLater(100, _cleanup)
        self.app.MainLoop()
        del self.app

    def test_instance(self):
        """
        test error with an invalid url filename and/or
        invalid executable.

        """
        #if self.data.ERROR():
            #self.assertRaises(AssertionError)
            #self.assertEqual(self.data.data_format(), [])
        if self.app:
            self.assertTrue(self.app)


def main():
    unittest.main()


if __name__ == '__main__':
    main()
