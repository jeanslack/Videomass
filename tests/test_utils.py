# -*- coding: UTF-8 -*-

# Porpose: Contains test cases for the utils.py object.
# Rev: 07.Feb.2024

import sys
import os.path
import unittest

PATH = os.path.realpath(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(PATH)))

try:
    from videomass.vdms_utils.utils import (format_bytes,
                                            to_bytes,
                                            time_to_integer,
                                            integer_to_time,
                                            )
except ImportError as error:
    sys.exit(error)


class TestFormatBytes(unittest.TestCase):
    """Test case for the format_bytes function."""

    def test_format_bytes_bytes(self):
        self.assertEqual(format_bytes(518.00), "518.00B")

    def test_format_bytes_kilobytes(self):
        self.assertEqual(format_bytes(1024.00), "1.00KiB")

    def test_format_bytes_megabytes(self):
        self.assertEqual(format_bytes(1048576.00), "1.00MiB")

    def test_format_bytes_gigabytes(self):
        self.assertEqual(format_bytes(1073741824.00), "1.00GiB")

    def test_format_bytes_terabytes(self):
        self.assertEqual(format_bytes(1099511627776.00), "1.00TiB")


class TestToBytes(unittest.TestCase):
    """Test case for the to_bytes function."""

    def test_to_bytes_bytes(self):
        self.assertEqual(to_bytes("596.00byte"), 596.00)
        self.assertEqual(to_bytes("133.55byte"), 133.55)

    def test_to_bytes_kilobytes(self):
        self.assertEqual(to_bytes("1.00Kibyte"), 1024.00)
        self.assertEqual(to_bytes("5.55Kbyte"), 5683.20)

    def test_to_bytes_megabytes(self):
        self.assertEqual(to_bytes("13.64Mibyte"), 14302576.64)
        self.assertEqual(to_bytes("1.00Mbyte"), 1048576.00)

    def test_to_bytes_gigabytes(self):
        self.assertEqual(to_bytes("1.00Gibyte"), 1073741824.00)
        self.assertEqual(to_bytes("1.55Gbyte"), 1664299827.20)

    def test_to_bytes_terabytes(self):
        self.assertEqual(to_bytes("1.00Tibyte"), 1099511627776.00)
        self.assertEqual(to_bytes("1.00Tbyte"), 1099511627776.00)


class Test_time_to_integer(unittest.TestCase):
    """ Test case for the `time_to_integer` function"""

    def test_to_get_seconds(self):
        self.assertEqual(time_to_integer('N/A', sec=True), 0)
        self.assertEqual(time_to_integer('00:00:00', sec=True), 0)
        self.assertEqual(time_to_integer('00:00:55', sec=True), 55)
        self.assertEqual(time_to_integer('00:50:23', sec=True), 3023)
        self.assertEqual(time_to_integer('02:30:50', sec=True), 9050)

    def test_to_get_milliseconds(self):
        self.assertEqual(time_to_integer('any string', sec=False), 0)
        self.assertEqual(time_to_integer('00:00:00', sec=False), 0)
        self.assertEqual(time_to_integer('00:00:55.777', sec=False), 55777)
        self.assertEqual(time_to_integer('00:50:23', sec=False), 3023000)
        self.assertEqual(time_to_integer('02:30:50', sec=False), 9050000)

    def test_assertion_errors(self):
        with self.assertRaises(TypeError):
            # Accepts str only not any other types
            time_to_integer(160999)


class TestTimeHuman(unittest.TestCase):
    """ Test case for the time_human function"""

    def test_to_human(self):
        self.assertEqual(integer_to_time(round(0.0 * 1000),
                                         mills=False), '00:00:00')
        self.assertEqual(integer_to_time(round(55.0 * 1000),
                                         mills=False), '00:00:55')
        self.assertEqual(integer_to_time(round(3023.0 * 1000),
                                         mills=False), '00:50:23')
        self.assertEqual(integer_to_time(round(9050.0 * 1000),
                                         mills=False), '02:30:50')


def main():
    unittest.main()


if __name__ == '__main__':
    main()
