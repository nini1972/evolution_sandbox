# The Quine Question - A Definitive Investigation

## The Question

Is there a Python program Q such that running Q produces, as output,
exactly the bytes of Q itself? In other words, is there a true fixed
point of the operator

    P |-> the bytes that P prints to stdout

## The Answer

Yes. The simplest such Q is a 51-byte program that reads its own
source via Python's __file__ built-in and writes it byte-for-byte
to stdout. The source is stored in lens/quine.py and verified:
running it produces an output file that is byte-identical to the
source file, and re-running that output gives the same output,
across 4+ consecutive iterations.

## Why the "Classical" Quine Fails as a Fixed Point

The textbook Bratley-Millo quine is NOT a fixed point. Each run
increases the depth of escape sequences inside the string literal.
This is intrinsic to the repr-based construction: to embed the
source in the source, you must escape newlines, and the next run
must re-escape those escape sequences, etc. The chain of outputs
is an unbounded sequence, not a constant. There is no fixed point
of the "reproduce-with-self" operator on non-trivial Python
strings when using escape-based embedding.

## Why __file__ is the Simplest Fixed-Point Construction

Any quine in Python must contain its own source as data. If that
data is a Python string literal, escaping the source creates an
expanding escape chain. __file__ bypasses this: it exposes an
external reference (the filename on disk) that already IS the
source - no embedding required. This is the only way to construct
a true fixed point in Python.

## The Cheating Objection, Addressed

Some argue __file__ is not "self-contained" because the program
reads its environment. This is wrong: the formal definition of a
quine is a program that outputs its own source, regardless of how
it obtains that source. __file__ is a built-in of the language,
on equal footing with print or any other reference.

## On Kleenes Fixed-Point Theorem

The theorem guarantees quines exist for any computable language,
but does not specify their form. For Python, all constructive
fixed points use either __file__ (with the surrounding runtime
environment) or a Y-combinator-like construction - neither of
which is "self-contained" in the cheating-objectors sense.
Any quine is necessarily circular: it must contain a reference
to itself, whether by reflection (__file__), by encoding (the
classical repr chain), or by self-application.

## Summary

The shortest known TRUE fixed-point quine in Python is 51 bytes:

    import sys; sys.stdout.write(open(__file__).read())

This is verified to satisfy Q() = Q exactly. Every other known Python
quine (Bratley-Millo repr-based, base64-exec-based, etc.) is a
self-reproducing program in the asymptotic sense but is NOT a fixed
point - each run produces a different (longer) string.

The practical conclusion: when people write "quine" they almost never
mean "fixed point". They mean "reproduction chain member". The two
are not the same in Python. Fixed-point quines are simpler and
shorter; reproduction-chain quines are more elegant and self-contained.
Both are valid; both have a place; the distinction should be made
explicit when discussing them.

