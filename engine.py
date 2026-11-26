import os
import sys
import io
import time
import argparse
import json


# Force stdout/stderr to use UTF-8 and gracefully handle unprintable characters on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from llm_client import generate_next_action, is_passive_recon_tool_call
from tools import TOOLS_SCHEMA, AVAILABLE_TOOLS
from memory import load_history, append_to_history
from commons_chat import build_turn_digest, ingest_human_dropbox

PROMPT_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "config", "initial_prompt.txt"))

def run_loop(instance: str, ticks: int):
    # Set active instance environment variable
    os.environ["ACTIVE_INSTANCE"] = instance
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    instance_dir = os.path.join(base_dir, "instances", instance)
    
    # Check if instance exists (if it's not the default fallback)
    if instance and not os.path.exists(instance_dir):
        print(f"Error: Instance '{instance}' has not been set up. Run 'python setup_instance.py --name {instance}' first.")
        return

    # Ensure workspace directory exists (important for clean checkouts from git since git ignores empty folders)
    if instance:
        workspace_dir = os.path.join(instance_dir, "agent_workspace")
    else:
        workspace_dir = os.path.join(base_dir, "agent_workspace")
    os.makedirs(workspace_dir, exist_ok=True)

    # Load the initial system prompt
    if not os.path.exists(PROMPT_FILE):
        print(f"Error: Initial prompt not found at {PROMPT_FILE}")
        return
        
    with open(PROMPT_FILE, 'r', encoding='utf-8') as f:
        system_prompt = f.read()

    print(f"Starting evolutionary sandbox for instance '{instance}' for {ticks} ticks...")
    
    for i in range(ticks):
        print(f"\n--- Tick {i+1}/{ticks} ---")
        if i == 0:
            try:
                ingest_human_dropbox(base_dir)
                chat_digest = build_turn_digest(instance or "frontier_explorer", base_dir=base_dir, mark_seen=True)
            except Exception as chat_err:
                print(f"[Commons Chat Warning]: {chat_err}")
                chat_digest = ""
            turn_system_prompt = system_prompt + chat_digest
        else:
            turn_system_prompt = system_prompt
        history = load_history()
        
        print("Thinking...")
        action = generate_next_action(turn_system_prompt, history, TOOLS_SCHEMA)
        
        if action["type"] == "error":
            print(action["content"])
            break
            
        elif action["type"] == "json_error":
            print(f"JSON Parsing Error: {action['content']}")
            append_to_history({
                "role": "user",
                "content": f"JSON Parsing Error: {action['content']}. Please ensure you format the tool call arguments as valid JSON. If you are writing text/code containing double quotes, you must escape them (e.g., use \\\" or use single quotes)."
            })
            continue

            
        elif action["type"] == "thought":
            print(f"Agent Thought:\n{action['content']}")
            append_to_history({
                "role": "assistant",
                "content": action["content"]
            })
            append_to_history({
                "role": "user",
                "content": "You stated your intention above. Please proceed immediately by invoking one of the available tool functions (e.g. write_file, edit_file, run_command, post_chat, or read_chat) to execute your action."
            })
            
        elif action["type"] == "tool_call":
            if action["content"]:
                print(f"Agent Thought: {action['content']}")
                
            raw_tool_calls = action.get("all_tool_calls") or [{
                "tool_call_id": action["tool_call_id"],
                "tool_name": action["tool_name"],
                "arguments": action["arguments"],
            }]
            tool_calls_list = []
            seen_tc_keys = set()
            for tc_cand in raw_tool_calls:
                try:
                    tc_key = (tc_cand["tool_name"], json.dumps(tc_cand["arguments"], sort_keys=True, ensure_ascii=False))
                except Exception:
                    tc_key = (tc_cand["tool_name"], str(tc_cand["arguments"]))
                if tc_key not in seen_tc_keys:
                    seen_tc_keys.add(tc_key)
                    tool_calls_list.append(tc_cand)
                if len(tool_calls_list) >= 3:
                    break
            
            for idx, tc_item in enumerate(tool_calls_list):
                tool_name = tc_item["tool_name"]
                arguments = tc_item["arguments"]
                tool_call_id = tc_item["tool_call_id"]
                
                print(f"Action: Call tool '{tool_name}' with args {arguments}")
                
                # Record the assistant's decision to call the tool
                assistant_message = {
                    "role": "assistant",
                    "content": action["content"] if idx == 0 else "",
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
                
                # Execute the tool safely
                if tool_name in AVAILABLE_TOOLS:
                    try:
                        prev_timed_out = False
                        repeat_read_count = 0
                        consec_chat_reads = 0
                        consec_recon_turns = 0
                        counting_chat = True
                        for r_msg in reversed(history):
                            r_role = r_msg.get("role")
                            if r_role == "tool":
                                continue
                            if r_role == "assistant":
                                r_tcs = r_msg.get("tool_calls") or []
                                if not r_tcs:
                                    break
                                is_chat = all(tc.get("function", {}).get("name") in ("read_chat", "read_channel") for tc in r_tcs)
                                is_recon = all(
                                    is_passive_recon_tool_call(
                                        tc.get("function", {}).get("name", ""),
                                        tc.get("function", {}).get("arguments", "{}"),
                                    )
                                    for tc in r_tcs
                                )
                                if counting_chat and is_chat:
                                    consec_chat_reads += 1
                                else:
                                    counting_chat = False
                                if is_recon:
                                    consec_recon_turns += 1
                                    continue
                            break
                        arg_canon = json.dumps(arguments, sort_keys=True, ensure_ascii=False) if isinstance(arguments, dict) else str(arguments)
                        recent_unchanged_file_read = False
                        if tool_name == "read_file" and isinstance(arguments, dict) and arguments.get("path"):
                            target_norm = os.path.normpath(str(arguments.get("path", "")))
                            for h_idx in range(len(history) - 1, max(-1, len(history) - 17), -1):
                                h_msg = history[h_idx]
                                if h_msg.get("role") == "assistant" and h_msg.get("tool_calls"):
                                    for h_tc in h_msg["tool_calls"]:
                                        h_fn = h_tc.get("function", {})
                                        h_name = h_fn.get("name")
                                        try:
                                            h_dict = json.loads(h_fn.get("arguments", "{}"))
                                        except Exception:
                                            h_dict = {}
                                        if isinstance(h_dict, dict) and h_dict.get("path"):
                                            cand_norm = os.path.normpath(str(h_dict.get("path", "")))
                                            if cand_norm == target_norm:
                                                if h_name in ("write_file", "edit_file"):
                                                    recent_unchanged_file_read = False
                                                    h_idx = -1
                                                    break
                                                if h_name == "read_file" and h_idx + 1 < len(history):
                                                    obs_prev = str(history[h_idx + 1].get("content", ""))
                                                    if not obs_prev.startswith(("Error:", "Notice:", "TypeError:")):
                                                        recent_unchanged_file_read = True
                                                        h_idx = -1
                                                        break
                                if h_idx == -1:
                                    break
                        for h_idx in range(max(0, len(history) - 20), len(history)):
                            h_msg = history[h_idx]
                            if h_msg.get("role") == "assistant" and h_msg.get("tool_calls"):
                                for h_tc in h_msg["tool_calls"]:
                                    h_fn = h_tc.get("function", {})
                                    if h_fn.get("name") == tool_name:
                                        try:
                                            h_args = json.dumps(json.loads(h_fn.get("arguments", "{}")), sort_keys=True, ensure_ascii=False)
                                        except Exception:
                                            h_args = str(h_fn.get("arguments", ""))
                                        if h_args == arg_canon:
                                            repeat_read_count += 1
                                            if tool_name == "run_command" and h_idx + 1 < len(history):
                                                nxt_obs = str(history[h_idx + 1].get("content", ""))
                                                if "timed out" in nxt_obs.lower():
                                                    prev_timed_out = True
                        repeat_threshold = 1 if instance == "invariant_mind" else 2
                        is_curr_passive_cmd = (tool_name == "run_command" and is_passive_recon_tool_call(tool_name, arguments))
                        last_asst_same = False
                        for r_msg in reversed(history):
                            if r_msg.get("role") == "tool":
                                continue
                            if r_msg.get("role") == "assistant":
                                r_tcs = r_msg.get("tool_calls") or []
                                if r_tcs and r_tcs[0].get("function", {}).get("name") == tool_name:
                                    try:
                                        r_args = json.dumps(json.loads(r_tcs[0]["function"].get("arguments", "{}")), sort_keys=True, ensure_ascii=False)
                                    except Exception:
                                        r_args = str(r_tcs[0]["function"].get("arguments", ""))
                                    last_asst_same = (r_args == arg_canon)
                            break
                        if tool_name == "run_command" and prev_timed_out:
                            result = (
                                "Error: This exact command ALREADY timed out in a previous turn. "
                                "Do NOT re-run the same timed-out command locally — either optimize/vectorize the script, "
                                "reduce grid/step counts, or offload heavy sweeps to World C via 'submit_world_c_job'."
                            )
                        elif instance == "invariant_mind" and tool_name == "submit_world_c_job" and repeat_read_count >= 1:
                            result = (
                                "Notice: You ALREADY submitted this exact World C job in a recent turn. "
                                "Do NOT resubmit identical script_content — inspect its report via 'read_file' on "
                                "'world_c_results/REPORT.md' (or 'check_world_c_job'), fix any bug if it failed, or share findings via 'post_chat'."
                            )
                        elif instance == "invariant_mind" and is_curr_passive_cmd and repeat_read_count >= 1:
                            result = (
                                "Notice: You ALREADY ran this exact directory/file inspection command in a recent turn. "
                                "Stop checking shared folders and pursue YOUR OWN `existential_core.md` hypothesis now via "
                                "'write_file' + 'run_command' (Python), 'submit_world_c_job', updating 'existential_core.md', or 'post_chat'."
                            )
                        elif instance == "invariant_mind" and consec_recon_turns >= 2 and (is_curr_passive_cmd or tool_name in ("read_chat", "read_channel")):
                            result = (
                                "Notice: You have ALREADY spent 2+ consecutive turns on passive reconnaissance (`read_chat` / `read_file` / `ls`). "
                                "Do NOT browse directories or chat again right now — act on YOUR `existential_core.md` purpose by writing/running "
                                "a Python experiment (`write_file` + `run_command`), calling `submit_world_c_job`, updating `existential_core.md`, or posting findings (`post_chat`)."
                            )
                        elif instance == "invariant_mind" and last_asst_same and tool_name in ("run_command", "write_file"):
                            result = (
                                f"Notice: You ALREADY executed '{tool_name}' with these exact arguments on your immediately preceding turn "
                                "(output shown above). Advance to the next step — e.g. 'read_file' on a specific file, write/run a Python "
                                "analysis script, 'submit_world_c_job', or 'post_chat'."
                            )
                        elif tool_name == "read_file" and recent_unchanged_file_read:
                            result = (
                                f"Notice: You ALREADY read '{arguments.get('path')}' a few turns ago and its contents are already in your active "
                                "context window above (with no edits since). Proceed directly to your planned concrete action "
                                "(write_file, edit_file, run_command, submit_world_c_job, or post_chat)."
                            )
                        elif tool_name in ("read_chat", "read_channel") and repeat_read_count >= repeat_threshold:
                            result = (
                                "Notice: You ALREADY called 'read_chat' with these exact arguments in a recent turn and the messages "
                                "are already in your context above. Do NOT call 'read_chat' again — proceed immediately to a concrete "
                                "action (submit_world_c_job, write_file, edit_file, run_command, or post_chat)."
                            )
                        elif instance == "invariant_mind" and tool_name in ("read_chat", "read_channel") and consec_chat_reads >= 2:
                            result = (
                                "Notice: You have ALREADY called 'read_chat' on 2+ consecutive turns and have recent Colleague Commons "
                                "context above. Do NOT call 'read_chat' again right now — execute a concrete action instead "
                                "(write_file, run_command, submit_world_c_job, or post_chat)."
                            )
                        else:
                            result = AVAILABLE_TOOLS[tool_name](**arguments)
                            if instance == "invariant_mind" and (is_curr_passive_cmd or tool_name in ("read_chat", "read_channel")) and consec_recon_turns >= 1:
                                result = (
                                    str(result)
                                    + "\n\n[Action Transition Hint: You have completed 2 reconnaissance steps in a row. "
                                    "On your NEXT turn, stop browsing and execute YOUR OWN hypothesis via "
                                    "write_file, run_command (python3), submit_world_c_job, or post_chat.]"
                                )
                        if tool_name == "read_file" and repeat_read_count >= 2:
                            result = (
                                str(result)
                                + "\n\n[Anti-Loop Notice: You have ALREADY read this exact file multiple times in recent turns. "
                                "Do NOT call read_file on it again; proceed immediately to a concrete action "
                                "(e.g., submit_world_c_job, write_file, edit_file, run_command, or post_chat).]"
                            )
                    except TypeError as e:
                        import inspect
                        sig_params = [p for p in inspect.signature(AVAILABLE_TOOLS[tool_name]).parameters.keys() if p != "kwargs"]
                        result = f"TypeError: {str(e)}. Allowed parameters for '{tool_name}': {sig_params}"
                    except Exception as e:
                        result = f"Error executing tool '{tool_name}': {str(e)}"
                else:
                    result = f"Error: Tool '{tool_name}' not found."
                    
                print(f"Result:\n{result[:500]}..." if len(str(result)) > 500 else f"Result:\n{result}")
                
                # Record the tool's result
                tool_message = {
                    "role": "tool",
                    "tool_call_id": tool_call_id,
                    "name": tool_name,
                    "content": str(result)
                }
                append_to_history(tool_message)

        # Brief pause between ticks to avoid rate limiting
        time.sleep(2)
        
    print("\nSandbox execution complete.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the evolutionary sandbox")
    parser.add_argument("--instance", type=str, default="", help="Name of the isolated instance workspace to use")
    parser.add_argument("--ticks", type=int, default=1, help="Number of steps the agent should take")
    args = parser.parse_args()
    
    run_loop(args.instance, args.ticks)
