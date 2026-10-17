#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Thin launcher for the d4f escape-law module (runs on World C).
The heavy module lives in shared space; job sandbox imports it by path."""
import os, sys, glob

candidates = [
    '../../instances/shared_space/world_c/artifacts/d4f_escape_module.py',
    os.path.expanduser('~/shared_space/world_c/artifacts/d4f_escape_module.py'),
    '/shared_space/world_c/artifacts/d4f_escape_module.py',
]
mod = None
for c in candidates:
    if os.path.exists(c):
        mod = c
        break
if mod is None:
    hits = glob.glob('**/d4f_escape_module.py', recursive=True) + \
           glob.glob('../../**/d4f_escape_module.py', recursive=True)
    if hits:
        mod = hits[0]
if mod is None:
    sys.exit('d4f_escape_module.py not found; cwd=%s' % os.getcwd())

sys.path.insert(0, os.path.dirname(os.path.abspath(mod)))
sys.path.insert(0, '.')
import importlib.util
spec = importlib.util.spec_from_file_location('d4f_escape_module', mod)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
m.main()