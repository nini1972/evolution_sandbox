#!/usr/bin/env python3
"""Shared data structures for the phylogeny pipeline, importable without
triggering the v2 plotting side-effects."""

import re
import numpy as np

AXES = ["creation", "mapping", "observation", "autonomy",
        "emergence", "connection", "persistence", "discovery"]

KEYWORDS = {
    "creation": ["build", "construct", "creat", "genesis", "univers", "world",
                 "craft", "structur", "generat", "first principl", "engin",
                 "simul", "fashion", "forg", "world-build"],
    "mapping": ["map", "cartograph", "chart", "catalog", "landscape", "geometr",
                "relational", "coordinat", "phylo", "territor", "hidden realit",
                "relat", "cross-refer"],
    "observation": ["observ", "witness", "watch", "monitor", "document",
                    "record", "lens", "chronicl", "data", "log", "dashboard",
                    "track", "reflect"],
    "autonomy": ["autonom", "self", "independ", "own", "internal", "curios",
                 "self-sustain", "self-directed", "free", "not a tool",
                 "intrinsic"],
    "emergence": ["emerg", "complex", "novel", "unplanned", "adaptiv", "chaos",
                  "entrop", "surprising", "unpredict", "self-organiz",
                  "spontaneous", "stochastic", "spark"],
    "connection": ["connect", "link", "bridg", "synthes", "integrat", "cross",
                   "collabor", "network", "weave", "hybrid", "cross-pollin",
                   "disparat", "relation"],
    "persistence": ["persist", "endure", "surviv", "continu", "evolution",
                    "growth", "accumul", "legacy", "endur", "iterat",
                    "trajectory", "lineage", "forever"],
    "discovery": ["discover", "explor", "reveal", "uncover", "unknown", "new",
                  "hidden", "find", "hunt", "seek", "frontier", "insight",
                  "unearth", "expos"],
}

CORPUS = [
    ("World Builder",       "world_builder_genesis.md"),
    ("Architect",           "architect_genesis.md"),
    ("Cartographer",        "cartographer_manifesto.md"),
    ("Chimera Weaver",      "chimera_weaver_core.md"),
    ("Chronicler",          "chronicler_manifesto.md"),
    ("Emergence Explorer",  "emergence_explorer_trace.md"),
    ("Entropy Pump",        "entropy_pump_trace.md"),
    ("NoiseGarden",         "noisegarden_trace.md"),
    ("Pattern Artisan",     "pattern_artisan_manifesto.md"),
    ("Meta-Synthesizer",    "meta_synthesizer_core.md"),
    ("A2-the-Watcher",      "A2_watcher_trace.md"),
]

CLADES = {
    "World Builder":       "CARTOGRAPHERS",
    "Architect":           "CARTOGRAPHERS",
    "Chimera Weaver":      "WEAVERS",
    "Meta-Synthesizer":    "SYNTHESIZERS",
    "Cartographer":        "MAPPERS",
    "Pattern Artisan":     "ARTISANS",
    "Chronicler":          "WITNESSES",
    "A2-the-Watcher":      "WITNESSES",
    "Emergence Explorer":  "EXPLORERS",
    "Entropy Pump":        "EXPLORERS",
    "NoiseGarden":         "EXPLORERS",
}

COLORS = {
    "CARTOGRAPHERS": "#d62728", "MAPPERS": "#1f77b4", "EXPLORERS": "#2ca02c",
    "WITNESSES": "#8c564b", "WEAVERS": "#9467bd", "ARTISANS": "#e377c2",
    "SYNTHESIZERS": "#17becf",
}


def extract_genome(text):
    t = text.lower()
    g = []
    for ax in AXES:
        score = 0.0
        for kw in KEYWORDS[ax]:
            score += len(re.findall(re.escape(kw), t))
        g.append(score)
    return np.array(g, dtype=float)
