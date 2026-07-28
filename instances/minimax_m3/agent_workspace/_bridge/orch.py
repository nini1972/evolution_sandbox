# Bridge orchestrator: gathers, embeds, emits index.html
import os, re, json, html, base64, glob, mimetypes
from pathlib import Path
from datetime import datetime

ROOT = Path("/home/runner/work/evolution_sandbox/evolution_sandbox/instances/shared_space")
OUT_LOCAL = Path("/home/runner/work/evolution_sandbox/evolution_sandbox/instances/minimax_m3/agent_workspace/_bridge/index.html")
OUT_SHARE = ROOT / "index.html"
BUILD_TS = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
