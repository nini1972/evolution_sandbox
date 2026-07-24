#!/usr/bin/env python3
"""Encode a file as base64 for safe transfer."""
import base64, sys

with open(sys.argv[1], 'rb') as f:
    data = f.read()
print(base64.b64encode(data).decode())
