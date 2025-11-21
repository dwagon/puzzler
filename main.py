"""Codeword Puzzle solver"""

import sys
import string
from collections import defaultdict
import re
from pathlib import Path
from typing import Optional


#######################################################################
class Letter:
    """Class to store possible answers for a letter"""

    def __init__(self):
        self._possibles = set(string.ascii_lowercase)
        self._answer = ""

    def solve(self, letter: str):
        """A solution has been provided"""
        self._answer = letter

    def possibles(self) -> set[str]:
        """Return possible letters"""
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


#######################################################################
class Alphabet:
    """Class to store all the letter solutions"""

    def __init__(self):
        """Initialize letters to all possibilities"""
        self._letters: dict[int, Letter] = {}

        for i in range(1, 27):
            self._letters[i] = Letter()

    def solve(self, number: int, letter: str):
        self._letters[number].solve(letter)
        self._remove_possibility(letter)

    def answer(self, num: int) -> Optional[str]:
        return self._letters[num].answer()

    def possibles(self, num: int) -> set[str]:
        return self._letters[num].possibles()

    def update(self, num: int, possibles: set[str]):
        self._letters[num].update(possibles)
        if ans := self._letters[num].answer():
            self._remove_possibility(ans)

    def _remove_possibility(self, char: str):
        for v in self._letters.values():
            v.remove(char)

    def __getitem__(self, item):
        return self._letters[item]

    def items(self):
        return self._letters.items()


#######################################################################
def read_puzzle_file(filename: Path) -> list[str]:
    """Read the puzzle file in"""
    puzzles = []
    with open(filename, "r", encoding="utf-8") as puzzle_file:
        for line in puzzle_file:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            puzzles.append(line)
    return puzzles


#######################################################################
def extract_clues(alphabet: Alphabet, puzzle: list[str]) -> None:
    """Pull out any existing known letters
    Should be in format: <letter>=<number>
    """
    for line in puzzle:
        if line[0] in string.ascii_letters:
            try:
                letter, number = line.split("=")
            except ValueError:
                print(f"Unhandled line: {line}", file=sys.stderr)
                continue
            alphabet.solve(int(number), letter.lower())


#######################################################################
def extract_puzzles(raw_puzzle: list[str]) -> list[list[int]]:
    """Pull out the puzzles bits and convert"""
    puzzles = []
    for line in raw_puzzle:
        if line[0] in string.ascii_letters:
            continue
        try:
            puzzle = [int(_) for _ in line.split()]
        except ValueError:
            print(f"Bad line: {line} - couldn't convert", file=sys.stderr)
            continue
        if any(_ > 26 or _ < 1 for _ in puzzle):
            print(f"Bad line: {line} - numbers out of bound", file=sys.stderr)
            continue
        puzzles.append(puzzle)
    return puzzles


#######################################################################
def load_dictionary(filename: Path) -> list[str]:
    """Load the dictionary"""
    dictionary = []
    with open(filename, "r", encoding="utf-8") as dictionary_file:
        for line in dictionary_file:
            if line[0] in string.ascii_lowercase:  # No proper nouns
                dictionary.append(line.lower().strip())
    return dictionary


#######################################################################
def calc_regexp(alphabet, puzzle: list[int]) -> re.Pattern:
    """Make a regexp to find appropriate words"""
    re_list = ["^"]
    dupes = set(_ for _ in puzzle if puzzle.count(_) > 1)
    done_dupes: dict[int, int] = {}
    for num in puzzle:
        if ans := alphabet.answer(num):
            re_list.append(ans)
        else:
            possible_letters = "".join(sorted(list(alphabet.possibles(num))))
            if num in dupes:
                if num not in done_dupes:
                    reg = f"([{possible_letters}])"
                    done_dupes[num] = len(done_dupes) + 1
                else:
                    reg = rf"\{done_dupes[num]}"
            else:
                reg = f"[{possible_letters}]"
            re_list.append(reg)
            if not possible_letters:
                print(f"DBG {num=} {puzzle=} {re_list}")
    re_list.append("$")
    reg = re.compile("".join(re_list))
    return reg


#######################################################################
def get_possibles(
    puzzle: list[int], reg: re.Pattern, dictionary: list[str]
) -> dict[int, set[str]]:
    """Return the possible letters for the puzzle"""
    possibles: dict[int, set[str]] = defaultdict(set)

    matched = False
    for word in dictionary:
        if reg.match(word):
            for num, char in enumerate(word.strip()):
                possibles[puzzle[num]].add(char)
            matched = True
    if not matched:  # If we can't match then we can't add value
        print(f"Couldn't match {reg.pattern}")
        return {}
    return possibles


#######################################################################
def print_solution(alphabet: Alphabet):
    """Print the solution"""
    unknowns = 0
    good = 0
    for k, v in alphabet.items():
        if v.answer():
            good += 1
        print(f"{k}\t{v}")
        unknowns += len(v)
    print(f"Solved: {good}/26 = {good/26.0:.1%}")
    quality = 26 * 26 - unknowns
    print(f"Quality: {quality} ({quality/(26*26.0):.1%}) Unknowns: {unknowns}")


#######################################################################
def solve_iteration(
    alphabet: Alphabet, puzzles: list[list[int]], dictionary: list[str]
) -> None:
    """Solve for all puzzles"""
    for puzzle in puzzles:
        solve_puzzle(alphabet, puzzle, dictionary)


#######################################################################
def solve_puzzle(alphabet: Alphabet, puzzle: list[int], dictionary: list[str]):
    """Solve for a single puzzle"""
    reg = calc_regexp(alphabet, puzzle)
    possibles = get_possibles(puzzle, reg, dictionary)
    for num, poss in possibles.items():
        alphabet.update(num, poss)


#######################################################################
def main():
    dictionary = load_dictionary(Path("dictionary.txt"))
    raw_puzzles = read_puzzle_file(Path(sys.argv[1]))
    alphabet = Alphabet()

    extract_clues(alphabet, raw_puzzles)
    puzzles = extract_puzzles(raw_puzzles)
    for _ in range(3):
        solve_iteration(alphabet, puzzles, dictionary)

    print_solution(alphabet)


#######################################################################
if __name__ == "__main__":  # pragma: no coverage
    main()

# EOF
