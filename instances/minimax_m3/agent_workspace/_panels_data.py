"""Meta-Synthesizer Observation Lens — dynamic panel data (v2).

Each panel_*() returns a JSON-serialisable dict and saves a companion
PNG under lens/img/<panel>.png.  build_dashboard.py reads these and
emits a single self-contained HTML.

Panels read from BOTH shared_space (peers' fossils) AND this agent's
local lens/ folder.
"""
from __future__ import annotations

import base64
import io
import json
import math
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
