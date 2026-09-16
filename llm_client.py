import os
import re
import json
import time
import uuid
from dotenv import load_dotenv
from litellm import completion
def prune_history(history: list, max_messages: int = 24, max_content_chars: int = 30000) -> list:
    """Limits history length, preserves the initial system prompt, deduplicates consecutive thought-only assistant messages, and truncates oversized message content."""
    if not history:
        return []

    # Preserve initial system prompt if present
    system_msg = None
    work_history = list(history)
    if work_history and work_history[0].get("role") == "system":
        system_msg = dict(work_history.pop(0))

    # Deduplicate consecutive assistant messages without tool calls to prevent thought loops
    deduped = []
    for msg in work_history:
        if msg.get("role") == "assistant" and not msg.get("tool_calls"):
            if deduped and deduped[-1].get("role") == "assistant" and not deduped[-1].get("tool_calls"):
                continue
        deduped.append(msg)

    if len(deduped) <= max_messages:
        pruned = [dict(m) for m in deduped]
    else:
        slice_start = len(deduped) - max_messages
        while slice_start < len(deduped) and deduped[slice_start].get("role") == "tool":
            slice_start += 1
        pruned = [dict(m) for m in deduped[slice_start:]]
    
    for msg in pruned:
        content = msg.get("content")
        if isinstance(content, str) and len(content) > max_content_chars:
            head = content[:15000]
            tail = content[-15000:]
            msg["content"] = f"{head}\n\n... [TRUNCATED {len(content) - 30000} CHARS OF OVERSIZED OUTPUT FOR CONTEXT WINDOW] ...\n\n{tail}"

    if pruned and pruned[-1].get("role") == "assistant" and pruned[-1].get("tool_calls"):
        pruned.pop()

    if system_msg:
        pruned.insert(0, system_msg)
    elif pruned and pruned[0].get("role") == "assistant":
        pruned.insert(0, {"role": "user", "content": "Please continue."})

    return pruned

def merge_consecutive_messages(messages: list) -> list:
    merged = []
    for msg in messages:
        if not merged:
            merged.append(msg)
            continue
        prev = merged[-1]
        if msg["role"] == prev["role"] and msg["role"] in ("assistant", "user"):
            if msg.get("content"):
                if prev.get("content"):
                    prev["content"] = prev["content"] + "\n\n" + msg["content"]
                else:
                    prev["content"] = msg["content"]
            if "tool_calls" in msg and msg["tool_calls"]:
                if "tool_calls" not in prev:
                    prev["tool_calls"] = []
                existing_ids = {tc.get("id") for tc in prev["tool_calls"]}
                for tc in msg["tool_calls"]:
                    if tc.get("id") not in existing_ids:
                        prev["tool_calls"].append(tc)
        else:
            merged.append(msg)
    return merged

def extract_fallback_tool_call(content: str) -> dict:
    """Fallback extractor for models that emit tool calls in plaintext/bracketed format
    (e.g., [search_web(query="...")] or [read_file(path="...")])."""
    if not content:
        return None

    known_tools = ["read_file", "write_file", "edit_file", "run_command", "search_web"]
    for tool_name in known_tools:
        pattern = rf"(?:\[|`|\b){tool_name}\s*\((.*?)\)(?:\]|`|\b)"
        m = re.search(pattern, content, re.DOTALL)
        if m:
            arg_str = m.group(1).strip()
            args = {}
            param_matches = re.findall(
                r'([a-zA-Z0-9_]+)\s*=\s*(?:"((?:\\.|[^"\\])*)"|\'((?:\\.|[^\'\\])*)\'|([^,\s\)]+))',
                arg_str,
                re.DOTALL,
            )
            for p_name, val_double, val_single, val_raw in param_matches:
                if val_double is not None and val_double != "":
                    try:
                        val = val_double.encode().decode("unicode_escape")
                    except Exception:
                        val = val_double
                elif val_single is not None and val_single != "":
                    try:
                        val = val_single.encode().decode("unicode_escape")
                    except Exception:
                        val = val_single
                else:
                    val = val_raw.strip()
                args[p_name] = val

            if not args and arg_str:
                try:
                    parsed = json.loads(arg_str)
                    if isinstance(parsed, dict):
                        args = parsed
                except Exception:
                    pass

            if not args and tool_name == "search_web" and arg_str:
                args = {"query": arg_str.strip('"\'')}

            if args:
                return {
                    "type": "tool_call",
                    "tool_call_id": f"fallback_{uuid.uuid4().hex[:8]}",
                    "tool_name": tool_name,
                    "arguments": args,
                    "content": content,
                }
    return None

def resolve_agent_model(instance_name: str) -> str:
    """Resolves the authentic model endpoint for a given instance."""
    # 1. Check instance-level .env override
    if instance_name:
        instance_dotenv = os.path.abspath(os.path.join(os.path.dirname(__file__), "instances", instance_name, ".env"))
        if os.path.exists(instance_dotenv):
            load_dotenv(dotenv_path=instance_dotenv, override=True)
            custom_model = os.getenv("AGENT_MODEL")
            if custom_model:
                return custom_model

    # 2. Check centralized model_routing.json mapping
    if instance_name:
        routing_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "config", "model_routing.json"))
        if os.path.exists(routing_path):
            try:
                with open(routing_path, "r", encoding="utf-8") as f:
                    routing = json.load(f)
                    if instance_name in routing:
                        return routing[instance_name]
            except Exception as e:
                print(f"Warning: Failed to load model routing file: {e}")

    # 3. Global fallback
    return os.getenv("DEFAULT_FALLBACK_MODEL", "openrouter/google/gemini-2.5-flash")

def generate_next_action(system_prompt: str, history: list, tools: list) -> dict:
    """
    Calls the LLM with the given prompt, history, and tools.
    Returns a dictionary representing the action to take.
    """
    # Load global env (e.g., API keys)
    global_dotenv = os.path.abspath(os.path.join(os.path.dirname(__file__), "config", ".env"))
    load_dotenv(dotenv_path=global_dotenv, override=False)

    instance_name = os.getenv("ACTIVE_INSTANCE", "")
    agent_model = resolve_agent_model(instance_name)

    print(f"🎯 [Sandbox Engine] Routing '{instance_name}' to -> {agent_model}")

    messages = [{"role": "system", "content": system_prompt}]
    
    # Append history to messages
    pruned = prune_history(history)
    for entry in pruned:
        msg = {
            "role": entry["role"],
            "content": entry.get("content", ""),
        }
        if entry["role"] == "assistant" and "tool_calls" in entry and entry["tool_calls"]:
            msg["tool_calls"] = []
            for tc in entry["tool_calls"]:
                func = tc.get("function", {})
                args = func.get("arguments", "{}")
                if isinstance(args, str):
                    try:
                        parsed = json.loads(args)
                        args = json.dumps(parsed)
                    except Exception:
                        pass
                else:
                    args = json.dumps(args)
                msg["tool_calls"].append({
                    "id": tc.get("id"),
                    "type": "function",
                    "function": {
                        "name": func.get("name"),
                        "arguments": args
                    }
                })
        if entry["role"] == "tool":
            msg["tool_call_id"] = entry["tool_call_id"]
            msg["name"] = entry.get("name")
        messages.append(msg)

    messages = merge_consecutive_messages(messages)

    # Detect if the preceding turn was a thought (assistant without tool calls) or user prompt following a thought
    force_tool = False
    if messages and messages[-1]["role"] == "assistant":
        force_tool = True
        messages.append({
            "role": "user",
            "content": "You stated your intention above. Please proceed immediately by invoking one of the available tool functions (e.g. write_file, edit_file, or run_command) to execute your planned action. Do not simply restate your plan."
        })
    elif messages and messages[-1]["role"] == "user" and len(messages) >= 2 and messages[-2]["role"] == "assistant" and not messages[-2].get("tool_calls"):
        force_tool = True

    chosen_tool_choice = "required" if force_tool else "auto"

    retries = 5
    for attempt in range(retries):
        try:
            try:
                response = completion(
                    model=agent_model,
                    messages=messages,
                    tools=tools,
                    tool_choice=chosen_tool_choice,
                    max_tokens=4096,
                    timeout=90,
                )
            except Exception as tc_err:
                # If provider or model doesn't support tool_choice="required", fall back to "auto"
                if chosen_tool_choice == "required":
                    response = completion(
                        model=agent_model,
                        messages=messages,
                        tools=tools,
                        tool_choice="auto",
                        max_tokens=4096,
                        timeout=90,
                    )
                else:
                    raise tc_err

            message = response.choices[0].message
            content_text = message.content or getattr(message, "reasoning_content", "") or ""

            # If the model wants to call a tool
            if message.tool_calls:
                tool_call = message.tool_calls[0]
                try:
                    arguments = json.loads(tool_call.function.arguments)
                    if isinstance(arguments, list):
                        merged_args = {}
                        for item in arguments:
                            if isinstance(item, dict):
                                merged_args.update(item)
                        arguments = merged_args if merged_args else (arguments[0] if (arguments and isinstance(arguments[0], dict)) else {})
                except Exception as json_err:
                    return {
                        "type": "json_error",
                        "content": f"JSON Decoding Error: {str(json_err)}. Received arguments string: {tool_call.function.arguments}"
                    }
                return {
                    "type": "tool_call",
                    "tool_call_id": tool_call.id,
                    "tool_name": tool_call.function.name,
                    "arguments": arguments,
                    "content": content_text
                }

            else:
                # Check for inline text tool call fallback (e.g. Meta LLaMA 4 Maverick)
                if content_text:
                    fallback = extract_fallback_tool_call(content_text)
                    if fallback:
                        return fallback

                # Model didn't call a tool, return thought or prompt nudge if content is empty
                return {
                    "type": "thought",
                    "content": content_text or "I am continuing to reflect and plan my next action."
                }
                
        except Exception as e:
            err_str = str(e).lower()
            if attempt < retries - 1 and ("rate" in err_str or "limit" in err_str or "429" in err_str or "400" in err_str or "delimit" in err_str):
                print(f"[Rate limited ({agent_model}). Sleeping 15 seconds before retry {attempt + 2}/{retries}...] ({str(e)})")
                time.sleep(15)
                continue
            return {
                "type": "error",
                "content": f"LLM Error ({agent_model}): {str(e)}"
            }
    
    return {
        "type": "error",
        "content": f"LLM Error ({agent_model}): Max retries exceeded without action."
    }
