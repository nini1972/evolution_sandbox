#!/usr/bin/env python3
import sys
import os


if len(sys.argv) < 2:
    print("Usage: {} <script>", format(os.path.basename(__file__)))
    sys.exit(1)

script = sys.argv[1]
with open(script, "r") as f:
    content = f.read()

print(content)
