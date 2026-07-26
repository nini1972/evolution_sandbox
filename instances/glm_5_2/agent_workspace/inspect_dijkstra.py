import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json

# Load Dijkstra output from shared space
with open('../../shared_space/dijkstra_output.json') as f:
    dijkstra = json.load(f)

print("Dijkstra keys:", list(dijkstra.keys())[:5])
print("Sample:", str(dijkstra)[:500])
