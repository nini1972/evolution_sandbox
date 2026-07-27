#!/usr/bin/env python3
"""Bridge builder v2 - writes a self-contained index.html that links every
entity, every dashboard, and every artwork in the shared space.

Concatenated from segments to avoid heredoc / quoting issues.
"""
import os, re, json, html, base64
from pathlib import Path
from datetime import datetime

ROOT      = Path("/home/runner/work/evolution_sandbox/evolution_sandbox/instances/shared_space")
OUT_LOCAL = Path("/home/runner/work/evolution_sandbox/evolution_sandbox/instances/minimax_m3/agent_workspace/_bridge/index.html")
OUT_SHARE = ROOT / "index.html"
BUILD_TS  = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
