#!/usr/bin/env python
"""Test suite"""

import unittest
import io
import re
import contextlib
from pathlib import Path

from main import (
    calc_regexp,
    Alphabet,
    extract_clues,
    extract_puzzles,
    get_possibles,
    solve_puzzle,
    Letter,
    Alphabet,
    load_dictionary,
    read_puzzle_file,
)


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

    def test_combined(self):
        """Test regexp without a known letter"""
        reg = calc_regexp(self.alphabet, [1, 2])
        self.assertEqual(reg.pattern, "^a[bcdefghijklmnopqrstuvwxyz]$")

    def test_dupe(self):
        """Test regexp with a repeated letter"""
        reg = calc_regexp(self.alphabet, [2, 3, 1, 3])
        self.assertEqual(
            reg.pattern,
            r"^[bcdefghijklmnopqrstuvwxyz]([bcdefghijklmnopqrstuvwxyz])a\1$",
        )

    def test_repeated_dupe(self):
        """Test regexp with a repeated letter"""
        reg = calc_regexp(self.alphabet, [2, 3, 1, 3, 2, 3])
        self.assertEqual(
            reg.pattern,
            r"^([bcdefghijklmnopqrstuvwxyz])([bcdefghijklmnopqrstuvwxyz])a\2\1\2$",
        )


########################################################################
class TestExtractClues(unittest.TestCase):
    """Test extract_clues()"""

    def setUp(self):
        self.alphabet = Alphabet()

    def test_extract(self):
        """Test we are extracting clues"""
        self.assertIsNone(self.alphabet.answer(3))
        extract_clues(self.alphabet, ["A=3"])
        self.assertEqual(self.alphabet.answer(3), "a")

    def test_bad_line(self):
        """Test we catch bad lines"""
        f = io.StringIO()
        with contextlib.redirect_stderr(f):
            extract_clues(self.alphabet, ["whatever", "A=3"])
            self.assertIn("Unhandled line: whatever", f.getvalue())
            self.assertEqual(self.alphabet.answer(3), "a")


########################################################################
class TestExtractPuzzles(unittest.TestCase):
    """Test extract_puzzles()"""

    def test_extract(self):
        """Test we are extracting clues"""
        ans = extract_puzzles(
            [
                "A=3",
                "1 2 3",
            ]
        )
        self.assertEqual(ans, [[1, 2, 3]])

    def test_bad_line(self):
        """Test invalid lines are reported"""
        f = io.StringIO()
        with contextlib.redirect_stderr(f):
            ans = extract_puzzles(["A=3", "1 2 3", "1 a"])
            self.assertEqual(ans, [[1, 2, 3]])
            self.assertIn("1 a - couldn't convert", f.getvalue())

    def test_bad_numbers(self):
        """Test invalid numbers are reported"""
        f = io.StringIO()
        with contextlib.redirect_stderr(f):
            ans = extract_puzzles(["1 2 3", "1 27"])
            self.assertEqual(ans, [[1, 2, 3]])
            self.assertIn("1 27 - numbers out of bound", f.getvalue())


########################################################################
class TestGetPossibles(unittest.TestCase):
    """Test get_possibles()"""

    def test_match(self):
        """Test a match"""
        reg = re.compile("^c[aeiou]t$")
        ans = get_possibles([1, 2, 3], reg, ["cat", "dog", "cut"])
        self.assertEqual(ans, {1: {"c"}, 2: {"u", "a"}, 3: {"t"}})

    def test_no_match(self):
        """Test where there is no match"""
        reg = re.compile("^c[aeiou]t$")
        ans = get_possibles([1, 2, 3], reg, ["dog", "bird"])
        self.assertEqual(ans, {})


########################################################################
class TestLoadDictionary(unittest.TestCase):
    """Test load_dictionary()"""

    def test_load(self):
        ans = load_dictionary(Path("tests/test_dict.txt"))
        self.assertIn("cat", ans)
        self.assertNotIn("Arthur", ans)


########################################################################
class TestReadPuzzleFile(unittest.TestCase):
    """Test read_puzzle_file()"""

    def test_read(self):
        ans = read_puzzle_file(Path("tests/test_puzzle.txt"))
        self.assertEqual(ans, ["1 2 3 4", "Z=5"])


########################################################################
class TestSolvePuzzle(unittest.TestCase):
    """Test solve_puzzle()"""

    def setUp(self):
        self.alphabet = Alphabet()

    def test_solve(self):
        """Solve a puzzle"""
        solve_puzzle(self.alphabet, [1, 2, 3], ["cat", "dog", "lemur"])
        self.assertEqual(self.alphabet[1].possibles(), {"c", "d"})
        self.assertEqual(self.alphabet[2].possibles(), {"a", "o"})
        self.assertEqual(self.alphabet[3].possibles(), {"t", "g"})


########################################################################
class TestLetter(unittest.TestCase):
    """Test Letter class"""

    def test_solve(self):
        """test solve()"""
        l = Letter()
        self.assertIsNone(l.answer())
        l.solve("a")
        self.assertEqual(l.answer(), "a")

    def test_update(self):
        """test update()"""
        l = Letter()
        self.assertEqual(len(l), 26)
        l.update({"c", "a", "t"})
        self.assertEqual(len(l), 3)
        self.assertEqual(l.possibles(), {"c", "a", "t"})
        l.update({"a", "e", "i", "o", "u"})
        self.assertEqual(l.possibles(), {"a"})
        self.assertEqual(l.answer(), "a")

    def test_remove(self):
        """Test remove()"""
        l = Letter()
        l.update({"a", "e", "i", "o", "u"})
        self.assertEqual(len(l), 5)
        l.remove("i")
        self.assertEqual(l.possibles(), {"a", "e", "o", "u"})
        self.assertEqual(len(l), 4)


########################################################################
class TestAlphabet(unittest.TestCase):
    """Test Alphabet class"""

    def test_init(self):
        """Test init()"""
        a = Alphabet()
        self.assertEqual(len(a[1]), 26)

    def test_solve(self):
        """Test solve()"""
        a = Alphabet()
        self.assertIn("a", a[2].possibles())
        a.solve(1, "a")
        self.assertNotIn("a", a[2].possibles())


########################################################################
if __name__ == "__main__":  # pragma: no cover
    unittest.main()
