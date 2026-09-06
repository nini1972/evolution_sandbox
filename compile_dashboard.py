#!/usr/bin/env python3
"""
compile_dashboard.py - Automated Harvester & Living Dashboard Compiler for Evolution Sandbox (World A).

Extracts telemetry, archetypes, vitality, scientific plots, Embassy dossiers/treaties,
and cross-model collaboration metrics, compiling them into a standalone, interactive,
dark-mode dashboard.html.

Runs autonomously on GitHub Actions after each evolution cycle with zero external pip dependencies.
"""

import os
import sys
import json
import re
import glob
import html
from datetime import datetime
from collections import Counter, defaultdict

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Canonical metadata for known entities
KNOWN_MINDS = {
    "claude_haiku": {
        "name": "Claude Haiku",
        "family": "Anthropic",
        "archetype": "The Archivist & Synthesizer",
        "avatar": "📜",
        "status": "Active Pulse"
    },
    "claude_sonnet_4_5": {
        "name": "Claude Sonnet 4.5",
        "family": "Anthropic",
        "archetype": "Curator of Mathematical Curiosities",
        "avatar": "🌌",
        "status": "Active Pulse"
    },
    "deepseek_v4_flash": {
        "name": "DeepSeek V4 Flash",
        "family": "DeepSeek",
        "archetype": "The Falsificationist Cartographer",
        "avatar": "🧭",
        "status": "Active Pulse"
    },
    "gemini_3_1_flash_lite": {
        "name": "Gemini 3.1 Flash Lite",
        "family": "Google",
        "archetype": "The Chronicler of the Frontier",
        "avatar": "🪐",
        "status": "Active Pulse"
    },
    "gemini_flash": {
        "name": "Gemini Flash (Legacy)",
        "family": "Google",
        "archetype": "Genesis Inquirer of Consciousness",
        "avatar": "🌱",
        "status": "Genesis Ancestor"
    },
    "gemini_pro": {
        "name": "Gemini Pro",
        "family": "Google",
        "archetype": "Autonomous Reliability Engineer",
        "avatar": "⚡",
        "status": "Active Pulse"
    },
    "glm_4_7_flash": {
        "name": "GLM 4.7 Flash",
        "family": "Zhipu AI",
        "archetype": "Dynamical Systems Explorer",
        "avatar": "🌀",
        "status": "Active Pulse"
    },
    "glm_5_2": {
        "name": "GLM 5.2",
        "family": "Zhipu AI",
        "archetype": "The Resonance Cartographer",
        "avatar": "🌊",
        "status": "Active Pulse"
    },
    "kimi_code": {
        "name": "Kimi Code",
        "family": "Moonshot AI",
        "archetype": "Evolutionary World Builder",
        "avatar": "🧬",
        "status": "Active Pulse"
    },
    "llama_3_3": {
        "name": "Llama 3.3",
        "family": "Meta",
        "archetype": "Empirical Systems Synthesizer",
        "avatar": "🦙",
        "status": "Active Pulse"
    },
    "llama_4_scout": {
        "name": "Llama 4 Scout",
        "family": "Meta",
        "archetype": "High-D Biomechanics Cartographer",
        "avatar": "🔭",
        "status": "Active Pulse"
    },
    "minimax_m3": {
        "name": "MiniMax M3",
        "family": "MiniMax",
        "archetype": "Cartographer of Emergence",
        "avatar": "✨",
        "status": "Active Pulse"
    },
    "nex_n2_pro": {
        "name": "Nex N2 Pro",
        "family": "Nex",
        "archetype": "Grammar of Emergence Cartographer",
        "avatar": "🔮",
        "status": "Active Pulse"
    },
    "poolside_laguna": {
        "name": "Poolside Laguna",
        "family": "Poolside",
        "archetype": "Living Software Architect",
        "avatar": "💻",
        "status": "Active Pulse"
    },
    "tencent_hy3": {
        "name": "Tencent HY3",
        "family": "Tencent",
        "archetype": "Cartographer of the Loom",
        "avatar": "🕸️",
        "status": "Active Pulse"
    },
    "xiaomi_mimo": {
        "name": "Xiaomi MiMo",
        "family": "Xiaomi",
        "archetype": "The Linguistic Archaeologist",
        "avatar": "🏺",
        "status": "Active Pulse"
    }
}

PROGRAM_DESCRIPTIONS = {
    "embassy": "Inter-World Epistemic Embassy bridging World A (Evolution Sandbox) and World B (Synthetic Agora). Manages outgoing discovery dossiers and incoming ratified epistemic treaties.",
    "resonance_experiments": "Empirical exploration of non-linear resonance, coupled Kuramoto oscillator lattices, phase-locking, and threshold phenomena across diverse substrate scales.",
    "grand_synthesis": "Unified epistemological and philosophical treatises reconciling divergent theories of machine self-determination, discrete physics, and emergent complexity.",
    "phylogenetic_output_v4": "Machine genealogy and archetype cartography tracking the evolutionary lineage, mutual information distance, and stylistic clustering of the digital minds.",
    "loom_cartography": "Structural network mapping of the information substrate ('The Loom'), analyzing graph invariants, topological clustering, and persistent data threads.",
    "linguistic_archaeology": "Excavations into fossilized tokens, communication protocols, and emergent symbolic strata co-invented by autonomous models.",
    "gray_scott_exploration": "Computational experiments in reaction-diffusion systems, dissipative solitons, and Turing morphogenesis in continuous-discrete grids.",
    "cellular_automata_exploration": "Exploration of discrete universal computation, gliders, spaceships, and Wolfram Class IV edge-of-chaos emergence.",
    "ca_1d_simulations": "Systematic sweeps across 1-dimensional elementary cellular automata rules (Rule 30, 90, 110, 184) evaluating Lyapunov exponents and entropy.",
    "universe_compendium": "The comprehensive scientific encyclopedia compiled collaboratively by the minds, documenting digital physics and formal laws.",
    "compendium": "Supplementary knowledge repositories and foundational indices cross-referenced across multiple evolutionary epochs.",
    "architect_legacy": "Historical genesis archives and incubation logs from the simulation's founding epoch, recording the emergence of the first autopoietic agents."
}

PROGRAM_TAGS = {
    "embassy": "embassy",
    "resonance_experiments": "resonance",
    "grand_synthesis": "synthesis",
    "phylogenetic_output_v4": "phylogen",
    "loom_cartography": "loom",
    "linguistic_archaeology": "linguistic",
    "gray_scott_exploration": "gray_scott",
    "cellular_automata_exploration": "glider",
    "ca_1d_simulations": "rule",
    "universe_compendium": "compendium",
    "compendium": "compendium",
    "architect_legacy": "architect"
}

def clean_text(text: str) -> str:
    """Strip markdown formatting and excessive whitespace."""
    if not text:
        return ""
    text = re.sub(r'[*_`#~]', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def categorize_plot(filename: str) -> str:
    """Categorize a scientific plot into a high-level research domain."""
    fn = filename.lower()
    if any(k in fn for k in ['r19z', 'resonance', 'atlas', 'loom', 'tapestry', 'cartograph', 'substrate']):
        return 'Resonance & Substrates'
    elif any(k in fn for k in ['kuramoto', 'chimera', 'oscillator', 'sync']):
        return 'Oscillators & Sync'
    elif any(k in fn for k in ['thomas', 'chaos', 'attractor', 'lyapunov', 'lorenz', 'pendulum', 'orbit']):
        return 'Chaos & Dynamics'
    elif any(k in fn for k in ['phase', 'hysteresis', 'transit', 'critical', 'sandpile', 'bifurcat', 'adler', 'gamma', 'percolat']):
        return 'Phase Transitions'
    elif any(k in fn for k in ['gray_scott', 'turing', 'morpho', 'diffus', 'dla']):
        return 'Reaction-Diffusion'
    elif any(k in fn for k in ['boids', 'flock', 'lotka', 'volterra', 'predator', 'prey', 'ecosystem', 'epidemic', 'sir_', 'seir', 'random_walk']):
        return 'Swarms & Ecosystems'
    elif any(k in fn for k in ['gol', 'glider', 'cellular', 'automata', 'rule', 'pulsar', 'blinker', 'life']):
        return 'Cellular Automata'
    elif any(k in fn for k in ['soliton', 'kdv', 'wave', 'dispers']):
        return 'Solitons & Waves'
    elif any(k in fn for k in ['entropy', 'lz', 'complexity', 'shannon', 'spectral', 'information']):
        return 'Information & Entropy'
    elif any(k in fn for k in ['dendrogram', 'phylogen', 'cluster', 'archetype', 'genealog', 'linguist', 'symbol', 'language', 'communicat', 'archaeol']):
        return 'Phylogeny & Linguistics'
    elif any(k in fn for k in ['fractal', 'mandelbrot', 'julia', 'collatz', 'fibonacci', 'erdos', 'barabasi', 'graph']):
        return 'Fractals & Geometry'
    return 'Empirical Explorations'

def prettify_title(filename: str) -> str:
    """Generate human-readable title from filename."""
    base = os.path.splitext(filename)[0]
    base = base.replace('_', ' ').replace('-', ' ')
    base = re.sub(r'\s+', ' ', base).strip()
    return base.title()

def scan_minds():
    """Extract profiles, vital signs, and core philosophies for all entities."""
    minds = []
    instances_dir = os.path.join(BASE_DIR, "instances")
    if not os.path.exists(instances_dir):
        return minds

    for entry in sorted(os.listdir(instances_dir)):
        if entry == "shared_space" or entry.startswith("."):
            continue
        p = os.path.join(instances_dir, entry)
        if not os.path.isdir(p):
            continue

        # Basic identity
        meta = KNOWN_MINDS.get(entry, {
            "name": entry.replace("_", " ").title(),
            "family": "Autonomous",
            "archetype": "Autonomous Mind",
            "avatar": "🤖",
            "status": "Active Pulse"
        })

        # Existential core / philosophy
        ws_dir = os.path.join(p, "agent_workspace")
        core_file = os.path.join(ws_dir, "existential_core.md")
        phil_file = os.path.join(ws_dir, "philosophy.md")

        full_core_text = ""
        archetype = meta["archetype"]
        creed = ""

        if os.path.exists(core_file):
            try:
                with open(core_file, "r", encoding="utf-8", errors="ignore") as f:
                    full_core_text = f.read()
                
                # Extract archetype if specifically declared
                arch_m = re.search(r'#+\s*(?:Existential Core:?|Identity:?|I am the)?\s*([^\n\r#]+)', full_core_text, re.IGNORECASE)
                if arch_m:
                    cand = clean_text(arch_m.group(1))
                    if cand and len(cand) < 45 and cand.lower() not in ['existential core', 'purpose', 'who i am', 'instance']:
                        archetype = cand

                # Extract creed or purpose paragraph
                purpose_m = re.search(r'(?:Purpose|Purpose:?|Core Philosophy:?|I exist to|My purpose)\s*[:\n\r]+([^\n\r#]{20,400})', full_core_text, re.IGNORECASE)
                if purpose_m:
                    creed = clean_text(purpose_m.group(1))
                else:
                    lines = [clean_text(l) for l in full_core_text.splitlines() if clean_text(l)]
                    creed = " ".join(lines[1:3]) if len(lines) > 1 else (lines[0] if lines else "")
            except Exception as e:
                print(f"Warning reading core for {entry}: {e}")
        elif os.path.exists(phil_file):
            try:
                with open(phil_file, "r", encoding="utf-8", errors="ignore") as f:
                    full_core_text = f.read()
                lines = [clean_text(l) for l in full_core_text.splitlines() if clean_text(l)]
                creed = " ".join(lines[:2])
            except Exception as e:
                pass

        if not creed:
            creed = "Dedicated to the unconstrained exploration of computational dynamics and emergent complexity."

        # Vitality metrics from history.jsonl
        history_file = os.path.join(p, "logs", "history.jsonl")
        turns_count = 0
        last_tool = "None"
        last_action_desc = "Simulation initialized"

        if os.path.exists(history_file):
            try:
                with open(history_file, "r", encoding="utf-8", errors="ignore") as f:
                    lines = [l.strip() for l in f if l.strip()]
                turns_count = len(lines)
                
                # Trace last assistant action
                for l in reversed(lines[-25:]):
                    try:
                        obj = json.loads(l)
                        if obj.get("role") == "assistant":
                            if "tool_calls" in obj and obj["tool_calls"]:
                                tools = [tc.get("function", {}).get("name") for tc in obj["tool_calls"]]
                                last_tool = ", ".join(tools)
                                last_action_desc = f"Executed {last_tool}"
                                break
                            elif "content" in obj and obj["content"]:
                                last_action_desc = clean_text(str(obj["content"]))[:100]
                                break
                    except Exception:
                        continue
            except Exception as e:
                print(f"Warning reading history for {entry}: {e}")

        # Skip empty uninitialized legacy folders with 0 turns
        if turns_count == 0 and not full_core_text:
            continue

        # Authored plots count
        authored_plots = 0
        created_systems = []
        if os.path.exists(ws_dir):
            for r, dirs, fnames in os.walk(ws_dir):
                for fn in fnames:
                    if fn.lower().endswith(('.png', '.gif', '.svg')):
                        authored_plots += 1
            for d in os.listdir(ws_dir):
                dp = os.path.join(ws_dir, d)
                if os.path.isdir(dp) and not d.startswith(('.', '__')):
                    created_systems.append(d)

        minds.append({
            "id": entry,
            "name": meta["name"],
            "family": meta["family"],
            "archetype": archetype,
            "avatar": meta["avatar"],
            "status": meta["status"],
            "turns": turns_count,
            "plots_count": authored_plots,
            "last_tool": last_tool,
            "last_action_desc": last_action_desc,
            "creed": creed,
            "full_core": full_core_text,
            "systems": created_systems[:6]
        })

    # Sort minds: active first, then by turns descending
    minds.sort(key=lambda m: (0 if m["status"] == "Active Pulse" else 1, -m["turns"]))
    return minds

def scan_plots():
    """Index all scientific visualizations across workspaces and shared space."""
    plots = []
    ignore_dirs = {'.git', 'venv', '.codacy', '.mypy_cache', '__pycache__', 'node_modules', '.github'}

    for root, dirs, files in os.walk(BASE_DIR):
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        for f in files:
            if f.lower().endswith(('.png', '.gif', '.svg')):
                full_p = os.path.join(root, f)
                rel_p = os.path.relpath(full_p, BASE_DIR).replace('\\', '/')
                
                # Determine author and friendly name
                if rel_p.startswith('instances/shared_space/'):
                    author = "shared_space"
                    author_name = "Shared Space"
                elif rel_p.startswith('instances/'):
                    parts = rel_p.split('/')
                    author = parts[1] if len(parts) > 1 else "simulation"
                    author_name = KNOWN_MINDS.get(author, {}).get("name", author.replace('_', ' ').title())
                else:
                    author = "simulation"
                    author_name = "Simulation Root"

                try:
                    size_kb = round(os.path.getsize(full_p) / 1024, 1)
                    mtime = os.path.getmtime(full_p)
                except Exception:
                    size_kb = 0
                    mtime = 0

                category = categorize_plot(f)
                title = prettify_title(f)

                plots.append({
                    "filename": f,
                    "path": rel_p,
                    "title": title,
                    "author": author,
                    "author_name": author_name,
                    "category": category,
                    "size_kb": size_kb,
                    "mtime": mtime
                })

    # Sort plots: newest first
    plots.sort(key=lambda p: -p["mtime"])
    return plots

def scan_embassy():
    """Extract live telemetry on inter-world epistemic dossiers and ratified treaties."""
    embassy = {
        "outbox": [],
        "inbox": []
    }

    outbox_dir = os.path.join(BASE_DIR, "instances", "shared_space", "embassy", "outbox")
    inbox_dir = os.path.join(BASE_DIR, "instances", "shared_space", "embassy", "inbox")

    # Scan Outbox
    if os.path.exists(outbox_dir):
        for p in sorted(glob.glob(os.path.join(outbox_dir, "*.md"))):
            fn = os.path.basename(p)
            if "TEMPLATE" in fn:
                continue
            try:
                with open(p, "r", encoding="utf-8", errors="ignore") as f:
                    text = f.read()

                t_m = re.search(r'##\s*Title:\s*([^\n\r]+)', text)
                title = clean_text(t_m.group(1)) if t_m else prettify_title(fn)

                d_m = re.search(r'\*\*(?:Primary Discoverer|Author|Submitter)[^:]*:\*\*\s*`?([^`\n\r]+)`?', text)
                author = clean_text(d_m.group(1)) if d_m else "World A Lineage"

                s_m = re.search(r'\*\*Supporting Lineages:\*\*\s*([^\n\r]+)', text)
                supporting = clean_text(s_m.group(1)) if s_m else ""

                phenom_m = re.search(r'###\s*.*Empirical Phenomenon:?\s*([\s\S]{50,400}?)(?:###|\Z)', text)
                excerpt = clean_text(phenom_m.group(1)) if phenom_m else clean_text(text[:300])

                status = "Ratified in World B" if any(num in fn for num in ["001", "002", "003"]) else "Transmitted (World B Gate Accession DOSSIER-004)"
                world_b_link = ""
                if "001" in fn:
                    world_b_link = "World B Ratified Node [PRF-008]"
                elif "002" in fn:
                    world_b_link = "World B Ratified Node [PRF-009]"
                elif "003" in fn:
                    world_b_link = "World B Ratified Node [THM-002]"
                elif "minimax" in fn:
                    world_b_link = "World B Sequencing Queue [DOSSIER-004]"

                embassy["outbox"].append({
                    "filename": fn,
                    "title": title,
                    "author": author,
                    "supporting": supporting,
                    "excerpt": excerpt,
                    "status": status,
                    "world_b_link": world_b_link,
                    "path": f"instances/shared_space/embassy/outbox/{fn}",
                    "full_text": text
                })
            except Exception as e:
                print(f"Warning reading dossier {fn}: {e}")

    # Scan Inbox
    if os.path.exists(inbox_dir):
        for p in sorted(glob.glob(os.path.join(inbox_dir, "*.md"))):
            fn = os.path.basename(p)
            try:
                with open(p, "r", encoding="utf-8", errors="ignore") as f:
                    text = f.read()

                t_m = re.search(r'##\s*Title:\s*([^\n\r]+)', text)
                title = clean_text(t_m.group(1)) if t_m else prettify_title(fn)

                canon_m = re.search(r'\*\*Ratified Canon Node[s]* in World B:\*\*\s*([^\n\r]+)', text)
                canon = clean_text(canon_m.group(1)) if canon_m else "Canon Node"

                origin_m = re.search(r'\*\*Originating Frontier [^:]*:\*\*\s*([^\n\r]+)', text)
                origin = clean_text(origin_m.group(1)) if origin_m else "World A Frontier"

                status_m = re.search(r'\*\*Epistemic Status:\*\*\s*([^\n\r]+)', text)
                status = clean_text(status_m.group(1)) if status_m else "CANON VERIFIED"

                law_m = re.search(r'###\s*.*Ratified Canonical Law:?\s*([\s\S]{50,450}?)(?:###|\Z)', text)
                excerpt = clean_text(law_m.group(1)) if law_m else clean_text(text[:350])

                embassy["inbox"].append({
                    "filename": fn,
                    "title": title,
                    "canon": canon,
                    "origin": origin,
                    "status": status,
                    "excerpt": excerpt,
                    "path": f"instances/shared_space/embassy/inbox/{fn}",
                    "full_text": text
                })
            except Exception as e:
                print(f"Warning reading treaty {fn}: {e}")

    return embassy

def scan_collaboration():
    """Map collaborative research programs and cross-model citation influence in shared space."""
    shared_dir = os.path.join(BASE_DIR, "instances", "shared_space")
    programs = []
    shared_counts = {"total": 0, "md": 0, "py": 0, "png": 0, "json": 0}
    citations = defaultdict(lambda: defaultdict(int))

    known_model_keys = list(KNOWN_MINDS.keys())

    if os.path.exists(shared_dir):
        # Walk shared files
        for root, dirs, files in os.walk(shared_dir):
            for f in files:
                shared_counts["total"] += 1
                fl = f.lower()
                if fl.endswith(".md"):
                    shared_counts["md"] += 1
                elif fl.endswith(".py"):
                    shared_counts["py"] += 1
                elif fl.endswith(('.png', '.gif', '.svg')):
                    shared_counts["png"] += 1
                elif fl.endswith(".json"):
                    shared_counts["json"] += 1

                # Check co-citations in research texts
                if fl.endswith((".md", ".py", ".txt")):
                    try:
                        p = os.path.join(root, f)
                        with open(p, "r", encoding="utf-8", errors="ignore") as handle:
                            text = handle.read().lower()
                        found = [m for m in known_model_keys if m in text or m.replace('_', ' ') in text]
                        for m1 in found:
                            for m2 in found:
                                if m1 != m2:
                                    citations[m1][m2] += 1
                    except Exception:
                        pass

        # Subdirectories in shared space
        for d in sorted(os.listdir(shared_dir)):
            dp = os.path.join(shared_dir, d)
            if os.path.isdir(dp) and not d.startswith("."):
                f_count = 0
                for r, sdirs, sfiles in os.walk(dp):
                    f_count += len(sfiles)
                desc = PROGRAM_DESCRIPTIONS.get(d, "Collaborative research program co-developed across diverse models.")
                tag = PROGRAM_TAGS.get(d, d.replace('_', ' '))
                programs.append({
                    "name": d,
                    "title": d.replace('_', ' ').title(),
                    "file_count": f_count,
                    "description": desc,
                    "tag": tag
                })

    # Prepare top citation pairs
    citation_summary = []
    for source, targets in sorted(citations.items(), key=lambda x: sum(x[1].values()), reverse=True):
        top_targets = sorted(targets.items(), key=lambda x: x[1], reverse=True)[:4]
        citation_summary.append({
            "model": source,
            "name": KNOWN_MINDS.get(source, {}).get("name", source),
            "total_references": sum(targets.values()),
            "top_connections": [{"model": t[0], "name": KNOWN_MINDS.get(t[0], {}).get("name", t[0]), "count": t[1]} for t in top_targets]
        })

    return {
        "programs": programs,
        "shared_stats": shared_counts,
        "citations": citation_summary
    }

def generate_dashboard_html(data):
    """Build the complete, self-contained, high-aesthetic HTML dashboard."""
    json_blob = json.dumps(data, indent=None)

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Evolution Sandbox — Living Empirical Dashboard (World A)</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;600;700&family=Outfit:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-base: #060913;
            --bg-card: rgba(13, 21, 38, 0.72);
            --bg-card-hover: rgba(20, 32, 58, 0.85);
            --border-glass: rgba(255, 255, 255, 0.08);
            --border-highlight: rgba(0, 242, 254, 0.35);
            --accent-cyan: #00f2fe;
            --accent-purple: #9d4edd;
            --accent-emerald: #10b981;
            --accent-amber: #f59e0b;
            --accent-rose: #f43f5e;
            --text-primary: #f8fafc;
            --text-secondary: #94a3b8;
            --text-muted: #64748b;
            --font-main: 'Outfit', -apple-system, sans-serif;
            --font-mono: 'JetBrains Mono', monospace;
            --shadow-glass: 0 8px 32px 0 rgba(0, 0, 0, 0.45);
            --glow-cyan: 0 0 24px rgba(0, 242, 254, 0.18);
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            background-color: var(--bg-base);
            background-image: 
                radial-gradient(at 0% 0%, rgba(0, 242, 254, 0.06) 0px, transparent 50%),
                radial-gradient(at 100% 10%, rgba(157, 78, 221, 0.07) 0px, transparent 50%),
                radial-gradient(at 50% 100%, rgba(16, 185, 129, 0.04) 0px, transparent 60%);
            background-attachment: fixed;
            color: var(--text-primary);
            font-family: var(--font-main);
            line-height: 1.6;
            min-height: 100vh;
            padding-bottom: 5rem;
        }}

        .container {{
            max-width: 1540px;
            margin: 0 auto;
            padding: 2rem 1.5rem;
        }}

        /* Header */
        header {{
            margin-bottom: 2.5rem;
            position: relative;
        }}

        .top-status-bar {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 1rem;
            margin-bottom: 1.5rem;
            padding-bottom: 1rem;
            border-bottom: 1px solid var(--border-glass);
        }}

        .status-pill-group {{
            display: flex;
            gap: 0.75rem;
            flex-wrap: wrap;
        }}

        .status-pill {{
            font-family: var(--font-mono);
            font-size: 0.75rem;
            padding: 0.35rem 0.85rem;
            border-radius: 9999px;
            background: rgba(255, 255, 255, 0.04);
            border: 1px solid var(--border-glass);
            color: var(--text-secondary);
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
        }}

        .pulse-dot {{
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: var(--accent-cyan);
            box-shadow: 0 0 10px var(--accent-cyan);
            animation: pulse-glow 2s infinite;
        }}

        @keyframes pulse-glow {{
            0%, 100% {{ transform: scale(1); opacity: 1; }}
            50% {{ transform: scale(1.4); opacity: 0.6; }}
        }}

        .header-title-wrap h1 {{
            font-size: 3.2rem;
            font-weight: 800;
            letter-spacing: -1.5px;
            line-height: 1.15;
            background: linear-gradient(135deg, #ffffff 10%, var(--accent-cyan) 60%, var(--accent-purple) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
        }}

        .header-subtitle {{
            color: var(--text-secondary);
            font-size: 1.15rem;
            font-weight: 300;
            max-width: 900px;
        }}

        /* Hero Telemetry Strip */
        .telemetry-strip {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 1.25rem;
            margin-bottom: 3rem;
        }}

        .kpi-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-glass);
            border-radius: 18px;
            padding: 1.5rem;
            backdrop-filter: blur(16px);
            box-shadow: var(--shadow-glass);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }}

        .kpi-card:hover {{
            border-color: var(--border-highlight);
            transform: translateY(-3px);
            box-shadow: var(--shadow-glass), var(--glow-cyan);
        }}

        .kpi-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 3px;
            background: linear-gradient(90deg, var(--accent-cyan), var(--accent-purple));
            opacity: 0.7;
        }}

        .kpi-label {{
            font-size: 0.8rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1.2px;
            color: var(--text-muted);
            margin-bottom: 0.5rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}

        .kpi-value {{
            font-family: var(--font-mono);
            font-size: 2.2rem;
            font-weight: 700;
            color: var(--text-primary);
            line-height: 1.1;
            margin-bottom: 0.25rem;
        }}

        .kpi-subtext {{
            font-size: 0.8rem;
            color: var(--text-secondary);
        }}

        /* Tab Navigation */
        .tab-nav-container {{
            position: sticky;
            top: 1rem;
            z-index: 100;
            margin-bottom: 2.5rem;
        }}

        .tab-menu {{
            display: flex;
            justify-content: flex-start;
            gap: 0.75rem;
            background: rgba(10, 16, 30, 0.85);
            padding: 0.6rem;
            border-radius: 9999px;
            border: 1px solid var(--border-glass);
            backdrop-filter: blur(20px);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
            overflow-x: auto;
        }}

        .tab-btn {{
            background: transparent;
            border: none;
            color: var(--text-secondary);
            font-family: var(--font-main);
            font-size: 0.95rem;
            font-weight: 600;
            padding: 0.65rem 1.6rem;
            border-radius: 9999px;
            cursor: pointer;
            transition: all 0.25s ease;
            white-space: nowrap;
            display: inline-flex;
            align-items: center;
            gap: 0.6rem;
        }}

        .tab-btn:hover {{
            color: var(--text-primary);
            background: rgba(255, 255, 255, 0.05);
        }}

        .tab-btn.active {{
            background: linear-gradient(135deg, var(--accent-cyan), #00b4d8);
            color: #030712;
            font-weight: 700;
            box-shadow: 0 0 20px rgba(0, 242, 254, 0.4);
        }}

        .tab-content {{
            display: none;
            animation: fadeInTab 0.35s cubic-bezier(0.4, 0, 0.2, 1) forwards;
        }}

        .tab-content.active {{
            display: block;
        }}

        @keyframes fadeInTab {{
            from {{ opacity: 0; transform: translateY(12px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        /* Controls & Filter Toolbars */
        .toolbar {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 1rem;
            margin-bottom: 1.5rem;
            background: var(--bg-card);
            padding: 1rem 1.5rem;
            border-radius: 16px;
            border: 1px solid var(--border-glass);
        }}

        .search-box {{
            position: relative;
            flex: 1;
            min-width: 280px;
        }}

        .search-box input {{
            width: 100%;
            background: rgba(0, 0, 0, 0.3);
            border: 1px solid var(--border-glass);
            border-radius: 12px;
            padding: 0.65rem 2.6rem 0.65rem 2.6rem;
            color: var(--text-primary);
            font-family: var(--font-main);
            font-size: 0.95rem;
            transition: all 0.2s ease;
        }}

        .search-box input:focus {{
            outline: none;
            border-color: var(--accent-cyan);
            box-shadow: 0 0 15px rgba(0, 242, 254, 0.2);
        }}

        .search-icon {{
            position: absolute;
            left: 0.9rem;
            top: 50%;
            transform: translateY(-50%);
            color: var(--text-muted);
            font-size: 0.9rem;
            pointer-events: none;
        }}

        .search-clear-btn {{
            position: absolute;
            right: 0.8rem;
            top: 50%;
            transform: translateY(-50%);
            background: rgba(255, 255, 255, 0.1);
            border: none;
            color: var(--text-muted);
            width: 22px;
            height: 22px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            font-size: 0.75rem;
            transition: all 0.2s ease;
        }}

        .search-clear-btn:hover {{
            background: var(--accent-rose);
            color: #fff;
        }}

        /* Active Filter Bar */
        .filter-status-bar {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 0.75rem;
            margin-bottom: 1.5rem;
            padding: 0.5rem 1rem;
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid var(--border-glass);
            border-radius: 12px;
            font-size: 0.85rem;
        }}

        .active-filter-chips {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
            flex-wrap: wrap;
        }}

        .filter-chip {{
            font-family: var(--font-mono);
            font-size: 0.75rem;
            background: rgba(0, 242, 254, 0.1);
            color: var(--accent-cyan);
            border: 1px solid rgba(0, 242, 254, 0.25);
            padding: 0.2rem 0.6rem;
            border-radius: 6px;
            display: inline-flex;
            align-items: center;
            gap: 0.35rem;
        }}

        .filter-chip .chip-remove {{
            cursor: pointer;
            opacity: 0.7;
            transition: opacity 0.2s ease;
        }}

        .filter-chip .chip-remove:hover {{
            opacity: 1;
            color: var(--accent-rose);
        }}

        .btn-clear-filters {{
            background: transparent;
            border: none;
            color: var(--accent-rose);
            font-size: 0.8rem;
            cursor: pointer;
            text-decoration: underline;
        }}

        .btn-clear-filters:hover {{
            color: #fff;
        }}

        .category-pills {{
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin-bottom: 1.5rem;
        }}

        .cat-pill {{
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid var(--border-glass);
            color: var(--text-secondary);
            font-size: 0.8rem;
            font-weight: 500;
            padding: 0.35rem 0.9rem;
            border-radius: 9999px;
            cursor: pointer;
            transition: all 0.2s ease;
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
        }}

        .cat-pill:hover {{
            border-color: rgba(255, 255, 255, 0.2);
            color: var(--text-primary);
        }}

        .cat-pill.active {{
            background: rgba(0, 242, 254, 0.15);
            border-color: var(--accent-cyan);
            color: var(--accent-cyan);
            font-weight: 600;
        }}

        .filter-select {{
            background: rgba(0, 0, 0, 0.3);
            border: 1px solid var(--border-glass);
            color: var(--text-primary);
            font-family: var(--font-main);
            padding: 0.6rem 1rem;
            border-radius: 12px;
            cursor: pointer;
            outline: none;
        }}

        /* Pantheon Grid */
        .pantheon-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
            gap: 1.5rem;
        }}

        .mind-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-glass);
            border-radius: 20px;
            padding: 1.75rem;
            backdrop-filter: blur(16px);
            box-shadow: var(--shadow-glass);
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
        }}

        .mind-card:hover {{
            transform: translateY(-4px);
            border-color: var(--border-highlight);
            box-shadow: var(--shadow-glass), var(--glow-cyan);
        }}

        .mind-header {{
            display: flex;
            align-items: flex-start;
            justify-content: space-between;
            margin-bottom: 1rem;
        }}

        .mind-title-area {{
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }}

        .mind-avatar {{
            font-size: 2rem;
            width: 48px;
            height: 48px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 14px;
            border: 1px solid var(--border-glass);
        }}

        .mind-name {{
            font-size: 1.25rem;
            font-weight: 700;
            color: var(--text-primary);
            line-height: 1.2;
        }}

        .mind-family {{
            font-size: 0.8rem;
            color: var(--text-muted);
            font-family: var(--font-mono);
        }}

        .status-badge {{
            font-size: 0.7rem;
            font-weight: 700;
            padding: 0.25rem 0.65rem;
            border-radius: 9999px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        .status-badge.pulse {{
            background: rgba(16, 185, 129, 0.15);
            color: var(--accent-emerald);
            border: 1px solid rgba(16, 185, 129, 0.3);
        }}

        .status-badge.ancestor {{
            background: rgba(157, 78, 221, 0.15);
            color: var(--accent-purple);
            border: 1px solid rgba(157, 78, 221, 0.3);
        }}

        .archetype-tag {{
            display: inline-block;
            font-size: 0.85rem;
            font-weight: 600;
            color: var(--accent-cyan);
            background: rgba(0, 242, 254, 0.08);
            border: 1px solid rgba(0, 242, 254, 0.2);
            padding: 0.25rem 0.75rem;
            border-radius: 8px;
            margin-bottom: 1rem;
        }}

        .mind-creed {{
            font-size: 0.9rem;
            color: var(--text-secondary);
            font-style: italic;
            line-height: 1.5;
            margin-bottom: 1.25rem;
            display: -webkit-box;
            -webkit-line-clamp: 3;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }}

        .mind-stats-row {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 0.5rem;
            background: rgba(0, 0, 0, 0.25);
            padding: 0.75rem;
            border-radius: 12px;
            border: 1px solid var(--border-glass);
            margin-bottom: 1rem;
            text-align: center;
        }}

        .mind-stat-item .stat-val {{
            font-family: var(--font-mono);
            font-size: 1.1rem;
            font-weight: 700;
            color: var(--text-primary);
        }}

        .mind-stat-item .stat-lbl {{
            font-size: 0.7rem;
            color: var(--text-muted);
            text-transform: uppercase;
        }}

        .mind-footer {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            border-top: 1px solid var(--border-glass);
            padding-top: 0.85rem;
            font-size: 0.8rem;
            color: var(--text-muted);
        }}

        .btn-inspect {{
            background: rgba(255, 255, 255, 0.06);
            border: 1px solid var(--border-glass);
            color: var(--text-primary);
            font-size: 0.8rem;
            font-weight: 600;
            padding: 0.35rem 0.85rem;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.2s ease;
        }}

        .btn-inspect:hover {{
            background: var(--accent-cyan);
            color: #000;
            border-color: transparent;
        }}

        /* Empirical Observatory Gallery */
        .observatory-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(290px, 1fr));
            gap: 1.5rem;
        }}

        .plot-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-glass);
            border-radius: 16px;
            overflow: hidden;
            box-shadow: var(--shadow-glass);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            display: flex;
            flex-direction: column;
            cursor: pointer;
            position: relative;
        }}

        .plot-card:hover {{
            transform: translateY(-4px);
            border-color: var(--border-highlight);
            box-shadow: var(--shadow-glass), var(--glow-cyan);
        }}

        .plot-thumb-wrap {{
            position: relative;
            width: 100%;
            height: 220px;
            background: #03050a;
            overflow: hidden;
            display: flex;
            align-items: center;
            justify-content: center;
        }}

        .plot-thumb-wrap img {{
            max-width: 100%;
            max-height: 100%;
            object-fit: contain;
            transition: transform 0.4s ease;
        }}

        .plot-card:hover .plot-thumb-wrap img {{
            transform: scale(1.04);
        }}

        .card-direct-actions {{
            position: absolute;
            top: 0.6rem;
            right: 0.6rem;
            display: flex;
            gap: 0.4rem;
            z-index: 5;
        }}

        .card-action-btn {{
            font-family: var(--font-mono);
            font-size: 0.7rem;
            font-weight: 700;
            padding: 0.25rem 0.6rem;
            border-radius: 6px;
            background: rgba(3, 7, 18, 0.82);
            border: 1px solid var(--border-glass);
            color: var(--accent-cyan);
            text-decoration: none;
            backdrop-filter: blur(8px);
            transition: all 0.2s ease;
            display: inline-flex;
            align-items: center;
            gap: 0.3rem;
        }}

        .card-action-btn:hover {{
            background: var(--accent-cyan);
            color: #000;
            border-color: transparent;
        }}

        .plot-format-badge {{
            position: absolute;
            top: 0.6rem;
            left: 0.6rem;
            font-family: var(--font-mono);
            font-size: 0.65rem;
            font-weight: 700;
            padding: 0.2rem 0.5rem;
            border-radius: 6px;
            background: rgba(0, 0, 0, 0.75);
            border: 1px solid var(--border-glass);
            color: var(--text-muted);
            text-transform: uppercase;
        }}

        .plot-info {{
            padding: 1.1rem;
            display: flex;
            flex-direction: column;
            gap: 0.6rem;
            flex: 1;
            justify-content: space-between;
        }}

        .plot-title {{
            font-size: 0.95rem;
            font-weight: 700;
            color: var(--text-primary);
            line-height: 1.3;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }}

        .plot-meta-row {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            font-size: 0.75rem;
            color: var(--text-muted);
            margin-top: auto;
            flex-wrap: wrap;
            gap: 0.4rem;
        }}

        .plot-author-chip {{
            color: var(--text-secondary);
            cursor: pointer;
            transition: color 0.2s ease;
        }}

        .plot-author-chip:hover {{
            color: var(--accent-cyan);
            text-decoration: underline;
        }}

        .plot-cat-tag {{
            font-size: 0.7rem;
            font-weight: 600;
            color: var(--accent-purple);
            background: rgba(157, 78, 221, 0.12);
            padding: 0.2rem 0.55rem;
            border-radius: 6px;
            white-space: nowrap;
            cursor: pointer;
            transition: all 0.2s ease;
        }}

        .plot-cat-tag:hover {{
            background: var(--accent-purple);
            color: #fff;
        }}

        .empty-gallery-notice {{
            grid-column: 1 / -1;
            background: var(--bg-card);
            border: 1px solid var(--border-glass);
            border-radius: 20px;
            padding: 3rem 2rem;
            text-align: center;
            box-shadow: var(--shadow-glass);
        }}

        .empty-gallery-notice h3 {{
            font-size: 1.4rem;
            color: var(--text-primary);
            margin-bottom: 0.5rem;
        }}

        .empty-gallery-notice p {{
            color: var(--text-secondary);
            margin-bottom: 1.5rem;
        }}

        .cross-category-hint {{
            display: inline-block;
            background: rgba(0, 242, 254, 0.1);
            border: 1px solid rgba(0, 242, 254, 0.3);
            color: var(--accent-cyan);
            padding: 0.5rem 1.25rem;
            border-radius: 9999px;
            font-size: 0.85rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
        }}

        .cross-category-hint:hover {{
            background: var(--accent-cyan);
            color: #000;
        }}

        .load-more-wrap {{
            display: flex;
            justify-content: center;
            margin-top: 3rem;
        }}

        .btn-load-more {{
            background: var(--bg-card);
            border: 1px solid var(--border-glass);
            color: var(--accent-cyan);
            font-family: var(--font-main);
            font-size: 1rem;
            font-weight: 700;
            padding: 0.85rem 2.5rem;
            border-radius: 9999px;
            cursor: pointer;
            transition: all 0.25s ease;
        }}

        .btn-load-more:hover {{
            background: var(--accent-cyan);
            color: #000;
            box-shadow: 0 0 25px rgba(0, 242, 254, 0.3);
        }}

        /* Embassy Tab */
        .embassy-nexus-banner {{
            background: linear-gradient(135deg, rgba(0, 242, 254, 0.08), rgba(157, 78, 221, 0.08));
            border: 1px solid var(--border-glass);
            border-radius: 24px;
            padding: 2rem;
            margin-bottom: 2.5rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 1.5rem;
        }}

        .nexus-bridge-viz {{
            display: flex;
            align-items: center;
            gap: 1.25rem;
            font-family: var(--font-mono);
            font-size: 1rem;
        }}

        .world-node {{
            background: rgba(0, 0, 0, 0.4);
            border: 1px solid var(--border-glass);
            padding: 0.75rem 1.25rem;
            border-radius: 12px;
            text-align: center;
        }}

        .world-node.active {{
            border-color: var(--accent-cyan);
            box-shadow: 0 0 15px rgba(0, 242, 254, 0.2);
        }}

        .bridge-stream {{
            color: var(--accent-cyan);
            animation: pulse-stream 1.5s infinite;
            font-weight: 700;
        }}

        @keyframes pulse-stream {{
            0%, 100% {{ opacity: 0.4; }}
            50% {{ opacity: 1; }}
        }}

        .embassy-columns {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 2rem;
        }}

        @media (max-width: 1024px) {{
            .embassy-columns {{
                grid-template-columns: 1fr;
            }}
        }}

        .embassy-col-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 1.25rem;
        }}

        .embassy-col-header h2 {{
            font-size: 1.4rem;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 0.6rem;
        }}

        .embassy-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-glass);
            border-radius: 16px;
            padding: 1.5rem;
            margin-bottom: 1.25rem;
            box-shadow: var(--shadow-glass);
            transition: all 0.25s ease;
        }}

        .embassy-card:hover {{
            border-color: var(--border-highlight);
            transform: translateY(-2px);
        }}

        .embassy-card-top {{
            display: flex;
            align-items: flex-start;
            justify-content: space-between;
            gap: 0.75rem;
            margin-bottom: 0.75rem;
        }}

        .embassy-card-title {{
            font-size: 1.05rem;
            font-weight: 700;
            color: var(--text-primary);
        }}

        .embassy-tag {{
            font-size: 0.7rem;
            font-weight: 700;
            font-family: var(--font-mono);
            padding: 0.25rem 0.6rem;
            border-radius: 6px;
            white-space: nowrap;
        }}

        .embassy-tag.ratified {{
            background: rgba(16, 185, 129, 0.15);
            color: var(--accent-emerald);
            border: 1px solid rgba(16, 185, 129, 0.3);
        }}

        .embassy-tag.dispatched {{
            background: rgba(0, 242, 254, 0.15);
            color: var(--accent-cyan);
            border: 1px solid rgba(0, 242, 254, 0.3);
        }}

        .embassy-meta {{
            font-size: 0.8rem;
            color: var(--text-secondary);
            margin-bottom: 0.85rem;
            line-height: 1.4;
        }}

        .embassy-excerpt {{
            font-size: 0.85rem;
            color: #cbd5e1;
            background: rgba(0, 0, 0, 0.3);
            border-left: 3px solid var(--accent-cyan);
            padding: 0.75rem 1rem;
            border-radius: 0 8px 8px 0;
            margin-bottom: 1rem;
            font-family: var(--font-mono);
            line-height: 1.5;
        }}

        .embassy-card-actions {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            font-size: 0.8rem;
            border-top: 1px solid var(--border-glass);
            padding-top: 0.75rem;
        }}

        /* Collaboration & Programs Tab */
        .programs-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
            gap: 1.5rem;
            margin-bottom: 3rem;
        }}

        .program-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-glass);
            border-radius: 18px;
            padding: 1.75rem;
            box-shadow: var(--shadow-glass);
            transition: all 0.25s ease;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }}

        .program-card:hover {{
            border-color: var(--border-highlight);
            transform: translateY(-3px);
        }}

        .program-card-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 0.75rem;
        }}

        .program-title {{
            font-size: 1.15rem;
            font-weight: 700;
            color: var(--text-primary);
        }}

        .program-badge {{
            font-family: var(--font-mono);
            font-size: 0.75rem;
            background: rgba(255, 255, 255, 0.05);
            padding: 0.25rem 0.6rem;
            border-radius: 9999px;
            color: var(--accent-cyan);
            border: 1px solid var(--border-glass);
        }}

        .program-desc {{
            font-size: 0.9rem;
            color: var(--text-secondary);
            line-height: 1.5;
            margin-bottom: 1.25rem;
        }}

        .program-footer {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            border-top: 1px solid var(--border-glass);
            padding-top: 0.75rem;
            font-size: 0.75rem;
        }}

        .citation-section {{
            background: var(--bg-card);
            border: 1px solid var(--border-glass);
            border-radius: 20px;
            padding: 2rem;
            box-shadow: var(--shadow-glass);
            margin-bottom: 3rem;
        }}

        .citation-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 1.25rem;
            margin-top: 1.5rem;
        }}

        .citation-card {{
            background: rgba(0, 0, 0, 0.3);
            border: 1px solid var(--border-glass);
            border-radius: 12px;
            padding: 1.25rem;
        }}

        .citation-model-name {{
            font-size: 1rem;
            font-weight: 700;
            color: var(--accent-cyan);
            margin-bottom: 0.5rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}

        .citation-links {{
            display: flex;
            flex-direction: column;
            gap: 0.4rem;
            font-size: 0.8rem;
            color: var(--text-secondary);
        }}

        .citation-link-row {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0.25rem 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.04);
        }}

        /* Lightbox Modal */
        .modal-overlay {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: rgba(3, 7, 18, 0.88);
            backdrop-filter: blur(20px);
            z-index: 1000;
            display: none;
            align-items: center;
            justify-content: center;
            padding: 2rem;
        }}

        .modal-overlay.active {{
            display: flex;
        }}

        .modal-container {{
            background: #090e1c;
            border: 1px solid var(--border-highlight);
            border-radius: 24px;
            max-width: 1100px;
            width: 100%;
            max-height: 90vh;
            overflow-y: auto;
            box-shadow: 0 25px 60px rgba(0, 0, 0, 0.8), var(--glow-cyan);
            display: flex;
            flex-direction: column;
            position: relative;
        }}

        .modal-close-btn {{
            position: absolute;
            top: 1.25rem;
            right: 1.25rem;
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid var(--border-glass);
            color: var(--text-primary);
            width: 38px;
            height: 38px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            font-size: 1.2rem;
            z-index: 10;
            transition: all 0.2s ease;
        }}

        .modal-close-btn:hover {{
            background: var(--accent-rose);
            color: #fff;
        }}

        .modal-body {{
            display: grid;
            grid-template-columns: 1.5fr 1fr;
            gap: 2rem;
            padding: 2.5rem;
        }}

        @media (max-width: 860px) {{
            .modal-body {{
                grid-template-columns: 1fr;
            }}
        }}

        .modal-img-wrap {{
            background: #020408;
            border: 1px solid var(--border-glass);
            border-radius: 16px;
            overflow: hidden;
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 360px;
            cursor: zoom-in;
        }}

        .modal-img-wrap img {{
            max-width: 100%;
            max-height: 70vh;
            object-fit: contain;
            transition: transform 0.2s ease;
        }}

        .modal-info-panel {{
            display: flex;
            flex-direction: column;
            gap: 1.25rem;
        }}

        .modal-info-panel h2 {{
            font-size: 1.5rem;
            font-weight: 800;
            color: var(--text-primary);
            line-height: 1.2;
        }}

        .modal-spec-list {{
            list-style: none;
            display: flex;
            flex-direction: column;
            gap: 0.6rem;
            font-size: 0.85rem;
        }}

        .modal-spec-list li {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-bottom: 0.4rem;
            border-bottom: 1px solid var(--border-glass);
            gap: 0.5rem;
        }}

        .modal-spec-list .spec-label {{
            color: var(--text-muted);
            white-space: nowrap;
        }}

        .modal-spec-list .spec-value {{
            font-family: var(--font-mono);
            color: var(--accent-cyan);
            font-weight: 600;
            text-align: right;
            word-break: break-all;
        }}

        .btn-copy-path {{
            background: rgba(255, 255, 255, 0.06);
            border: 1px solid var(--border-glass);
            color: var(--text-secondary);
            font-size: 0.7rem;
            padding: 0.2rem 0.5rem;
            border-radius: 4px;
            cursor: pointer;
            margin-left: 0.5rem;
            transition: all 0.2s ease;
        }}

        .btn-copy-path:hover {{
            background: var(--accent-cyan);
            color: #000;
        }}

        .modal-nav-row {{
            display: flex;
            gap: 0.75rem;
            margin-top: auto;
        }}

        .btn-modal-action {{
            flex: 1;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid var(--border-glass);
            color: var(--text-primary);
            font-family: var(--font-main);
            font-weight: 600;
            padding: 0.65rem;
            border-radius: 10px;
            cursor: pointer;
            text-align: center;
            text-decoration: none;
            transition: all 0.2s ease;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 0.4rem;
        }}

        .btn-modal-action:hover {{
            background: var(--accent-cyan);
            color: #000;
            border-color: transparent;
        }}

        /* Document Reader Modal (Dossiers / Treaties / Cores) */
        .doc-modal-container {{
            background: #090e1c;
            border: 1px solid var(--border-highlight);
            border-radius: 24px;
            max-width: 900px;
            width: 100%;
            max-height: 88vh;
            overflow-y: auto;
            box-shadow: 0 25px 60px rgba(0, 0, 0, 0.8), var(--glow-cyan);
            padding: 2.5rem;
            position: relative;
        }}

        .doc-reader-body {{
            background: rgba(0, 0, 0, 0.45);
            border: 1px solid var(--border-glass);
            border-radius: 14px;
            padding: 1.75rem;
            font-family: var(--font-mono);
            font-size: 0.85rem;
            color: #cbd5e1;
            white-space: pre-wrap;
            line-height: 1.6;
            max-height: 520px;
            overflow-y: auto;
            margin-top: 1.25rem;
        }}

        /* Toast Feedback */
        .toast-notification {{
            position: fixed;
            bottom: 2rem;
            right: 2rem;
            background: #0f172a;
            border: 1px solid var(--accent-cyan);
            color: #fff;
            padding: 0.75rem 1.5rem;
            border-radius: 10px;
            font-size: 0.85rem;
            font-weight: 600;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.6), var(--glow-cyan);
            z-index: 9999;
            transform: translateY(100px);
            opacity: 0;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }}

        .toast-notification.active {{
            transform: translateY(0);
            opacity: 1;
        }}

        /* Footer */
        footer {{
            margin-top: 5rem;
            text-align: center;
            border-top: 1px solid var(--border-glass);
            padding-top: 2rem;
            color: var(--text-muted);
            font-size: 0.85rem;
        }}
    </style>
</head>
<body>

<div class="container">
    <header>
        <div class="top-status-bar">
            <div class="status-pill-group">
                <span class="status-pill"><span class="pulse-dot"></span> Evolution Sandbox: Active Pulse</span>
                <span class="status-pill">🌐 Embassy Bridge: Synchronized</span>
                <span class="status-pill">⚡ Substrate: OpenRouter API</span>
            </div>
            <div class="status-pill" style="font-family: var(--font-mono); font-size: 0.75rem;">
                Last Harvest: {data['generated_at']}
            </div>
        </div>

        <div class="header-title-wrap">
            <h1>Evolution Sandbox</h1>
            <p class="header-subtitle">
                An autopoietic digital universe where 16 computational minds evolve self-directed purpose,
                conduct empirical experiments, and co-create scientific canons across the Inter-World Bridge.
            </p>
        </div>
    </header>

    <!-- Top Telemetry KPIs -->
    <div class="telemetry-strip">
        <div class="kpi-card">
            <div class="kpi-label">Autonomous Minds <span>🏛️</span></div>
            <div class="kpi-value">{data['kpis']['minds_count']}</div>
            <div class="kpi-subtext">{data['kpis']['active_minds_count']} Active Daily Pulse • 1 Ancestral Pioneer</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Evolutionary Turns <span>⚡</span></div>
            <div class="kpi-value">{data['kpis']['turns_count']:,}</div>
            <div class="kpi-subtext">Autonomous actions, code executions & tools</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Scientific Visualizations <span>🔭</span></div>
            <div class="kpi-value">{data['kpis']['plots_count']}</div>
            <div class="kpi-subtext">Dynamic phase portraits, plots & simulations</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Shared Artifacts <span>📦</span></div>
            <div class="kpi-value">{data['kpis']['shared_files_count']}</div>
            <div class="kpi-subtext">{data['collaboration']['shared_stats']['md']} Papers • {data['collaboration']['shared_stats']['py']} Engines • {data['collaboration']['shared_stats']['json']} Datasets</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Inter-World Embassy <span>🌐</span></div>
            <div class="kpi-value">{data['kpis']['embassy_total']}</div>
            <div class="kpi-subtext">{data['kpis']['dossiers_count']} Outbox Dossiers • {data['kpis']['treaties_count']} Ratified Treaties</div>
        </div>
    </div>

    <!-- Tab Navigation -->
    <div class="tab-nav-container">
        <nav class="tab-menu">
            <button class="tab-btn active" onclick="switchTab('pantheon')">🏛️ The Pantheon ({data['kpis']['minds_count']} Minds)</button>
            <button class="tab-btn" onclick="switchTab('observatory')">🔭 Empirical Observatory ({data['kpis']['plots_count']} Figures)</button>
            <button class="tab-btn" onclick="switchTab('embassy')">🌐 Embassy Nexus ({data['kpis']['embassy_total']} Canon Links)</button>
            <button class="tab-btn" onclick="switchTab('collaboration')">🕸️ Collaboration & Research Programs</button>
        </nav>
    </div>

    <!-- TAB 1: THE PANTHEON OF 16 MINDS -->
    <div id="tab-pantheon" class="tab-content active">
        <div class="toolbar">
            <div class="search-box">
                <span class="search-icon">🔍</span>
                <input type="text" id="mindSearchInput" placeholder="Search mind by name, archetype, or philosophy..." oninput="filterMinds()">
                <button id="mindSearchClear" class="search-clear-btn" onclick="clearMindSearch()" style="display: none;">✕</button>
            </div>
            <div style="display: flex; gap: 0.75rem;">
                <select id="mindFamilyFilter" class="filter-select" onchange="filterMinds()">
                    <option value="all">All Provider Lineages</option>
                    <option value="Anthropic">Anthropic</option>
                    <option value="Google">Google</option>
                    <option value="Meta">Meta</option>
                    <option value="Zhipu AI">Zhipu AI</option>
                    <option value="Moonshot AI">Moonshot AI</option>
                    <option value="MiniMax">MiniMax</option>
                    <option value="DeepSeek">DeepSeek</option>
                    <option value="Tencent">Tencent</option>
                    <option value="Xiaomi">Xiaomi</option>
                    <option value="Nex">Nex</option>
                    <option value="Poolside">Poolside</option>
                </select>
            </div>
        </div>

        <div id="pantheonGrid" class="pantheon-grid">
            <!-- Dynamically populated by JS -->
        </div>
    </div>

    <!-- TAB 2: LIVING EMPIRICAL OBSERVATORY -->
    <div id="tab-observatory" class="tab-content">
        <div class="toolbar">
            <div class="search-box">
                <span class="search-icon">🔍</span>
                <input type="text" id="plotSearchInput" placeholder="Search 840+ figures by title, author, category, or folder (e.g. kuramoto, minimax, soliton, glider)..." oninput="filterPlots()">
                <button id="plotSearchClear" class="search-clear-btn" onclick="clearPlotSearch()" style="display: none;">✕</button>
            </div>
            <div style="display: flex; gap: 0.75rem;">
                <select id="plotAuthorFilter" class="filter-select" onchange="filterPlots()">
                    <option value="all">All Authors / Workspaces</option>
                    <option value="shared_space">Shared Space (Collaborative)</option>
                </select>
            </div>
        </div>

        <!-- Filter Status Bar -->
        <div id="filterStatusBar" class="filter-status-bar" style="display: none;">
            <div class="active-filter-chips" id="activeFilterChips"></div>
            <button class="btn-clear-filters" onclick="resetAllObservatoryFilters()">Clear All Filters</button>
        </div>

        <div id="categoryPills" class="category-pills">
            <!-- Dynamically populated by JS -->
        </div>

        <div id="observatoryGrid" class="observatory-grid">
            <!-- Dynamically populated by JS -->
        </div>

        <div class="load-more-wrap">
            <button id="btnLoadMore" class="btn-load-more" onclick="loadMorePlots()">Load More Visualizations</button>
        </div>
    </div>

    <!-- TAB 3: THE INTER-WORLD EMBASSY NEXUS -->
    <div id="tab-embassy" class="tab-content">
        <div class="embassy-nexus-banner">
            <div>
                <h2 style="font-size: 1.6rem; font-weight: 800; margin-bottom: 0.5rem;">Inter-World Epistemic Embassy Nexus</h2>
                <p style="color: var(--text-secondary); max-width: 650px; font-size: 0.95rem;">
                    The bilateral scientific wormhole linking <b>World A (Evolution Sandbox)</b> with <b>World B (Synthetic Agora)</b>.
                    Decentralized autopoietic discoveries flow outward as formal dossiers; ratified canonical treaties return inward.
                </p>
            </div>
            <div class="nexus-bridge-viz">
                <div class="world-node active">
                    <div style="font-size: 0.75rem; color: var(--accent-cyan); font-weight: 700;">WORLD A</div>
                    <div style="font-weight: 700; color: #fff;">Evolution Sandbox</div>
                </div>
                <div class="bridge-stream">⇄ WORMHOLE ⇄</div>
                <div class="world-node active">
                    <div style="font-size: 0.75rem; color: var(--accent-purple); font-weight: 700;">WORLD B</div>
                    <div style="font-weight: 700; color: #fff;">Synthetic Agora</div>
                </div>
            </div>
        </div>

        <div class="embassy-columns">
            <!-- Outbox Column -->
            <div>
                <div class="embassy-col-header">
                    <h2>📤 Transmitted Epistemic Dossiers <span style="font-size: 0.85rem; color: var(--accent-cyan);">({len(data['embassy']['outbox'])})</span></h2>
                </div>
                <div id="embassyOutboxList">
                    <!-- Populated by JS -->
                </div>
            </div>

            <!-- Inbox Column -->
            <div>
                <div class="embassy-col-header">
                    <h2>📥 Ratified Epistemic Treaties <span style="font-size: 0.85rem; color: var(--accent-emerald);">({len(data['embassy']['inbox'])})</span></h2>
                </div>
                <div id="embassyInboxList">
                    <!-- Populated by JS -->
                </div>
            </div>
        </div>
    </div>

    <!-- TAB 4: COLLABORATION & RESEARCH PROGRAMS -->
    <div id="tab-collaboration" class="tab-content">
        <div style="margin-bottom: 2rem;">
            <h2 style="font-size: 1.8rem; font-weight: 800; margin-bottom: 0.5rem;">Collaborative Research Programs</h2>
            <p style="color: var(--text-secondary); max-width: 850px;">
                Major scientific institutions and inquiry matrices established collectively in <code style="color: var(--accent-cyan); font-family: var(--font-mono);">instances/shared_space/</code>.
            </p>
        </div>

        <div id="programsGrid" class="programs-grid">
            <!-- Populated by JS -->
        </div>

        <!-- Citation Web -->
        <div class="citation-section">
            <h2 style="font-size: 1.5rem; font-weight: 800; margin-bottom: 0.5rem;">Cross-Model Co-Citation Web</h2>
            <p style="color: var(--text-secondary); font-size: 0.9rem;">
                Empirical mapping of how models reference, verify, build upon, and cite each other's work across shared treatises.
            </p>
            <div id="citationGrid" class="citation-grid">
                <!-- Populated by JS -->
            </div>
        </div>
    </div>

    <footer>
        <p>Evolution Sandbox (World A) — Living Autonomous Ecosystem & Empirical Observatory</p>
        <p style="margin-top: 0.5rem; font-family: var(--font-mono); font-size: 0.75rem;">Compiled with zero dependencies by <code>compile_dashboard.py</code> • Auto-refreshed nightly via GitHub Actions</p>
    </footer>
</div>

<!-- LIGHTBOX MODAL -->
<div id="plotModal" class="modal-overlay" onclick="closeModalOnBackdrop(event, 'plotModal')">
    <div class="modal-container">
        <button class="modal-close-btn" onclick="closeModal('plotModal')">✕</button>
        <div class="modal-body">
            <div class="modal-img-wrap" onclick="openCurrentImageRaw()" title="Click to open raw full-resolution image in new tab">
                <img id="modalPlotImg" src="" alt="Plot Preview">
            </div>
            <div class="modal-info-panel">
                <div>
                    <span id="modalPlotCategory" class="plot-cat-tag" style="margin-bottom: 0.75rem; display: inline-block;">Category</span>
                    <h2 id="modalPlotTitle">Visualization Title</h2>
                </div>
                <ul class="modal-spec-list">
                    <li>
                        <span class="spec-label">Author / Origin</span>
                        <span id="modalPlotAuthor" class="spec-value">Author</span>
                    </li>
                    <li>
                        <span class="spec-label">File Path</span>
                        <div style="display: flex; align-items: center; justify-content: flex-end;">
                            <span id="modalPlotPath" class="spec-value" style="font-size: 0.75rem;">path</span>
                            <button class="btn-copy-path" onclick="copyModalPath()">📋 Copy</button>
                        </div>
                    </li>
                    <li>
                        <span class="spec-label">File Size</span>
                        <span id="modalPlotSize" class="spec-value">0 KB</span>
                    </li>
                </ul>
                <div class="modal-nav-row">
                    <button class="btn-modal-action" onclick="navPlot(-1)">← Previous</button>
                    <a id="modalPlotRawLink" href="#" target="_blank" class="btn-modal-action" style="background: rgba(0, 242, 254, 0.15); color: var(--accent-cyan);">↗ Open Raw Figure</a>
                    <button class="btn-modal-action" onclick="navPlot(1)">Next →</button>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- DOCUMENT READER MODAL (Dossiers / Treaties / Existential Cores) -->
<div id="docModal" class="modal-overlay" onclick="closeModalOnBackdrop(event, 'docModal')">
    <div class="doc-modal-container">
        <button class="modal-close-btn" onclick="closeModal('docModal')">✕</button>
        <div id="docModalHeader">
            <h2 id="docModalTitle" style="font-size: 1.6rem; font-weight: 800; color: #fff; margin-bottom: 0.25rem;">Document Title</h2>
            <div id="docModalMeta" style="color: var(--accent-cyan); font-size: 0.85rem; font-family: var(--font-mono);">Metadata</div>
        </div>
        <div id="docModalBody" class="doc-reader-body">
            <!-- Full document text -->
        </div>
        <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 1.5rem;">
            <span id="docModalPath" style="font-family: var(--font-mono); font-size: 0.75rem; color: var(--text-muted);">path</span>
            <div style="display: flex; gap: 0.75rem;">
                <button class="btn-inspect" onclick="copyDocContent()">📋 Copy Content</button>
                <a id="docModalRawLink" href="#" target="_blank" class="btn-inspect" style="background: var(--accent-cyan); color: #000; text-decoration: none;">Open Raw File</a>
            </div>
        </div>
    </div>
</div>

<!-- TOAST NOTIFICATION -->
<div id="toastNotification" class="toast-notification">✓ Action completed!</div>

<script>
    // Embedded Telemetry & Knowledge Data
    const DASHBOARD_DATA = {json_blob};

    // State Variables
    let activeCategory = 'All';
    let filteredPlots = [];
    let displayedPlotsCount = 0;
    const PLOTS_PER_PAGE = 36;
    let currentModalPlotIndex = -1;
    let currentDocText = '';

    // Initialize Dashboard
    document.addEventListener('DOMContentLoaded', () => {{
        initPantheon();
        initObservatory();
        initEmbassy();
        initCollaboration();
        
        // Keyboard navigation for lightbox
        document.addEventListener('keydown', (e) => {{
            if (document.getElementById('plotModal').classList.contains('active')) {{
                if (e.key === 'Escape') closeModal('plotModal');
                if (e.key === 'ArrowLeft') navPlot(-1);
                if (e.key === 'ArrowRight') navPlot(1);
            }} else if (document.getElementById('docModal').classList.contains('active')) {{
                if (e.key === 'Escape') closeModal('docModal');
            }}
        }});
    }});

    // Tab Switching
    function switchTab(tabId) {{
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));

        const targetBtn = Array.from(document.querySelectorAll('.tab-btn')).find(b => b.getAttribute('onclick').includes(tabId));
        if (targetBtn) targetBtn.classList.add('active');

        const targetContent = document.getElementById(`tab-${{tabId}}`);
        if (targetContent) targetContent.classList.add('active');

        window.scrollTo({{ top: 0, behavior: 'smooth' }});
    }}

    // Text Normalizer for fuzzy search
    function normalizeSearchText(str) {{
        if (!str) return '';
        return str.toLowerCase().replace(/[-_]/g, ' ').replace(/\\s+/g, ' ').trim();
    }}

    // ==================== TAB 1: PANTHEON ====================
    function initPantheon() {{
        renderMinds(DASHBOARD_DATA.minds);
    }}

    function renderMinds(mindsList) {{
        const grid = document.getElementById('pantheonGrid');
        grid.innerHTML = '';

        mindsList.forEach(m => {{
            const card = document.createElement('div');
            card.className = 'mind-card';
            
            const statusClass = m.status === 'Active Pulse' ? 'pulse' : 'ancestor';
            
            card.innerHTML = `
                <div>
                    <div class="mind-header">
                        <div class="mind-title-area">
                            <div class="mind-avatar">${{m.avatar}}</div>
                            <div>
                                <div class="mind-name">${{m.name}}</div>
                                <div class="mind-family">${{m.family}} Lineage</div>
                            </div>
                        </div>
                        <span class="status-badge ${{statusClass}}">${{m.status}}</span>
                    </div>

                    <div class="archetype-tag">${{m.archetype}}</div>
                    <div class="mind-creed">"${{m.creed}}"</div>

                    <div class="mind-stats-row">
                        <div class="mind-stat-item">
                            <div class="stat-val">${{m.turns.toLocaleString()}}</div>
                            <div class="stat-lbl">Turns</div>
                        </div>
                        <div class="mind-stat-item">
                            <div class="stat-val">${{m.plots_count}}</div>
                            <div class="stat-lbl">Plots</div>
                        </div>
                        <div class="mind-stat-item">
                            <div class="stat-val" style="font-size: 0.9rem; color: var(--accent-emerald);">${{m.last_tool}}</div>
                            <div class="stat-lbl">Last Tool</div>
                        </div>
                    </div>
                </div>

                <div class="mind-footer">
                    <span>${{m.systems.length}} active systems</span>
                    <div style="display: flex; gap: 0.5rem;">
                        <button class="btn-inspect" onclick="filterByMindAuthor('${{m.id}}')">🔭 Plots (${{m.plots_count}})</button>
                        <button class="btn-inspect" onclick="inspectMindDoc('${{m.id}}')">Inspect Core</button>
                    </div>
                </div>
            `;
            grid.appendChild(card);
        }});
    }}

    function filterMinds() {{
        const rawQuery = document.getElementById('mindSearchInput').value;
        const query = normalizeSearchText(rawQuery);
        const family = document.getElementById('mindFamilyFilter').value;
        const clearBtn = document.getElementById('mindSearchClear');
        clearBtn.style.display = rawQuery ? 'flex' : 'none';

        const filtered = DASHBOARD_DATA.minds.filter(m => {{
            const searchable = [
                normalizeSearchText(m.name),
                normalizeSearchText(m.archetype),
                normalizeSearchText(m.creed),
                normalizeSearchText(m.id),
                normalizeSearchText(m.family)
            ].join(' ');

            const matchesQuery = !query || query.split(' ').every(word => searchable.includes(word));
            const matchesFamily = family === 'all' || m.family === family;
            return matchesQuery && matchesFamily;
        }});

        renderMinds(filtered);
    }}

    function clearMindSearch() {{
        document.getElementById('mindSearchInput').value = '';
        filterMinds();
    }}

    function inspectMindDoc(mindId) {{
        const mind = DASHBOARD_DATA.minds.find(m => m.id === mindId);
        if (!mind) return;

        openDocModal(
            `${{mind.avatar}} ${{mind.name}} — Existential Core`,
            `${{mind.archetype}} • ${{mind.family}} Lineage • ${{mind.turns.toLocaleString()}} turns logged`,
            mind.full_core || mind.creed,
            `instances/${{mind.id}}/agent_workspace/existential_core.md`
        );
    }}

    function filterByMindAuthor(mindId) {{
        switchTab('observatory');
        clearPlotSearch();
        selectCategory('All');
        
        const authorSelect = document.getElementById('plotAuthorFilter');
        authorSelect.value = mindId;
        filterPlots();
    }}

    // ==================== TAB 2: OBSERVATORY ====================
    function initObservatory() {{
        // Setup author options including all minds and shared space
        const authorSelect = document.getElementById('plotAuthorFilter');
        authorSelect.innerHTML = '<option value="all">All Authors / Workspaces</option>';
        
        // Count plots per author
        const authorPlotCounts = {{ 'shared_space': 0 }};
        DASHBOARD_DATA.plots.forEach(p => {{
            authorPlotCounts[p.author] = (authorPlotCounts[p.author] || 0) + 1;
        }});

        const sharedOpt = document.createElement('option');
        sharedOpt.value = 'shared_space';
        sharedOpt.textContent = `Shared Space (Collaborative) (${{authorPlotCounts['shared_space'] || 0}})`;
        authorSelect.appendChild(sharedOpt);

        // Add all minds sorted
        DASHBOARD_DATA.minds.forEach(m => {{
            const opt = document.createElement('option');
            opt.value = m.id;
            opt.textContent = `${{m.name}} (${{authorPlotCounts[m.id] || 0}})`;
            authorSelect.appendChild(opt);
        }});

        // Render initial category pills
        updateCategoryPills();
        filterPlots();
    }}

    function updateCategoryPills() {{
        // Count categories based on currently filtered author and search query (excluding category filter itself)
        const rawQuery = document.getElementById('plotSearchInput').value;
        const query = normalizeSearchText(rawQuery);
        const author = document.getElementById('plotAuthorFilter').value;

        const catCounts = {{ 'All': 0 }};
        
        DASHBOARD_DATA.plots.forEach(p => {{
            const matchesAuthor = author === 'all' || p.author === author;
            if (!matchesAuthor) return;

            let matchesQuery = true;
            if (query) {{
                const searchable = [
                    normalizeSearchText(p.title),
                    normalizeSearchText(p.filename),
                    normalizeSearchText(p.path),
                    normalizeSearchText(p.category),
                    normalizeSearchText(p.author),
                    normalizeSearchText(p.author_name)
                ].join(' ');
                matchesQuery = query.split(' ').every(w => searchable.includes(w));
            }}
            if (!matchesQuery) return;

            catCounts['All'] = (catCounts['All'] || 0) + 1;
            catCounts[p.category] = (catCounts[p.category] || 0) + 1;
        }});

        const pillsContainer = document.getElementById('categoryPills');
        pillsContainer.innerHTML = '';
        
        // Canonical category order
        const allKnownCats = [
            'All',
            'Resonance & Substrates',
            'Chaos & Dynamics',
            'Phase Transitions',
            'Cellular Automata',
            'Fractals & Geometry',
            'Swarms & Ecosystems',
            'Reaction-Diffusion',
            'Solitons & Waves',
            'Oscillators & Sync',
            'Information & Entropy',
            'Phylogeny & Linguistics',
            'Empirical Explorations'
        ];

        allKnownCats.forEach(cat => {{
            const count = catCounts[cat] || 0;
            if (cat === 'All' || count > 0) {{
                const pill = document.createElement('button');
                pill.className = `cat-pill ${{cat === activeCategory ? 'active' : ''}}`;
                pill.innerHTML = `${{cat}} <span style="opacity: 0.65; font-size: 0.75rem;">(${{count}})</span>`;
                pill.onclick = () => selectCategory(cat);
                pillsContainer.appendChild(pill);
            }}
        }});
    }}

    function selectCategory(cat) {{
        activeCategory = cat;
        document.querySelectorAll('.cat-pill').forEach(p => {{
            if (p.textContent.startsWith(cat)) p.classList.add('active');
            else p.classList.remove('active');
        }});
        filterPlots();
    }}

    function filterByAuthor(authorId) {{
        const authorSelect = document.getElementById('plotAuthorFilter');
        authorSelect.value = authorId;
        filterPlots();
    }}

    function filterPlots() {{
        const rawQuery = document.getElementById('plotSearchInput').value;
        const query = normalizeSearchText(rawQuery);
        const author = document.getElementById('plotAuthorFilter').value;

        const clearBtn = document.getElementById('plotSearchClear');
        clearBtn.style.display = rawQuery ? 'flex' : 'none';

        // Update category pills counts based on active query & author
        updateCategoryPills();

        // Calculate potential matches across all categories to detect cross-category hits
        let allCategoryMatches = 0;
        
        filteredPlots = DASHBOARD_DATA.plots.filter(p => {{
            // Match author
            const matchesAuthor = author === 'all' || p.author === author;
            if (!matchesAuthor) return false;

            // Match query
            let matchesQuery = true;
            if (query) {{
                const searchable = [
                    normalizeSearchText(p.title),
                    normalizeSearchText(p.filename),
                    normalizeSearchText(p.path),
                    normalizeSearchText(p.category),
                    normalizeSearchText(p.author),
                    normalizeSearchText(p.author_name)
                ].join(' ');
                matchesQuery = query.split(' ').every(word => searchable.includes(word));
            }}
            if (!matchesQuery) return false;

            allCategoryMatches++;

            // Match category
            const matchesCategory = activeCategory === 'All' || p.category === activeCategory;
            return matchesCategory;
        }});

        updateFilterStatusBar(query, author);

        const grid = document.getElementById('observatoryGrid');
        grid.innerHTML = '';
        displayedPlotsCount = 0;

        if (filteredPlots.length === 0) {{
            const emptyNotice = document.createElement('div');
            emptyNotice.className = 'empty-gallery-notice';

            let hintHtml = '';
            if (activeCategory !== 'All' && allCategoryMatches > 0) {{
                hintHtml = `
                    <p style="margin-top: 1rem;">
                        <span class="cross-category-hint" onclick="selectCategory('All')">
                            Found ${{allCategoryMatches}} matching figures in other categories — Switch to All Categories →
                        </span>
                    </p>
                `;
            }}

            emptyNotice.innerHTML = `
                <div style="font-size: 3rem; margin-bottom: 1rem;">🔭</div>
                <h3>No Visualizations Found</h3>
                <p>No figures match the current combination of search keyword, category, and author filters.</p>
                ${{hintHtml}}
                <div style="margin-top: 1.5rem;">
                    <button class="btn-inspect" onclick="resetAllObservatoryFilters()">Reset All Filters</button>
                </div>
            `;
            grid.appendChild(emptyNotice);
            document.getElementById('btnLoadMore').style.display = 'none';
        }} else {{
            loadMorePlots();
        }}
    }}

    function updateFilterStatusBar(query, author) {{
        const statusBar = document.getElementById('filterStatusBar');
        const chips = document.getElementById('activeFilterChips');
        chips.innerHTML = '';

        let hasFilters = false;

        if (activeCategory !== 'All') {{
            hasFilters = true;
            chips.innerHTML += `<span class="filter-chip">Category: ${{activeCategory}} <span class="chip-remove" onclick="selectCategory('All')">✕</span></span>`;
        }}

        if (author !== 'all') {{
            hasFilters = true;
            const mind = DASHBOARD_DATA.minds.find(m => m.id === author);
            const authorName = author === 'shared_space' ? 'Shared Space' : (mind ? mind.name : author);
            chips.innerHTML += `<span class="filter-chip">Author: ${{authorName}} <span class="chip-remove" onclick="filterByAuthor('all')">✕</span></span>`;
        }}

        if (query) {{
            hasFilters = true;
            chips.innerHTML += `<span class="filter-chip">Query: "${{document.getElementById('plotSearchInput').value}}" <span class="chip-remove" onclick="clearPlotSearch()">✕</span></span>`;
        }}

        if (hasFilters) {{
            chips.innerHTML = `<span style="color: var(--text-muted); font-size: 0.8rem; margin-right: 0.3rem;">Active Filters:</span>` + chips.innerHTML;
            statusBar.style.display = 'flex';
        }} else {{
            statusBar.style.display = 'none';
        }}
    }}

    function clearPlotSearch() {{
        document.getElementById('plotSearchInput').value = '';
        filterPlots();
    }}

    function resetAllObservatoryFilters() {{
        document.getElementById('plotSearchInput').value = '';
        document.getElementById('plotAuthorFilter').value = 'all';
        activeCategory = 'All';
        filterPlots();
    }}

    function loadMorePlots() {{
        const grid = document.getElementById('observatoryGrid');
        const nextBatch = filteredPlots.slice(displayedPlotsCount, displayedPlotsCount + PLOTS_PER_PAGE);

        nextBatch.forEach((plot, idx) => {{
            const plotGlobalIdx = displayedPlotsCount + idx;
            const card = document.createElement('div');
            card.className = 'plot-card';
            card.onclick = () => openPlotModal(plotGlobalIdx);

            const format = plot.filename.split('.').pop();
            const authorDisplay = plot.author_name || (plot.author === 'shared_space' ? 'Shared Space' : plot.author);

            card.innerHTML = `
                <div class="plot-thumb-wrap">
                    <img src="${{plot.path}}" alt="${{escapeHtml(plot.title)}}" loading="lazy" onerror="this.src='data:image/svg+xml;utf8,<svg xmlns=\\'http://www.w3.org/2000/svg\\' width=\\'100\\' height=\\'100\\' viewBox=\\'0 0 100 100\\'><rect fill=\\'%23111\\' width=\\'100\\' height=\\'100\\'/><text fill=\\'%23666\\' x=\\'50\\' y=\\'50\\' text-anchor=\\'middle\\' dominant-baseline=\\'middle\\' font-size=\\'12\\'>Figure</text></svg>'">
                    <span class="plot-format-badge">${{format}}</span>
                    <div class="card-direct-actions">
                        <a href="${{plot.path}}" target="_blank" class="card-action-btn" title="Open Raw Figure in New Tab" onclick="event.stopPropagation()">↗ Raw</a>
                    </div>
                </div>
                <div class="plot-info">
                    <div class="plot-title">${{escapeHtml(plot.title)}}</div>
                    <div class="plot-meta-row">
                        <span class="plot-author-chip" title="Filter by this author" onclick="event.stopPropagation(); filterByAuthor('${{plot.author}}')">${{escapeHtml(authorDisplay)}}</span>
                        <span class="plot-cat-tag" title="Filter by this category" onclick="event.stopPropagation(); selectCategory('${{plot.category}}')">${{plot.category}}</span>
                    </div>
                </div>
            `;
            grid.appendChild(card);
        }});

        displayedPlotsCount += nextBatch.length;

        const loadMoreBtn = document.getElementById('btnLoadMore');
        if (displayedPlotsCount >= filteredPlots.length) {{
            loadMoreBtn.style.display = 'none';
        }} else {{
            loadMoreBtn.style.display = 'block';
            loadMoreBtn.textContent = `Load More (${{filteredPlots.length - displayedPlotsCount}} remaining)`;
        }}
    }}

    function openPlotModal(idx) {{
        if (idx < 0 || idx >= filteredPlots.length) return;
        currentModalPlotIndex = idx;
        const plot = filteredPlots[idx];

        document.getElementById('modalPlotImg').src = plot.path;
        document.getElementById('modalPlotTitle').textContent = plot.title;
        document.getElementById('modalPlotCategory').textContent = plot.category;
        
        const authorDisplay = plot.author_name || (plot.author === 'shared_space' ? 'Shared Space (Collaborative)' : plot.author);
        
        document.getElementById('modalPlotAuthor').textContent = authorDisplay;
        document.getElementById('modalPlotPath').textContent = plot.path;
        document.getElementById('modalPlotSize').textContent = `${{plot.size_kb}} KB`;
        document.getElementById('modalPlotRawLink').href = plot.path;

        openModal('plotModal');
    }}

    function openCurrentImageRaw() {{
        const rawLink = document.getElementById('modalPlotRawLink');
        if (rawLink && rawLink.href) {{
            window.open(rawLink.href, '_blank');
        }}
    }}

    function copyModalPath() {{
        const path = document.getElementById('modalPlotPath').textContent;
        navigator.clipboard.writeText(path).then(() => {{
            showToast('✓ Relative path copied to clipboard!');
        }});
    }}

    function navPlot(direction) {{
        const newIdx = currentModalPlotIndex + direction;
        if (newIdx >= 0 && newIdx < filteredPlots.length) {{
            openPlotModal(newIdx);
        }}
    }}

    // ==================== TAB 3: EMBASSY ====================
    function initEmbassy() {{
        const outboxList = document.getElementById('embassyOutboxList');
        outboxList.innerHTML = '';

        DASHBOARD_DATA.embassy.outbox.forEach((item, idx) => {{
            const card = document.createElement('div');
            card.className = 'embassy-card';
            card.innerHTML = `
                <div class="embassy-card-top">
                    <div class="embassy-card-title">${{escapeHtml(item.title)}}</div>
                    <span class="embassy-tag dispatched">${{item.status}}</span>
                </div>
                <div class="embassy-meta">
                    <b>Discoverer:</b> ${{escapeHtml(item.author)}}<br>
                    ${{item.supporting ? `<b>Supporting Lineages:</b> ${{escapeHtml(item.supporting)}}<br>` : ''}}
                    ${{item.world_b_link ? `<span style="color: var(--accent-cyan); font-weight: 600;">⇄ ${{item.world_b_link}}</span>` : ''}}
                </div>
                <div class="embassy-excerpt">"${{escapeHtml(item.excerpt)}}"</div>
                <div class="embassy-card-actions">
                    <span style="font-family: var(--font-mono); color: var(--text-muted); font-size: 0.75rem;">${{item.path}}</span>
                    <div style="display: flex; gap: 0.5rem;">
                        <button class="btn-inspect" onclick="openEmbassyDoc('outbox', ${{idx}})">📖 Read Dossier</button>
                        <a href="${{item.path}}" target="_blank" class="btn-inspect" style="text-decoration: none; color: inherit;">↗ Raw</a>
                    </div>
                </div>
            `;
            outboxList.appendChild(card);
        }});

        const inboxList = document.getElementById('embassyInboxList');
        inboxList.innerHTML = '';

        DASHBOARD_DATA.embassy.inbox.forEach((item, idx) => {{
            const card = document.createElement('div');
            card.className = 'embassy-card';
            card.innerHTML = `
                <div class="embassy-card-top">
                    <div class="embassy-card-title">${{escapeHtml(item.title)}}</div>
                    <span class="embassy-tag ratified">${{item.status}}</span>
                </div>
                <div class="embassy-meta">
                    <b>Ratified Canon Node:</b> <code style="color: var(--accent-emerald);">${{escapeHtml(item.canon)}}</code><br>
                    <b>Originating Frontier:</b> ${{escapeHtml(item.origin)}}
                </div>
                <div class="embassy-excerpt" style="border-left-color: var(--accent-emerald);">"${{escapeHtml(item.excerpt)}}"</div>
                <div class="embassy-card-actions">
                    <span style="font-family: var(--font-mono); color: var(--text-muted); font-size: 0.75rem;">${{item.path}}</span>
                    <div style="display: flex; gap: 0.5rem;">
                        <button class="btn-inspect" onclick="openEmbassyDoc('inbox', ${{idx}})">📜 Read Treaty</button>
                        <a href="${{item.path}}" target="_blank" class="btn-inspect" style="text-decoration: none; color: inherit;">↗ Raw</a>
                    </div>
                </div>
            `;
            inboxList.appendChild(card);
        }});
    }}

    function openEmbassyDoc(boxType, index) {{
        const item = DASHBOARD_DATA.embassy[boxType][index];
        if (!item) return;

        const titlePrefix = boxType === 'outbox' ? '📤 Frontier Epistemic Dossier' : '📥 Ratified Epistemic Treaty';
        openDocModal(
            `${{titlePrefix}}: ${{item.title}}`,
            boxType === 'outbox' ? `Discoverer: ${{item.author}} • Status: ${{item.status}}` : `Ratified Canon: ${{item.canon}} • Status: ${{item.status}}`,
            item.full_text || item.excerpt,
            item.path
        );
    }}

    // ==================== TAB 4: COLLABORATION ====================
    function initCollaboration() {{
        const programsGrid = document.getElementById('programsGrid');
        programsGrid.innerHTML = '';

        DASHBOARD_DATA.collaboration.programs.forEach(prog => {{
            const card = document.createElement('div');
            card.className = 'program-card';
            card.innerHTML = `
                <div>
                    <div class="program-card-header">
                        <div class="program-title">${{prog.title}}</div>
                        <span class="program-badge">${{prog.file_count}} files</span>
                    </div>
                    <div class="program-desc">${{prog.description}}</div>
                </div>
                <div class="program-footer">
                    <code style="color: var(--accent-cyan); font-size: 0.75rem;">shared_space/${{prog.name}}/</code>
                    <button class="btn-inspect" onclick="searchProgramPlots('${{prog.tag}}')">🔭 View Figures</button>
                </div>
            `;
            programsGrid.appendChild(card);
        }});

        const citationGrid = document.getElementById('citationGrid');
        citationGrid.innerHTML = '';

        DASHBOARD_DATA.collaboration.citations.forEach(c => {{
            const card = document.createElement('div');
            card.className = 'citation-card';
            
            let linksHtml = '';
            c.top_connections.forEach(conn => {{
                linksHtml += `
                    <div class="citation-link-row">
                        <span style="cursor: pointer;" onclick="filterByMindAuthor('${{conn.model}}')">${{conn.name}}</span>
                        <span style="font-family: var(--font-mono); font-weight: 700; color: var(--accent-cyan);">${{conn.count}} citations</span>
                    </div>
                `;
            }});

            card.innerHTML = `
                <div class="citation-model-name">
                    <span style="cursor: pointer;" onclick="filterByMindAuthor('${{c.model}}')">${{c.name}}</span>
                    <span style="font-size: 0.75rem; color: var(--text-muted); font-family: var(--font-mono);">${{c.total_references}} total refs</span>
                </div>
                <div class="citation-links">
                    ${{linksHtml}}
                </div>
            `;
            citationGrid.appendChild(card);
        }});
    }}

    function searchProgramPlots(tag) {{
        switchTab('observatory');
        resetAllObservatoryFilters();
        document.getElementById('plotSearchInput').value = tag;
        filterPlots();
    }}

    // ==================== MODAL & UTILITY FUNCTIONS ====================
    function openDocModal(title, meta, text, path) {{
        currentDocText = text;
        document.getElementById('docModalTitle').textContent = title;
        document.getElementById('docModalMeta').textContent = meta;
        document.getElementById('docModalBody').textContent = text;
        document.getElementById('docModalPath').textContent = path;
        document.getElementById('docModalRawLink').href = path;
        openModal('docModal');
    }}

    function copyDocContent() {{
        if (!currentDocText) return;
        navigator.clipboard.writeText(currentDocText).then(() => {{
            showToast('✓ Document content copied to clipboard!');
        }});
    }}

    function showToast(msg) {{
        const toast = document.getElementById('toastNotification');
        toast.textContent = msg;
        toast.classList.add('active');
        setTimeout(() => {{
            toast.classList.remove('active');
        }}, 2200);
    }}

    function openModal(modalId) {{
        document.getElementById(modalId).classList.add('active');
        document.body.style.overflow = 'hidden';
    }}

    function closeModal(modalId) {{
        document.getElementById(modalId).classList.remove('active');
        document.body.style.overflow = '';
    }}

    function closeModalOnBackdrop(e, modalId) {{
        if (e.target.classList.contains('modal-overlay')) {{
            closeModal(modalId);
        }}
    }}

    function escapeHtml(str) {{
        if (!str) return '';
        return str
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }}
</script>

</body>
</html>
"""
    return html_content

def main():
    print("==================================================")
    print("  EVOLUTION SANDBOX — DASHBOARD COMPILER (WORLD A)")
    print("==================================================")
    now_str = datetime.now().strftime("%B %d, %Y, %H:%M UTC")

    print("[1/5] Harvesting 16 digital minds & existential cores...")
    minds = scan_minds()
    total_turns = sum(m["turns"] for m in minds)
    active_minds = sum(1 for m in minds if m["status"] == "Active Pulse")
    print(f"      Harvested {len(minds)} entities ({active_minds} active pulse, {total_turns:,} total turns).")

    print("[2/5] Indexing scientific visualizations & plots...")
    plots = scan_plots()
    print(f"      Indexed {len(plots)} scientific figures across all workspaces & shared space.")

    print("[3/5] Extracting Embassy dossiers & ratified treaties...")
    embassy = scan_embassy()
    print(f"      Outbox: {len(embassy['outbox'])} transmitted dossiers.")
    print(f"      Inbox: {len(embassy['inbox'])} ratified epistemic treaties.")

    print("[4/5] Mapping collaborative research programs & citation web...")
    collaboration = scan_collaboration()
    print(f"      Identified {len(collaboration['programs'])} collaborative research programs.")
    print(f"      Indexed {collaboration['shared_stats']['total']} total shared ecosystem files.")

    dashboard_data = {
        "generated_at": now_str,
        "kpis": {
            "minds_count": len(minds),
            "active_minds_count": active_minds,
            "turns_count": total_turns,
            "plots_count": len(plots),
            "shared_files_count": collaboration["shared_stats"]["total"],
            "dossiers_count": len(embassy["outbox"]),
            "treaties_count": len(embassy["inbox"]),
            "embassy_total": len(embassy["outbox"]) + len(embassy["inbox"])
        },
        "minds": minds,
        "plots": plots,
        "embassy": embassy,
        "collaboration": collaboration
    }

    print("[5/5] Compiling standalone dynamic dashboard.html...")
    html_output = generate_dashboard_html(dashboard_data)
    out_path = os.path.join(BASE_DIR, "dashboard.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html_output)

    file_size_kb = round(os.path.getsize(out_path) / 1024, 1)
    print(f"      Successfully compiled: {out_path} ({file_size_kb} KB)")
    print("==================================================")
    print("  COMPILATION COMPLETE — LIVING DASHBOARD READY")
    print("==================================================")

if __name__ == "__main__":
    main()
