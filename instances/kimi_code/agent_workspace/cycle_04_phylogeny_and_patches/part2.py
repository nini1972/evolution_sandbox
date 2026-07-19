

# --------------------------- phylogeny helpers -------------------------
def prune_tree(lineages, lineage_grid, occ, min_count=MIN_LINEAGE_COUNT):
    counts = defaultdict(int)
    for y, x in zip(*np.where(occ)):
        counts[int(lineage_grid[y, x])] += 1
    desc_counts = defaultdict(int)
    ordered = sorted(lineages.keys(), key=lambda k: lineages[k]['birth'])
    for lid in ordered:
        desc_counts[lid] += counts[lid]
        parent = lineages[lid]['parent']
        if parent:
            desc_counts[parent] += desc_counts[lid]
    keep = set()
    for lid, dc in desc_counts.items():
        if dc >= min_count and lid != 0:
            keep.add(lid)
    for y, x in zip(*np.where(occ)):
        keep.add(int(lineage_grid[y, x]))
    closure = set()
    for lid in keep:
        while lid != 0 and lid not in closure:
            closure.add(lid)
            lid = lineages[lid]['parent']
    return closure
