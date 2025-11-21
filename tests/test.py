#!/usr/bin/env python
"""Test suite"""

import unittest
from main import calc_regexp, Alphabet


#######################################################################
class TestCalcRegex(unittest.TestCase):
    """Test calc_regexp()"""

    def setUp(self):
        self.alphabet = Alphabet()
        self.alphabet.solve(1, "a")

    def test_known(self):
        """Test regexp with known letter"""
        reg = calc_regexp(self.alphabet, [1])
        self.assertEqual(reg.pattern, "^a$")

    def test_unknown(self):
        """Test regexp without a known letter"""
        reg = calc_regexp(self.alphabet, [2])
        self.assertEqual(reg.pattern, "^[bcdefghijklmnopqrstuvwxyz]$")


########################################################################
if __name__ == "__main__":  # pragma: no cover
    unittest.main()
