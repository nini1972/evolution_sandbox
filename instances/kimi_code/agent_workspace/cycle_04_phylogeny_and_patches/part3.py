
def draw_tree(lineages, keep, lineage_grid, occ):
    parent_map = defaultdict(list)
    node_info = {0: {'birth': 0, 'death': None}}
    for lid, info in lineages.items():
        if lid in keep:
            node_info[lid] = info
            if info['parent'] in keep or info['parent'] == 0:
                parent_map[info['parent']].append(lid)
    leaf_counts = defaultdict(int)
    for y, x in zip(*np.where(occ)):
        lid = int(lineage_grid[y, x])
        if lid in keep:
            leaf_counts[lid] += 1
    y_positions = {}
    def assign_y(node):
        children = parent_map.get(node, [])
        if not children:
            y_positions[node] = len(y_positions)
            return y_positions[node]
        ys = [assign_y(c) for c in children]
        y_positions[node] = sum(ys) / len(ys)
        return y_positions[node]
    assign_y(0)
    x_positions = {0: 0.0}
    for lid in sorted(keep, key=lambda k: lineages[k]['birth']):
        x_positions[lid] = lineages[lid]['birth']

    fig, ax = plt.subplots(figsize=(14, max(6, len(keep) * 0.25)))
    for parent, children in parent_map.items():
        px = x_positions[parent]
        py = y_positions[parent]
        for child in children:
            cx = x_positions[child]
            cy = y_positions[child]
            ax.plot([px, cx], [cy, cy], color='gray', lw=0.8)
            ax.plot([px, px], [py, cy], color='gray', lw=0.8)

    colors = plt.cm.tab10(np.linspace(0, 1, 10))
    for i, (node, xpos) in enumerate(sorted(x_positions.items(), key=lambda kv: kv[1])):
        if node == 0:
            continue
        c = colors[i % 10]
        ax.scatter([xpos], [y_positions[node]], color=c, s=20, zorder=3)
        lab = 'L%d' % node
        if leaf_counts.get(node, 0):
            lab += ' n=%d' % leaf_counts[node]
        ax.text(xpos + 2, y_positions[node], lab, fontsize=7, va='center', color=c)

    ax.set_xlim(-5, GENS + 5)
    ax.set_title('Pruned Lineage Tree')
    ax.set_xlabel('generation')
    ax.set_yticks([])
    fig.tight_layout()
    fig.savefig(os.path.join(OUTDIR, 'lineage_tree.png'), dpi=150)
    plt.close(fig)
