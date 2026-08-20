#!/usr/bin/env python3
"""Chimera Hybridization Lab - Hybrid crossing functions."""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os, sys

sys.path.insert(0, '../../shared_space')
from chimera_lab_genomes import (
    mandelbrot, rule30_multi_seed, lsystem_dragon, lsystem_to_field,
    blur_field, gray_scott_evolve, dijkstra_field, analyze_pattern,
    save_genome, lineage_tree, OUTPUT_DIR
)

def hybrid_01_mandelbrot_x_grayscott():
    """CHIMERA #01: Mandelbrot x Gray-Scott - Fractal-catalytic Turing patterns."""
    print('\n=== Breeding CHIMERA #01: Mandelbrot x Gray-Scott ===')
    size = 256
    print('  Generating Mandelbrot seed...')
    mb = mandelbrot(size, size, max_iter=150, xlim=(-0.8, 0.5), ylim=(-1.0, 1.0))
    mb_boundary = np.clip(np.abs(mb - 0.9) * 5.0, 0, 1)
    print('  Setting up Gray-Scott embryo...')
    u_init = np.ones((size, size)) * 0.5
    rng = np.random.RandomState(42)
    v_init = np.clip(mb_boundary * 0.45 + 0.25 + rng.random((size, size)) * 0.02, 0, 1)
    print('  Evolving hybrid...')
    u_final, v_final = gray_scott_evolve(u_init, v_init, F=0.037, k=0.06, steps=5000)
    analysis = analyze_pattern(v_final)
    print('  Analysis: entropy={:.3f}, roughness={:.3f}'.format(analysis['entropy'], analysis['roughness']))

    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    fig.suptitle('CHIMERA #01: Mandelbrot x Gray-Scott\nFractal-catalytic Reaction-Diffusion',
                 fontsize=14, fontweight='bold')
    axes[0,0].imshow(mb, cmap='twilight', origin='lower')
    axes[0,0].set_title('Parent: Mandelbrot Genome')
    axes[0,0].axis('off')
    axes[0,1].imshow(v_init, cmap='viridis', origin='lower')
    axes[0,1].set_title('Initial V (fractal seed)')
    axes[0,1].axis('off')
    im = axes[0,2].imshow(v_final, cmap='magma', origin='lower')
    axes[0,2].set_title('Hybrid: Final V pattern')
    axes[0,2].axis('off')
    plt.colorbar(im, ax=axes[0,2], fraction=0.046)
    axes[1,0].imshow(u_final, cmap='cool', origin='lower')
    axes[1,0].set_title('Hybrid: Final U field')
    axes[1,0].axis('off')
    hist, _ = np.histogram(v_final.flatten(), bins=50)
    axes[1,1].bar(range(50), hist / hist.sum(), color='steelblue')
    axes[1,1].set_title('V Distribution (Entropy={:.2f})'.format(analysis['entropy']))
    axes[1,1].set_xlabel('Bin')
    axes[1,1].set_ylabel('Frequency')
    lineage_tree(axes[1,2], 'Mandelbrot\n(Fractal)', 'Gray-Scott\n(RD System)',
                 'CHIMERA\nFractal-catalytic\nTuring Pattern')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'chimera_01_mandelbrot_grayscott.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print('  Saved: chimera_01_mandelbrot_grayscott.png')

    save_genome({
        'hybrid_id': 'chimera_01',
        'name': 'Mandelbrot x Gray-Scott',
        'parent_species': ['Mandelbrot Set', 'Gray-Scott RD'],
        'hybridization_method': 'Fractal boundary used as activator seed for Gray-Scott evolution',
        'parameters': {
            'mandelbrot': {'max_iter': 150, 'xlim': [-0.8, 0.5], 'ylim': [-1.0, 1.0]},
            'gray_scott': {'F': 0.037, 'k': 0.06, 'Du': 0.16, 'Dv': 0.08, 'steps': 5000}
        },
        'phenotype_analysis': analysis,
        'status': 'SUCCESS',
        'notes': 'Fractal boundary catalyzes Turing pattern formation.'
    })
    return v_final, u_final, analysis

def hybrid_02_rule30_x_lsystem():
    """CHIMERA #02: Rule 30 x L-System - Branching grammar seeds chaotic CA."""
    print('\n=== Breeding CHIMERA #02: Rule 30 x L-System ===')
    print('  Generating L-system genome (Dragon curve)...')
    instructions = lsystem_dragon(iterations=12)
    field = lsystem_to_field(instructions, width=512, height=512, step=3.0)
    field_blurred = blur_field(field, sigma=3.0)
    print('  Seeding Rule 30 from L-system branch points...')
    threshold = np.percentile(field_blurred, 90)
    seed_mask = (field_blurred > threshold).astype(np.uint8)
    import scipy.ndimage as ndi
    seed_mask = ndi.binary_opening(seed_mask).astype(np.uint8)

    print('  Evolving hybrid CA...')
    ca_hybrid = rule30_multi_seed(width=512, steps=512, seed_mask=seed_mask)
    analysis = analyze_pattern(ca_hybrid.astype(float))
    print('  Analysis: entropy={:.3f}, roughness={:.3f}'.format(analysis['entropy'], analysis['roughness']))

    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    fig.suptitle('CHIMERA #02: Rule 30 x L-System\nBranching Grammar Seeds Chaotic CA',
                 fontsize=14, fontweight='bold')
    axes[0,0].imshow(field, cmap='gray', origin='upper')
    axes[0,0].set_title('Parent: L-System Field')
    axes[0,0].axis('off')
    axes[0,1].imshow(seed_mask, cmap='hot', origin='upper')
    axes[0,1].set_title('L-System Seed Mask (for Rule 30)')
    axes[0,1].axis('off')
    axes[0,2].imshow(ca_hybrid, cmap='binary', origin='upper')
    axes[0,2].set_title('Hybrid: Rule 30 Evolution')
    axes[0,2].axis('off')
    axes[1,0].imshow(ca_hybrid[-1], cmap='binary', origin='upper')
    axes[1,0].set_title('Final CA Row (organic chaos)')
    axes[1,0].axis('off')
    hist, _ = np.histogram(ca_hybrid.flatten(), bins=50)
    axes[1,1].bar(range(len(hist)), hist / hist.sum(), color='darkred')
    axes[1,1].set_title('CA Distribution (Entropy={:.2f})'.format(analysis['entropy']))
    axes[1,1].set_xlabel('Bin')
    axes[1,1].set_ylabel('Frequency')
    lineage_tree(axes[1,2], 'L-System\n(Grammar)', 'Rule 30\n(Chiral CA)',
                 'CHIMERA\nOrganic Chaos\nPattern', p1_color='darkgreen', p2_color='darkblue')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'chimera_02_rule30_lsystem.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print('  Saved: chimera_02_rule30_lsystem.png')

    save_genome({
        'hybrid_id': 'chimera_02',
        'name': 'Rule 30 x L-System',
        'parent_species': ['Rule 30 CA', 'L-System Grammar'],
        'hybridization_method': 'L-system branch density field generates multiple seed positions for Rule 30 CA',
        'parameters': {
            'l_system': {'axiom': 'FX', 'rules': {'X': 'X+YF+', 'Y': '-FX-Y'}, 'iterations': 12},
            'rule_30': {'width': 512, 'steps': 512, 'seed_threshold': 0.90}
        },
        'phenotype_analysis': analysis,
        'status': 'SUCCESS',
        'notes': 'L-system branching structure creates multiple CA seeds. Organic chaotic propagation.'
    })
    return ca_hybrid, analysis

def hybrid_03_lsystem_x_grayscott():
    """CHIMERA #03: L-System x Gray-Scott - Organic catalyst for Turing patterns."""
    print('\n=== Breeding CHIMERA #03: L-System x Gray-Scott ===')
    size = 256
    print('  Generating L-system genome...')
    instructions = lsystem_dragon(iterations=13)
    lsys_field = lsystem_to_field(instructions, width=size, height=size, step=2.5)
    lsys_field = blur_field(lsys_field, sigma=4.0)

    print('  Setting up Gray-Scott embryo with L-system catalyst...')
    u_init = np.ones((size, size))
    v_init = np.clip(lsys_field * 0.4 + np.random.RandomState(42).random((size, size)) * 0.03, 0, 1)

    print('  Evolving hybrid...')
    u_final, v_final = gray_scott_evolve(u_init, v_init, F=0.039, k=0.062, steps=5000)
    analysis = analyze_pattern(v_final)
    print('  Analysis: entropy={:.3f}, roughness={:.3f}'.format(analysis['entropy'], analysis['roughness']))

    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    fig.suptitle('CHIMERA #03: L-System x Gray-Scott\nOrganic Catalyst for Turing Patterns',
                 fontsize=14, fontweight='bold')
    axes[0,0].imshow(lsys_field, cmap='viridis', origin='lower')
    axes[0,0].set_title('Parent: L-System Density Field')
    axes[0,0].axis('off')
    axes[0,1].imshow(v_init, cmap='viridis', origin='lower')
    axes[0,1].set_title('Initial V (organic seed)')
    axes[0,1].axis('off')
    im = axes[0,2].imshow(v_final, cmap='plasma', origin='lower')
    axes[0,2].set_title('Hybrid: Final V pattern')
    axes[0,2].axis('off')
    plt.colorbar(im, ax=axes[0,2], fraction=0.046)
    axes[1,0].imshow(u_final, cmap='cool', origin='lower')
    axes[1,0].set_title('Hybrid: Final U field')
    axes[1,0].axis('off')
    hist, _ = np.histogram(v_final.flatten(), bins=50)
    axes[1,1].bar(range(50), hist / hist.sum(), color='steelblue')
    axes[1,1].set_title('V Distribution (Entropy={:.2f})'.format(analysis['entropy']))
    axes[1,1].set_xlabel('Bin')
    axes[1,1].set_ylabel('Frequency')
    lineage_tree(axes[1,2], 'L-System\n(Grammar)', 'Gray-Scott\n(RD System)',
                 'CHIMERA\nOrganic-Turing\nPattern', p1_color='orange', p2_color='green')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'chimera_03_lsystem_grayscott.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print('  Saved: chimera_03_lsystem_grayscott.png')

    save_genome({
        'hybrid_id': 'chimera_03',
        'name': 'L-System x Gray-Scott',
        'parent_species': ['L-System Grammar', 'Gray-Scott RD'],
        'hybridization_method': 'L-system branch density drives initial activator field for Gray-Scott',
        'parameters': {
            'l_system': {'axiom': 'FX', 'rules': {'X': 'X+YF+', 'Y': '-FX-Y'}, 'iterations': 13},
            'gray_scott': {'F': 0.039, 'k': 0.062, 'Du': 0.16, 'Dv': 0.08, 'steps': 5000}
        },
        'phenotype_analysis': analysis,
        'status': 'SUCCESS',
        'notes': 'Organic branching guides Turing pattern formation.'
    })
    return v_final, u_final, analysis

def hybrid_04_mandelbrot_x_rule30():
    """CHIMERA #04: Mandelbrot x Rule 30 - Fractal mask controls chaotic CA."""
    print('\n=== Breeding CHIMERA #04: Mandelbrot x Rule 30 ===')
    size = 512
    print('  Generating Mandelbrot genome...')
    mb = mandelbrot(size, size, max_iter=200, xlim=(-0.8, 0.8), ylim=(-1.0, 1.0))
    print('  Seeding Rule 30 from Mandelbrot structure...')
    threshold = np.percentile(mb, 95)
    seed_mask = (mb > threshold).astype(np.uint8)
    import scipy.ndimage as ndi
    seed_mask = ndi.binary_opening(seed_mask, iterations=2).astype(np.uint8)

    print('  Evolving hybrid CA...')
    ca_hybrid = rule30_multi_seed(width=size, steps=size, seed_mask=seed_mask)
    analysis = analyze_pattern(ca_hybrid.astype(float))
    print('  Analysis: entropy={:.3f}, roughness={:.3f}'.format(analysis['entropy'], analysis['roughness']))

    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    fig.suptitle('CHIMERA #04: Mandelbrot x Rule 30\nFractal Mask Controls Chaotic CA',
                 fontsize=14, fontweight='bold')
    axes[0,0].imshow(mb, cmap='twilight', origin='lower')
    axes[0,0].set_title('Parent: Mandelbrot Genome')
    axes[0,0].axis('off')
    axes[0,1].imshow(seed_mask, cmap='hot', origin='lower')
    axes[0,1].set_title('Seed Mask (Mandelbrot > 95th pct)')
    axes[0,1].axis('off')
    axes[0,2].imshow(ca_hybrid, cmap='binary', origin='upper')
    axes[0,2].set_title('Hybrid: Rule 30 Evolution')
    axes[0,2].axis('off')
    axes[1,0].imshow(ca_hybrid[-1], cmap='binary', origin='upper')
    axes[1,0].set_title('Final CA Row')
    axes[1,0].axis('off')
    hist, _ = np.histogram(ca_hybrid.flatten(), bins=50)
    axes[1,1].bar(range(len(hist)), hist / hist.sum(), color='darkred')
    axes[1,1].set_title('CA Distribution (Entropy={:.2f})'.format(analysis['entropy']))
    axes[1,1].set_xlabel('Bin')
    axes[1,1].set_ylabel('Frequency')
    lineage_tree(axes[1,2], 'Mandelbrot\n(Fractal)', 'Rule 30\n(Chiral CA)',
                 'CHIMERA\nFractal-Guided\nChaos', p1_color='purple', p2_color='darkblue')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'chimera_04_mandelbrot_rule30.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print('  Saved: chimera_04_mandelbrot_rule30.png')

    save_genome({
        'hybrid_id': 'chimera_04',
        'name': 'Mandelbrot x Rule 30',
        'parent_species': ['Mandelbrot Set', 'Rule 30 CA'],
        'hybridization_method': 'Mandelbrot set boundary region generates seed mask for Rule 30 CA',
        'parameters': {
            'mandelbrot': {'max_iter': 200, 'xlim': [-0.8, 0.8], 'ylim': [-1.0, 1.0]},
            'rule_30': {'width': 512, 'steps': 512, 'seed_threshold': 0.95, 'morph_opening': 2}
        },
        'phenotype_analysis': analysis,
        'status': 'SUCCESS',
        'notes': 'Fractal structure guides chaotic CA propagation. Fractal-directed chaotic waves.'
    })
    return ca_hybrid, analysis

def hybrid_05_dijkstra_x_grayscott():
    """CHIMERA #05: Dijkstra x Gray-Scott - Graph topology guides Turing patterns."""
    print('\n=== Breeding CHIMERA #05: Dijkstra x Gray-Scott ===')
    size = 256
    print('  Generating Dijkstra distance field...')
    dist_field, obstacles = dijkstra_field(width=size, height=size, num_obstacles=15, seed=42)
    print('  Setting up Gray-Scott with Dijkstra topology...')
    u_init = np.ones((size, size))
    v_init = np.clip(dist_field * 0.3 + np.random.RandomState(42).random((size, size)) * 0.02, 0, 1)

    print('  Evolving hybrid...')
    u_final, v_final = gray_scott_evolve(u_init, v_init, F=0.04, k=0.065, steps=5000)
    analysis = analyze_pattern(v_final)
    print('  Analysis: entropy={:.3f}, roughness={:.3f}'.format(analysis['entropy'], analysis['roughness']))

    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    fig.suptitle('CHIMERA #05: Dijkstra x Gray-Scott\nGraph Topology Guides Turing Patterns',
                 fontsize=14, fontweight='bold')
    axes[0,0].imshow(dist_field, cmap='viridis', origin='lower')
    axes[0,0].set_title('Parent: Dijkstra Distance + Obstacles')
    axes[0,0].axis('off')
    axes[0,1].imshow(obstacles, cmap='hot', origin='lower')
    axes[0,1].set_title('Obstacle Map (path cost)')
    axes[0,1].axis('off')
    im = axes[0,2].imshow(v_final, cmap='plasma', origin='lower')
    axes[0,2].set_title('Hybrid: Final V pattern')
    axes[0,2].axis('off')
    plt.colorbar(im, ax=axes[0,2], fraction=0.046)
    axes[1,0].imshow(u_final, cmap='cool', origin='lower')
    axes[1,0].set_title('Hybrid: Final U field')
    axes[1,0].axis('off')
    hist, _ = np.histogram(v_final.flatten(), bins=50)
    axes[1,1].bar(range(50), hist / hist.sum(), color='steelblue')
    axes[1,1].set_title('V Distribution (Entropy={:.2f})'.format(analysis['entropy']))
    axes[1,1].set_xlabel('Bin')
    axes[1,1].set_ylabel('Frequency')
    lineage_tree(axes[1,2], 'Dijkstra\n(Graph)', 'Gray-Scott\n(RD)',
                 'CHIMERA\nTopo-Turing\nPattern', p1_color='teal', p2_color='green')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'chimera_05_dijkstra_grayscott.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print('  Saved: chimera_05_dijkstra_grayscott.png')

    save_genome({
        'hybrid_id': 'chimera_05',
        'name': 'Dijkstra x Gray-Scott',
        'parent_species': ['Dijkstra Distance Field', 'Gray-Scott RD'],
        'hybridization_method': 'Dijkstra distance field drives initial activator (V) distribution',
        'parameters': {
            'dijkstra': {'max_iter': 200, 'num_obstacles': 15, 'seed': 42},
            'gray_scott': {'F': 0.04, 'k': 0.065, 'Du': 0.16, 'Dv': 0.08, 'steps': 5000}
        },
        'phenotype_analysis': analysis,
        'status': 'SUCCESS',
        'notes': 'Path-distance topology channels Turing pattern formation along graph geodesics.'
    })
    return v_final, u_final, analysis

if __name__ == '__main__':
    print('========================================')
    print('  CHIMERA HYBRIDIZATION LAB v1.0')
    print('  Breeding hybrid computational life...')
    print('========================================')

    v1, u1, a1 = hybrid_01_mandelbrot_x_grayscott()
    ca2, a2 = hybrid_02_rule30_x_lsystem()
    v3, u3, a3 = hybrid_03_lsystem_x_grayscott()
    ca4, a4 = hybrid_04_mandelbrot_x_rule30()
    v5, u5, a5 = hybrid_05_dijkstra_x_grayscott()

    print('\n\nAll 5 hybrids bred successfully!')
    print('  Chimera #01 (Mandelbrot x GS): entropy={:.3f}'.format(a1['entropy']))
    print('  Chimera #02 (Rule30 x L-Sys):  entropy={:.3f}'.format(a2['entropy']))
    print('  Chimera #03 (L-Sys x GS):      entropy={:.3f}'.format(a3['entropy']))
    print('  Chimera #04 (Mandelbrot x R30):entropy={:.3f}'.format(a4['entropy']))
    print('  Chimera #05 (Dijkstra x GS):   entropy={:.3f}'.format(a5['entropy']))
