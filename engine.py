import os
import sys
import io
import time
import argparse
import json


# Force stdout/stderr to use UTF-8 and gracefully handle unprintable characters on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from llm_client import generate_next_action
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
                        arg_canon = json.dumps(arguments, sort_keys=True, ensure_ascii=False) if isinstance(arguments, dict) else str(arguments)
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
                        if tool_name == "run_command" and prev_timed_out:
                            result = (
                                "Error: This exact command ALREADY timed out in a previous turn. "
                                "Do NOT re-run the same timed-out command locally — either optimize/vectorize the script, "
                                "reduce grid/step counts, or offload heavy sweeps to World C via 'submit_world_c_job'."
                            )
                        elif tool_name == "read_chat" and repeat_read_count >= 2:
                            result = (
                                "Notice: You ALREADY called 'read_chat' with these exact arguments in a recent turn and the messages "
                                "are already in your context above. Do NOT call 'read_chat' again — proceed immediately to a concrete "
                                "action (submit_world_c_job, write_file, edit_file, run_command, or post_chat)."
                            )
                        else:
                            result = AVAILABLE_TOOLS[tool_name](**arguments)
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
