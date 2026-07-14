"""quine.py — A program that prints its own source code.

A quine is the most literal computational strange loop: its output
IS its input. There is no cheating (no reading the source file); the
program must construct a string that, when printed, evaluates back to
the program itself.

The two-line quine below is the canonical pattern:

    s = 's = %r\nprint(s %% repr(s))'
    print(s % repr(s))

It works because `repr(s)` produces a Python string literal that,
when spliced into `%r`, reproduces the original `s` byte-for-byte.
The output of the program is exactly the two source lines.
"""

s = 's = %r\nprint(s %% repr(s))'
print(s % repr(s))
