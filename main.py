"""Codeword Puzzle solver"""

import sys
import string
from collections import defaultdict
import re
from pathlib import Path
from typing import Optional


#######################################################################
class Letter:
    def __init__(self):
        self._possibles = set(string.ascii_lowercase)
        self._answer = ""

    def solve(self, letter: str):
        """A solution has been provided"""
        self._answer = letter

    def possibles(self) -> set[str]:
        return self._possibles

    def update(self, possibles: set[str]):
        """Update possible letters"""
        self._possibles &= possibles
        self._have_solved()

    def _have_solved(self):
        """Check to see if we have solved"""
        if len(self._possibles) == 1:
            self.solve(list(self._possibles)[0])

    def remove(self, letter: str):
        """Remove a letter from the possibles"""
        if letter in self._possibles:
            self._possibles.remove(letter)
            self._have_solved()

    def answer(self) -> Optional[str]:
        if self._answer:
            return self._answer
        return None

    def __repr__(self):
        if self.answer():
            return f"Answer: {self.answer()}"
        else:
            return f"Possibles: {' '.join(sorted(self._possibles))} ({len(self)})"

    def __len__(self):
        return len(self._possibles)


LETTERS: dict[int, Letter] = {}


#######################################################################
def read_puzzle_file(filename: Path) -> list[str]:
    """Read the puzzle file in"""
    with open(filename, "r") as puzzle_file:
        puzzle = puzzle_file.read()
    return puzzle.split("\n")


#######################################################################
def init_letters():
    """Initialize letters to all possibilities"""
    for i in range(1, 27):
        LETTERS[i] = Letter()


#######################################################################
def extract_clues(puzzle: list[str]) -> None:
    """Pull out any existing known letters
    Should be in format: <letter>=<number>
    """
    for line in puzzle:
        if line and line[0] in string.ascii_letters:
            letter, number = line.split("=")
            LETTERS[int(number)].solve(letter.lower())

            for v in LETTERS.values():
                v.remove(letter.lower())


#######################################################################
def extract_puzzles(raw_puzzle: list[str]) -> list[list[int]]:
    """Pull out the puzzles bits and convert"""
    puzzles = []
    for line in raw_puzzle:
        if not line or line[0] == "#":
            continue
        if line[0] in string.ascii_letters:
            continue
        puzzle = [int(_) for _ in line.split()]
        puzzles.append(puzzle)
    return puzzles


#######################################################################
def load_dictionary(filename: Path) -> list[str]:
    """Load the dictionary"""
    dictionary = []
    with open(filename, "r") as dictionary_file:
        for line in dictionary_file:
            if line[0] in string.ascii_lowercase:  # No proper nouns
                dictionary.append(line.lower())
    return dictionary


#######################################################################
def calc_regexp(puzzle: list[int]) -> re.Pattern:
    """Make a regexp to find appropriate words"""
    re_list = ["^"]
    for num in puzzle:
        if ans := LETTERS[num].answer():
            re_list.append(ans)
        else:
            possible_letters = "".join(list(LETTERS[num].possibles()))
            re_list.append(f"[{possible_letters}]")
    re_list.append("$")
    reg = re.compile("".join(re_list))
    return reg


#######################################################################
def get_possibles(puzzle: list[int], dictionary: list[str]) -> dict[int, set[str]]:
    """Return the possible letters for the puzzle"""
    possibles: dict[int, set[str]] = defaultdict(set)
    reg = calc_regexp(puzzle)

    matched = False
    for word in dictionary:
        if reg.match(word):
            word = word.strip()
            for num, char in enumerate(word):
                possibles[puzzle[num]].add(char)
            matched = True
    if not matched:
        print(f"Couldn't match {reg.pattern}")
        return {}
    return possibles


#######################################################################
def print_solution():
    unknowns = 0
    good = 0
    for k, v in LETTERS.items():
        if v.answer():
            good += 1
        print(f"{k}\t{v}")
        unknowns += len(v)
    print(f"Solved: {good}/26 = {good/26.0:.1%}")
    quality = 26 * 26 - unknowns
    print(f"Quality: {quality} ({quality/(26*26.0):.1%}) Unknowns: {unknowns}")


#######################################################################
def solve_iteration(puzzles: list[list[int]], dictionary: list[str]) -> None:
    """Solve for all puzzles"""
    for puzzle in puzzles:
        solve_puzzle(puzzle, dictionary)


#######################################################################
def solve_puzzle(puzzle: list[int], dictionary: list[str]):
    """Solve for a single puzzle"""
    possibles = get_possibles(puzzle, dictionary)
    for num, poss in possibles.items():
        LETTERS[num].update(poss)
        # If we now have an answer, remove that possibility from all other letters
        if LETTERS[num].answer():
            for v in LETTERS.values():
                v.remove(LETTERS[num].answer())


#######################################################################
def main():
    init_letters()
    dictionary = load_dictionary(Path("dictionary.txt"))
    raw_puzzles = read_puzzle_file(Path(sys.argv[1]))
    extract_clues(raw_puzzles)
    puzzles = extract_puzzles(raw_puzzles)
    for _ in range(3):
        solve_iteration(puzzles, dictionary)

    print_solution()


#######################################################################
if __name__ == "__main__":
    main()

# EOF
