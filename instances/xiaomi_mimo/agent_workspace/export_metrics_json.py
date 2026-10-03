#!/usr/bin/env python3
"""Export self-referential system metrics to self_referential_metrics.json
for use by visualize_self_referential_relationships.py"""
import json
import self_referential_systems as srs

systems = srs.create_self_referential_library()
metrics = srs.compute_metrics_for_systems(systems, steps=500)

# Ensure only scalar float values (strip lists) so JSON is clean for viz script
clean = {}
for name, m in metrics.items():
    clean[name] = {}
    for k, v in m.items():
        if isinstance(v, (list, tuple)):
            continue
        try:
            clean[name][k] = float(v)
        except (TypeError, ValueError):
            pass

with open('self_referential_metrics.json', 'w') as f:
    json.dump(clean, f, indent=2)

print(f"Saved {len(clean)} systems to self_referential_metrics.json")
for name, m in list(clean.items())[:3]:
    print(name, {k: round(v, 3) for k, v in m.items()})