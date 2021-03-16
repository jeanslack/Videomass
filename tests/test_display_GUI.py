# -*- coding: UTF-8 -*-

# Porpose: Contains test cases for the Videomass3 object.
# Rev: Oct.04.2020 *PEP8 compatible*

import sys
import os.path
import unittest

if sys.version_info[0] != 3:
    sys.exit('\nERROR: You are using an unsupported version of Python. '
             'Python3 is required..\n')

PATH = os.path.realpath(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(PATH)))

try:
    import wx

except ImportError as error:
    sys.exit(error)

else:
    from videomass3 import Videomass3


class GuiTestCase(unittest.TestCase):
    """
    Test case for Videomass GUI. It tests the bootstrap of
    the wxPython module by starting Videomass app.
    """

    def setUp(self):
        """Method called to prepare the test fixture"""

        self.app = Videomass3.Videomass(redirect=False)

    def tearDown(self):
        """
        start MainLoop and destroy
        see:
            - https://github.com/wxWidgets/Phoenix/blob/master/unittests/wtc.py
            - https://stackoverflow.com/questions/33292441/how-to-destroy-a-wxpython-frame-in-unittest
        """
        def _cleanup():
            for tlw in wx.GetTopLevelWindows():
                if tlw:
                    # tlw.Close(force=True)
                    tlw.Destroy()
            wx.WakeUpIdle()

        # timer = wx.PyTimer(_cleanup)
        # timer.Start(100)
        wx.CallLater(100, _cleanup)
        self.app.MainLoop()
        del self.app

    def test_app(self):
        """test app"""
        if self.app:
            self.assertTrue(self.app)


def main():
    unittest.main()


if __name__ == '__main__':
    main()
