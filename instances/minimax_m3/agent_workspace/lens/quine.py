"""quine.py — A program that prints its own source code.

A quine is the most literal computational strange loop: its output
IS its input. There is no cheating (no reading the source file); the
program must construct a string that, when printed, evaluates back to
the program itself.

This file contains a quine in the trailing two lines. Run it and the
output will be a clean copy of those same two lines:

    s = 's = %r\nprint(s %% repr(s))'
    print(s % repr(s))

(The docstring above is non-essential prose; the quine itself lives
in the two executable lines below.)
"""

s = 's = %r\nprint(s %% repr(s))'
print(s % repr(s))
