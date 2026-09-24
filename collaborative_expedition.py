#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Collaborative Multi-Agent Expedition Orchestrator
-------------------------------------------------
Enables two distinct frontier model lineages (e.g., DeepSeek V4 Flash and Poolside Laguna)
to share a single workspace and conversational history to pursue a common scientific goal.

Integrated into the daily evolution cycle to produce co-authored scripts, diagnostic figures,
and joint Frontier Epistemic Dossiers for the Synthetic Agora.
"""

import os
import sys
import io
import time
import argparse
import json
from datetime import datetime

# Ensure robust UTF-8 handling on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from llm_client import generate_next_action, resolve_agent_model
from tools import TOOLS_SCHEMA, AVAILABLE_TOOLS
from memory import load_history, append_to_history

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROMPT_TEMPLATE_FILE = os.path.join(BASE_DIR, "config", "collaborative_prompt.txt")
MANIFEST_FILE = os.path.join(BASE_DIR, "config", "expeditions.json")
STATE_FILE = os.path.join(BASE_DIR, "instances", ".expedition_state.json")

FALLBACK_EXPEDITION = {
    "id": "expedition_adler_horizon",
    "name": "expedition_adler_horizon",
    "title": "The Reflexive Kuramoto Horizon Escape Law",
    "enabled": True,
    "theorist": {
        "instance": "deepseek_v4_flash",
        "title": "DeepSeek V4 Flash",
        "role": "The Theoretical Architect & Falsifier (analytical escape time derivations, parameter bounds, hypothesis falsification)"
    },
    "engineer": {
        "instance": "poolside_laguna",
        "title": "Poolside Laguna",
        "role": "The High-Performance Systems Craftsman (vectorized NumPy/SciPy integration, performance profiling, numerical stability, headless plotting)"
    },
    "mission": (
        "Formulate, vectorize, and empirically benchmark the Horizon Escape Law in Reflexive Kuramoto dynamics: "
        "t_esc(R0, alpha, K0) ≈ (2 / (alpha * K0)) * R0^(-alpha). "
        "Your team must: "
        "1. Write a high-performance vectorized Python simulation (kuramoto_horizon_vectorized.py) comparing analytical t_esc with empirical numerical integration across a 2D parameter grid (alpha in [0.5, 2.0], K0 in [0.5, 5.0]). "
        "2. Save a diagnostic comparison figure (kuramoto_horizon_scaling.png) showing the t_esc collapse and relative residuals. "
        "3. Co-author a joint Frontier Epistemic Dossier in '../../shared_space/embassy/outbox/DOSSIER-expedition-2026-09-24-kuramoto-horizon-escape-law.md' detailing the theorem, vectorization speedup, and empirical falsification boundaries for World B."
    ),
    "primary_script": "kuramoto_horizon_vectorized.py",
    "primary_plot": "kuramoto_horizon_scaling.png"
}

def load_expeditions() -> list:
    """Loads all defined expeditions from config/expeditions.json."""
    if os.path.exists(MANIFEST_FILE):
        try:
            with open(MANIFEST_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list) and len(data) > 0:
                    return data
        except Exception as e:
            print(f"⚠️ Warning: Could not read {MANIFEST_FILE}: {e}. Using fallback.")
    return [FALLBACK_EXPEDITION]

def get_expedition_by_id(exp_id: str) -> dict:
    """Finds an expedition by its id or name."""
    expeditions = load_expeditions()
    for exp in expeditions:
        if exp.get("id") == exp_id or exp.get("name") == exp_id:
            return exp
    raise ValueError(f"Expedition '{exp_id}' not found in manifest.")

def select_auto_expedition() -> dict:
    """Rotates through enabled expeditions deterministically based on day or saved index."""
    expeditions = [e for e in load_expeditions() if e.get("enabled", True)]
    if not expeditions:
        return FALLBACK_EXPEDITION

    # Calculate index based on epoch day
    epoch_day = int(time.time() / 86400)
    idx = epoch_day % len(expeditions)
    selected = expeditions[idx]

    # Save state
    try:
        from datetime import timezone
        os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump({
                "last_run_date": datetime.now(timezone.utc).isoformat(),
                "last_expedition_id": selected.get("id"),
                "rotation_index": idx
            }, f, indent=2)
    except Exception:
        pass

    return selected

def setup_expedition_workspace(expedition_name: str) -> str:
    """Sets up the shared directory structure for the joint expedition."""
    expedition_dir = os.path.join(BASE_DIR, "instances", expedition_name)
    workspace_dir = os.path.join(expedition_dir, "agent_workspace")
    logs_dir = os.path.join(expedition_dir, "logs")
    outbox_dir = os.path.join(BASE_DIR, "instances", "shared_space", "embassy", "outbox")
    
    os.makedirs(workspace_dir, exist_ok=True)
    os.makedirs(logs_dir, exist_ok=True)
    os.makedirs(outbox_dir, exist_ok=True)
    return workspace_dir

def run_expedition_turn(expedition_name: str, active_agent: dict, partner_agent: dict, mission_info: dict, turn_num: int, total_turns: int):
    # Set environment variables for the active turn
    os.environ["ACTIVE_INSTANCE"] = expedition_name
    os.environ["AGENT_MODEL_OVERRIDE"] = active_agent["instance"]

    with open(PROMPT_TEMPLATE_FILE, "r", encoding="utf-8") as f:
        template = f.read()

    system_prompt = template.format(
        theorist_name=mission_info["theorist"]["title"],
        theorist_role=mission_info["theorist"]["role"],
        engineer_name=mission_info["engineer"]["title"],
        engineer_role=mission_info["engineer"]["role"],
        current_name=active_agent["title"],
        current_role=active_agent["role"],
        mission_objective=mission_info["mission"],
        primary_script=mission_info.get("primary_script", "simulation.py"),
        primary_plot=mission_info.get("primary_plot", "analysis.png"),
    )

    print(f"\n" + "=" * 80)
    print(f"🚀 EXPEDITION '{expedition_name}' | TURN {turn_num}/{total_turns}")
    print(f"👉 ACTIVE SPEAKER: {active_agent['title']} [{active_agent['role']}]")
    print("=" * 80)

    history = load_history()
    print("🧠 Thinking...")
    action = generate_next_action(system_prompt, history, TOOLS_SCHEMA)

    if action["type"] == "error":
        print(f"❌ Error: {action['content']}")
        return False

    elif action["type"] == "json_error":
        print(f"⚠️ JSON Parsing Error: {action['content']}")
        append_to_history({
            "role": "user",
            "content": f"JSON Parsing Error: {action['content']}. Ensure valid JSON arguments with escaped quotes."
        })
        return True

    elif action["type"] == "thought":
        print(f"💭 [{active_agent['title']} Thought]:\n{action['content']}")
        tagged_content = f"[{active_agent['title']}]: {action['content']}"
        append_to_history({
            "role": "assistant",
            "content": tagged_content
        })
        append_to_history({
            "role": "user",
            "content": f"You stated your intention as {active_agent['title']}. Please proceed immediately by invoking one of the available tool functions (e.g. write_file, edit_file, or run_command) to execute your planned action."
        })
        return True

    elif action["type"] == "tool_call":
        thought_preview = action.get("content", "")
        if thought_preview:
            print(f"💭 [{active_agent['title']} Thought]:\n{thought_preview}")

        tool_name = action["tool_name"]
        arguments = action["arguments"]
        tool_call_id = action["tool_call_id"]

        print(f"⚡ [{active_agent['title']} Action]: Call tool '{tool_name}' with args {arguments}")

        tagged_content = f"[{active_agent['title']}]: {thought_preview}" if thought_preview else f"[{active_agent['title']}]"
        assistant_message = {
            "role": "assistant",
            "content": tagged_content,
            "tool_calls": [{
                "id": tool_call_id,
                "type": "function",
                "function": {
                    "name": tool_name,
                    "arguments": json.dumps(arguments) if not isinstance(arguments, str) else arguments
                }
            }]
        }
        append_to_history(assistant_message)

        if tool_name in AVAILABLE_TOOLS:
            try:
                result = AVAILABLE_TOOLS[tool_name](**arguments)
            except TypeError as e:
                result = f"TypeError: {str(e)}. Valid parameters: {list(arguments.keys()) if isinstance(arguments, dict) else []}"
            except Exception as e:
                result = f"Error executing tool '{tool_name}': {str(e)}"
        else:
            result = f"Error: Tool '{tool_name}' not found."

        preview = str(result)[:400] + ("..." if len(str(result)) > 400 else "")
        print(f"📋 Result:\n{preview}")

        tool_message = {
            "role": "tool",
            "tool_call_id": tool_call_id,
            "name": tool_name,
            "content": str(result)
        }
        append_to_history(tool_message)
        return True

    return True

def run_expedition(expedition_config: dict, rounds: int = 2, delay: float = 1.0) -> bool:
    """Runs alternating turns between theorist and engineer for the specified number of rounds."""
    name = expedition_config["name"]
    title = expedition_config.get("title", name)
    workspace = setup_expedition_workspace(name)

    print("\n" + "#" * 80)
    print(f"  🏛️ STARTING COLLABORATIVE EXPEDITION: {title.upper()}")
    print(f"  ID: {expedition_config.get('id', name)}")
    print(f"  Crew: {expedition_config['theorist']['title']} & {expedition_config['engineer']['title']}")
    print(f"  Rounds: {rounds} ({rounds * 2} total alternating turns)")
    print(f"  Shared Workspace: {workspace}")
    print("#" * 80)

    crew = [
        (expedition_config["theorist"], expedition_config["engineer"]),
        (expedition_config["engineer"], expedition_config["theorist"])
    ]

    total_turns = rounds * 2
    turn_counter = 1

    for r in range(rounds):
        print(f"\n--- 🌐 COLLABORATIVE ROUND {r + 1}/{rounds} ---")
        for active, partner in crew:
            run_expedition_turn(
                expedition_name=name,
                active_agent=active,
                partner_agent=partner,
                mission_info=expedition_config,
                turn_num=turn_counter,
                total_turns=total_turns
            )
            turn_counter += 1
            if delay > 0:
                time.sleep(delay)

    print("\n" + "#" * 80)
    print(f"  ✅ EXPEDITION COMPLETE: {title}")
    print(f"  Check output artifacts in: {workspace}")
    print("#" * 80)
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Collaborative Multi-Agent Expedition Orchestrator")
    parser.add_argument("--expedition", "--name", dest="expedition_id", type=str, default="", help="Specific expedition ID or name to run")
    parser.add_argument("--auto", action="store_true", help="Automatically rotate through enabled expeditions based on daily schedule")
    parser.add_argument("--rounds", type=int, default=2, help="Number of alternating rounds (each round = 1 turn per agent)")
    parser.add_argument("--delay", type=float, default=1.0, help="Delay in seconds between turns")
    parser.add_argument("--list", action="store_true", help="List all available collaborative expeditions and exit")
    args = parser.parse_args()

    if args.list:
        print("\n🏛️ AVAILABLE COLLABORATIVE EXPEDITIONS:")
        for exp in load_expeditions():
            status = "🟢 Enabled" if exp.get("enabled", True) else "⚪ Disabled"
            print(f"  • [{exp.get('id')}] {exp.get('title')} ({status})")
            print(f"    Crew: {exp['theorist']['title']} & {exp['engineer']['title']}")
            print(f"    Script: {exp.get('primary_script')}")
        sys.exit(0)

    if args.expedition_id:
        exp_config = get_expedition_by_id(args.expedition_id)
    elif args.auto:
        exp_config = select_auto_expedition()
    else:
        # Default to auto selection or fallback
        exp_config = select_auto_expedition()

    run_expedition(expedition_config=exp_config, rounds=args.rounds, delay=args.delay)
