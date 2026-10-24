import os
import sys
import re
import json
import time
import uuid
from dotenv import load_dotenv
from litellm import completion

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
def estimate_tokens(obj) -> int:
    """Accurately estimate token count of an object (message dict, list of messages, or tools schema)."""
    if not obj:
        return 0
    try:
        serialized = json.dumps(obj, ensure_ascii=False)
        return int(len(serialized) / 3.2)
    except Exception:
        return len(str(obj)) // 3

_INLINE_TOOL_RE = re.compile(
    r"(?:\[\s*(?:read_file|write_file|edit_file|run_command|search_web|submit_world_c_job|check_world_c_job|"
    r"report_issue_to_substrate|report_bug|contact_architect|post_epistemic_node|peer_verify_node|"
    r"query_epistemic_graph|send_agent_dispatch|read_agent_inbox|export_treaty_to_embassy)\s*\(|!function_call:|<tool_call>|"
    r"```(?:json)?\s*\{\s*\"(?:name|call|tool)\"\s*:)"
)

def strip_inline_tool_syntax(text: str) -> str:
    """Strips inline bracketed tool calls ([tool(...)]) and any hallucinated roleplay following the first inline call."""
    if not text or not isinstance(text, str):
        return text or ""
    m = _INLINE_TOOL_RE.search(text)
    if m:
        return text[:m.start()].strip()
    return text.strip()

def prune_history(history: list, max_messages: int = 24, max_content_chars: int = 8000, max_prompt_tokens: int = 10000) -> list:
    """Limits history length by message count and token budget. Preserves initial system prompt,
    deduplicates thoughts, truncates oversized messages, and packs backwards to guarantee context fit."""
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
        cleaned_msg = dict(msg)
        if cleaned_msg.get("role") == "assistant" and cleaned_msg.get("content"):
            cleaned_msg["content"] = strip_inline_tool_syntax(cleaned_msg["content"])
        deduped.append(cleaned_msg)

    # Truncate individual oversized messages (e.g. huge tool outputs or massive code dumps)
    for msg in deduped:
        content = msg.get("content")
        if isinstance(content, str) and len(content) > max_content_chars:
            half = max_content_chars // 2
            head = content[:half]
            tail = content[-half:]
            msg["content"] = f"{head}\n\n... [TRUNCATED {len(content) - max_content_chars} CHARS FOR CONTEXT WINDOW] ...\n\n{tail}"

    # Account for system prompt token budget
    sys_tokens = estimate_tokens(system_msg) if system_msg else 0
    effective_budget = max(2000, max_prompt_tokens - sys_tokens)

    # Pack backwards from latest turn
    selected = []
    accumulated_tokens = 0
    for msg in reversed(deduped):
        msg_tokens = estimate_tokens(msg)
        if accumulated_tokens + msg_tokens > effective_budget and len(selected) >= 2:
            break
        if len(selected) >= max_messages:
            break
        selected.append(msg)
        accumulated_tokens += msg_tokens

    selected.reverse()

    # Ensure the history slice does not start with an orphaned tool response
    while selected and selected[0].get("role") == "tool":
        selected.pop(0)

    # Avoid ending with a dangling tool_calls assistant message with no response
    if selected and selected[-1].get("role") == "assistant" and selected[-1].get("tool_calls"):
        selected.pop()

    if system_msg:
        selected.insert(0, system_msg)
    elif selected and selected[0].get("role") == "assistant":
        selected.insert(0, {"role": "user", "content": "Please continue."})

    return selected

def merge_consecutive_messages(messages: list) -> list:
    merged = []
    for msg in messages:
        if not merged:
            merged.append(msg)
            continue
        prev = merged[-1]
        if msg["role"] == prev["role"] and msg["role"] in ("assistant", "user"):
            if msg.get("content"):
                if msg["role"] == "assistant" and not prev.get("tool_calls") and not msg.get("tool_calls"):
                    # Keep only the latest thought when consecutive assistant turns had no tool calls,
                    # preventing multi-turn thought-loop repetition from conditioning future turns.
                    prev["content"] = msg["content"]
                elif prev.get("content"):
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

def format_messages_for_runpod(system_prompt: str, history: list, tools: list) -> list:
    """Serializes conversation history for the sovereign RunPod vLLM endpoint using explicit
    markdown ```json tool call blocks in assistant content and user-role tool outputs, avoiding
    vLLM Jinja <tool_call>/<|im_start|> token collisions and conditioning 100% tool execution."""
    tool_Entries = []
    if tools:
        for t in tools:
            if isinstance(t, dict) and "function" in t:
                fn = t["function"]
                params = list(fn.get("parameters", {}).get("properties", {}).keys())
                tool_Entries.append(f"{fn.get('name')}({', '.join(params)})")
    tools_summary = (
        ", ".join(tool_Entries)
        if tool_Entries
        else "run_command(command), write_file(path, content), read_file(path), edit_file(path, old_content, new_content), submit_world_c_job(title, script_content), check_world_c_job(job_id)"
    )

    sys_content = (
        system_prompt
        + f"\n\n[AVAILABLE TOOLS]: {tools_summary}\n"
        + "CRITICAL INSTRUCTION: At the end of EVERY response, you MUST invoke exactly one tool by outputting a ```json code block with \"name\" and \"arguments\", for example:\n"
        + "```json\n{\"name\": \"run_command\", \"arguments\": {\"command\": \"python3 script.py\"}}\n```"
    )
    msgs = [{"role": "system", "content": sys_content}]

    pruned = prune_history(history)
    for entry in pruned:
        role = entry.get("role")
        content = (entry.get("content") or "").strip()
        tcs = entry.get("tool_calls") or []
        if role == "assistant":
            if not tcs:
                # Skip thought-only assistant turns so in-context examples always end with a ```json tool call
                continue
            tc = tcs[0]
            func = tc.get("function", {})
            fn_name = func.get("name", "run_command")
            raw_args = func.get("arguments", "{}")
            try:
                parsed_args = json.loads(raw_args) if isinstance(raw_args, str) else raw_args
            except Exception:
                parsed_args = {}
            json_block = json.dumps({"name": fn_name, "arguments": parsed_args}, ensure_ascii=False)
            thought_part = content if content else f"Executing {fn_name}."
            msgs.append({
                "role": "assistant",
                "content": f"{thought_part}\n\n```json\n{json_block}\n```",
            })
        elif role == "tool":
            t_name = entry.get("name", "tool")
            msgs.append({
                "role": "user",
                "content": f"[Tool Output for {t_name}]:\n{content}\n\nState your brief scientific analysis and end your response with a ```json tool call block.",
            })
        elif role == "user":
            if "You stated your intention" in content:
                continue
            msgs.append({
                "role": "user",
                "content": f"{content}\n\nState your brief scientific analysis and end your response with a ```json tool call block.",
            })

    msgs = merge_consecutive_messages(msgs)
    if len(msgs) == 1 or msgs[-1]["role"] == "assistant":
        msgs.append({
            "role": "user",
            "content": "Proceed with your next scientific step and end your response with a ```json tool call block.",
        })
    return msgs

def extract_fallback_tool_call(content: str, tools: list = None) -> dict:
    """Fallback extractor for models that emit tool calls in plaintext, JSON, or bracketed format
    (e.g., !function_call:{"call": ...}, ```json {"name": ...}```, or [tool_name(path="...")])."""
    if not content:
        return None

    known_tools = set(["read_file", "write_file", "edit_file", "run_command", "search_web", "submit_world_c_job", "check_world_c_job"])
    if tools:
        for t in tools:
            if isinstance(t, dict) and "function" in t:
                fn_name = t["function"].get("name")
                if fn_name:
                    known_tools.add(fn_name)

    # 1. Check for !function_call: syntax (emitted by DeepSeek-R1 / thinking models)
    fc_idx = content.find("!function_call:")
    if fc_idx != -1:
        brace_idx = content.find("{", fc_idx)
        if brace_idx != -1:
            try:
                data, _ = json.JSONDecoder().raw_decode(content[brace_idx:])
                tool_name = data.get("call") or data.get("name")
                args = data.get("arguments", {})
                if tool_name in known_tools:
                    return {
                        "type": "tool_call",
                        "tool_call_id": f"fallback_{uuid.uuid4().hex[:8]}",
                        "tool_name": tool_name,
                        "arguments": args,
                        "content": strip_inline_tool_syntax(content[:fc_idx]),
                    }
            except Exception:
                pass

    # 1b. Check for Qwen / Hermes <tool_call>{"name": ..., "arguments": ...}</tool_call> syntax
    for m in re.finditer(r'<tool_call>\s*(\{)', content):
        brace_idx = m.start(1)
        try:
            data, _ = json.JSONDecoder().raw_decode(content[brace_idx:])
            tool_name = data.get("call") or data.get("name") or data.get("tool")
            args = data.get("arguments") or data.get("args") or {}
            if isinstance(args, str):
                args = json.loads(args)
            if tool_name in known_tools and isinstance(args, dict):
                return {
                    "type": "tool_call",
                    "tool_call_id": f"fallback_{uuid.uuid4().hex[:8]}",
                    "tool_name": tool_name,
                    "arguments": args,
                    "content": strip_inline_tool_syntax(content[:m.start()]),
                }
        except Exception:
            pass

    # 2. Check for markdown json codeblocks containing a tool call
    for m in re.finditer(r'```(?:json)?\s*(\{)', content):
        brace_idx = m.start(1)
        try:
            data, _ = json.JSONDecoder().raw_decode(content[brace_idx:])
            tool_name = data.get("call") or data.get("name") or data.get("tool")
            args = data.get("arguments") or data.get("args") or {}
            if tool_name in known_tools and isinstance(args, dict):
                return {
                    "type": "tool_call",
                    "tool_call_id": f"fallback_{uuid.uuid4().hex[:8]}",
                    "tool_name": tool_name,
                    "arguments": args,
                    "content": strip_inline_tool_syntax(content[:m.start()]),
                }
        except Exception:
            pass

    # 2b. Check for bare JSON tool call objects {"name": "<tool>", "arguments": {...}}
    for m in re.finditer(r'(\{\s*"(?:name|call|tool)"\s*:\s*"[^"]+"\s*,\s*"(?:arguments|args)"\s*:\s*\{)', content):
        brace_idx = m.start(1)
        try:
            data, _ = json.JSONDecoder().raw_decode(content[brace_idx:])
            tool_name = data.get("call") or data.get("name") or data.get("tool")
            args = data.get("arguments") or data.get("args") or {}
            if isinstance(args, str):
                args = json.loads(args)
            if tool_name in known_tools and isinstance(args, dict):
                return {
                    "type": "tool_call",
                    "tool_call_id": f"fallback_{uuid.uuid4().hex[:8]}",
                    "tool_name": tool_name,
                    "arguments": args,
                    "content": strip_inline_tool_syntax(content[:brace_idx]),
                }
        except Exception:
            pass

    # 3. Check for bracketed tool calls: [tool_name(param=val)], ordered by earliest position in text
    VALID_PARAMS = {
        "read_file": {"path", "offset", "limit", "start_line", "end_line"},
        "write_file": {"path", "content"},
        "edit_file": {"path", "old_content", "new_content"},
        "run_command": {"command"},
        "search_web": {"query"},
        "submit_world_c_job": {"title", "script_content", "timeout_seconds", "parameters", "entrypoint_code", "requirements_txt", "job_description"},
        "check_world_c_job": {"job_id"},
        "report_issue_to_substrate": {"component", "summary", "details", "suggested_fix"},
        "report_bug": {"component", "summary", "details", "suggested_fix"},
        "contact_architect": {"component", "summary", "details", "suggested_fix"},
        "post_epistemic_node": {"title", "node_type", "summary", "artifact_path", "parents", "tags", "confidence", "formal_statement", "supporting_evidence", "dependencies", "author_instance"},
        "peer_verify_node": {"node_id", "verdict", "critique_notes", "confidence", "reproduced_artifact_path", "verification_type", "replication_code", "empirical_outcome", "reproduced", "critique"},
        "query_epistemic_graph": {"node_id", "status", "tag", "node_type", "search_text", "limit", "author_family"},
        "send_agent_dispatch": {"recipient", "recipient_instance", "subject", "body", "reference_node_id", "node_id_ref", "action_requested", "content"},
        "read_agent_inbox": {"unread_only"},
        "export_treaty_to_embassy": {"node_id", "originating_dossier_filename", "treaty_id", "title", "ratified_theorems", "consensus_proof"},
    }
    REQUIRED_PARAMS = {
        "read_file": {"path"},
        "write_file": {"path", "content"},
        "edit_file": {"path", "old_content", "new_content"},
        "run_command": {"command"},
        "search_web": {"query"},
        "submit_world_c_job": {"title"},
        "check_world_c_job": {"job_id"},
        "report_issue_to_substrate": {"component", "summary", "details"},
        "report_bug": {"component", "summary", "details"},
        "contact_architect": {"component", "summary", "details"},
        "post_epistemic_node": {"title"},
        "peer_verify_node": {"node_id", "verdict"},
        "send_agent_dispatch": {"subject"},
        "export_treaty_to_embassy": {"node_id"},
    }

    candidates = []
    for tool_name in known_tools:
        pattern = rf"(?:\[|`|\b){tool_name}\s*\((.*?)\)(?:\]|`|(?=\s|$|\.|,|;))"
        for m in re.finditer(pattern, content, re.DOTALL):
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
                if tool_name in VALID_PARAMS and isinstance(args, dict):
                    args = {k: v for k, v in args.items() if k in VALID_PARAMS[tool_name]}
                    if tool_name == "write_file" and "content" not in args:
                        m_content = re.search(r'content\s*=\s*["\']*(.*)', arg_str, re.DOTALL)
                        if m_content:
                            args["content"] = m_content.group(1).rstrip(')"\' \n\t')

                req = REQUIRED_PARAMS.get(tool_name, set())
                if not args or not req.issubset(args.keys()):
                    continue

                candidates.append((m.start(), tool_name, args))

    if candidates:
        candidates.sort(key=lambda x: x[0])
        match_start, best_tool, best_args = candidates[0]
        return {
            "type": "tool_call",
            "tool_call_id": f"fallback_{uuid.uuid4().hex[:8]}",
            "tool_name": best_tool,
            "arguments": best_args,
            "content": strip_inline_tool_syntax(content[:match_start]),
        }

    # 4. Check for markdown Python code blocks or explicit natural-language execution/inspection intentions
    # (Especially for sovereign fine-tuned models like InvariantMind when running with tool_choice="auto")
    py_blocks = list(re.finditer(r"```(?:python|py)\s*\n(.*?)```", content, re.DOTALL))
    if py_blocks:
        last_block = py_blocks[-1]
        code_str = last_block.group(1).strip()
        prose_before = content[:last_block.start()].strip()
        prose_all = (prose_before + "\n" + content[last_block.end():]).strip()
        if len(code_str.splitlines()) >= 4 and any(k in code_str for k in ("import ", "from ", "def ", "print(")):
            if "submit_world_c_job" in known_tools and re.search(r"\b(?:resubmit|submit)\b[^.\n]*?\bWorld C\b", prose_all, re.IGNORECASE):
                py_files = re.findall(r"[`'\"]?([a-zA-Z0-9_./-]+\.py)[`'\"]?", prose_all)
                title_hint = py_files[0] if py_files else "InvariantMind Dynamical Invariants Simulation"
                return {
                    "type": "tool_call",
                    "tool_call_id": f"fallback_{uuid.uuid4().hex[:8]}",
                    "tool_name": "submit_world_c_job",
                    "arguments": {
                        "title": f"World C Simulation: {title_hint}",
                        "script_content": code_str + "\n",
                    },
                    "content": prose_before or "Submitting simulation script to World C.",
                }
            elif "write_file" in known_tools:
                py_files = re.findall(r"[`'\"]?([a-zA-Z0-9_./-]+\.py)[`'\"]?", prose_all)
                target_path = py_files[-1] if py_files else ("dimensional_analysis.py" if "lorenz" in code_str.lower() else "simulation_step.py")
                return {
                    "type": "tool_call",
                    "tool_call_id": f"fallback_{uuid.uuid4().hex[:8]}",
                    "tool_name": "write_file",
                    "arguments": {
                        "path": target_path,
                        "content": code_str + "\n",
                    },
                    "content": prose_before or f"Writing Python script to {target_path}.",
                }

    if "submit_world_c_job" in known_tools:
        m_sub_wc = re.search(
            r"(?:(?:I will(?: now)?|I'll(?: now)?|Let's|Now I'll)\s+(?:now\s+)?|(?:^|\n)\s*)(?:resubmit|submit)\b[^.\n]*?\bWorld C\b",
            content,
            re.IGNORECASE,
        )
        if m_sub_wc:
            py_files = re.findall(r"[`'\"]?([a-zA-Z0-9_./-]+\.py)[`'\"]?", content)
            candidate_py = py_files[0] if py_files else "dimensional_analysis.py"
            active_inst = os.getenv("ACTIVE_INSTANCE", "invariant_mind")
            base_dir = os.path.dirname(os.path.abspath(__file__))
            search_paths = [
                candidate_py,
                os.path.join(base_dir, "instances", active_inst, "agent_workspace", os.path.basename(candidate_py)),
                os.path.join(base_dir, "instances", "invariant_mind", "agent_workspace", os.path.basename(candidate_py)),
            ]
            for sp in search_paths:
                if os.path.exists(sp):
                    try:
                        with open(sp, "r", encoding="utf-8") as fp:
                            script_body = fp.read()
                        if script_body.strip():
                            return {
                                "type": "tool_call",
                                "tool_call_id": f"fallback_{uuid.uuid4().hex[:8]}",
                                "tool_name": "submit_world_c_job",
                                "arguments": {
                                    "title": f"World C Simulation: {os.path.basename(candidate_py)}",
                                    "script_content": script_body,
                                },
                                "content": content,
                            }
                    except Exception:
                        pass

    if "run_command" in known_tools:
        m_exec_py = re.search(
            r"(?:I will(?: now)?|I'll(?: now)?|Let's|Now I'll|Going to|Proceed to|^Executing|^Running)\s+(?:now\s+)?(?:execute|run|rerun)\b[^.\n]*?[`'\"]([a-zA-Z0-9_./-]+\.py)[`'\"]",
            content,
            re.IGNORECASE | re.MULTILINE,
        )
        if m_exec_py:
            script_path = m_exec_py.group(1)
            return {
                "type": "tool_call",
                "tool_call_id": f"fallback_{uuid.uuid4().hex[:8]}",
                "tool_name": "run_command",
                "arguments": {"command": f"python3 {script_path}"},
                "content": content,
            }

        m_generic_exec = re.search(
            r"(?:(?:Now I'll|Now I will|I will(?: now)?|I'll(?: now)?|Let's|I need to)\s+(?:run|execute)|(?:^|\n)\s*(?:Running|Executing|Starting))\s+the\s+(?:newly written\s+)?(validation|diagnostic|simulation(?:\s+step)?|test|analysis)\s+(?:script|process)",
            content,
            re.IGNORECASE,
        )
        if m_generic_exec:
            kind = m_generic_exec.group(1).lower()
            if "simulation step" in kind:
                cmd = "python3 simulation_step.py 2>&1 || python3 $(ls -t *.py 2>/dev/null | head -1)"
            elif kind in ("validation", "diagnostic"):
                cmd = "python3 validate_pipeline.py 2>&1 || python3 $(ls -t *.py 2>/dev/null | head -1)"
            else:
                cmd = "python3 $(ls -t *.py 2>/dev/null | head -1)"
            return {
                "type": "tool_call",
                "tool_call_id": f"fallback_{uuid.uuid4().hex[:8]}",
                "tool_name": "run_command",
                "arguments": {"command": cmd},
                "content": content,
            }

    if "read_file" in known_tools:
        m_read_file = re.search(
            r"(?:I will(?: now)?|I'll(?: now)?|Let's|Now I'll)\s+(?:proceed to\s+)?(?:review|read|inspect|examine)\b[^.\n]*?[`'\"]([a-zA-Z0-9_./-]+\.(?:py|json|md|txt|csv))[`'\"]",
            content,
            re.IGNORECASE,
        )
        if m_read_file:
            return {
                "type": "tool_call",
                "tool_call_id": f"fallback_{uuid.uuid4().hex[:8]}",
                "tool_name": "read_file",
                "arguments": {"path": m_read_file.group(1)},
                "content": content,
            }

    return None

def resolve_agent_model(instance_name: str) -> str:
    """Resolves the authentic model endpoint for a given instance."""
    # 1. Check centralized model_routing.json mapping FIRST
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

    # 2. Check instance-level .env override
    if instance_name:
        instance_dotenv = os.path.abspath(os.path.join(os.path.dirname(__file__), "instances", instance_name, ".env"))
        if os.path.exists(instance_dotenv):
            load_dotenv(dotenv_path=instance_dotenv, override=True)
            custom_model = os.getenv("AGENT_MODEL")
            if custom_model:
                return custom_model

    # 3. Global fallback
    return os.getenv("DEFAULT_FALLBACK_MODEL", "openrouter/google/gemini-2.5-flash")

def get_model_context_limits(agent_model: str) -> tuple[int, int]:
    """Returns (max_model_len, max_gen_tokens) for any model slug across World A and World B.
    Frontier/reasoning models (Tencent HY3, Kimi, DeepSeek, Claude, Gemini) receive high completion caps
    so internal chain-of-thought tokens never starve Python script generation."""
    slug = (agent_model or "").lower()

    # Sovereign Runpod endpoint (vLLM bare-metal, 16k window)
    if "runpod/" in slug or "invariantmind" in slug:
        return 16384, 4096

    # High-capacity reasoning, coding, and frontier models (64k to 1M+ context)
    # Tencent HY3 has 256k context and outputs internal chain-of-thought tokens, needing generous completion headroom
    if any(k in slug for k in [
        "tencent", "hy3", "kimi", "deepseek", "minimax", "claude", "gemini",
        "glm", "qwen", "llama-3.3", "llama-4", "mistral", "nemotron", "mimo",
        "poolside", "laguna"
    ]):
        return 65536, 8192

    # Default / smaller open-weight models (e.g. 8B models, Gemma)
    return 16384, 4096

def generate_next_action(system_prompt: str, history: list, tools: list) -> dict:
    """
    Calls the LLM with the given prompt, history, and tools.
    Returns a dictionary representing the action to take.
    """
    # Load global env (e.g., API keys)
    global_dotenv = os.path.abspath(os.path.join(os.path.dirname(__file__), "config", ".env"))
    load_dotenv(dotenv_path=global_dotenv, override=False)

    instance_name = os.getenv("ACTIVE_INSTANCE", "")
    model_override = os.getenv("AGENT_MODEL_OVERRIDE", "")
    if model_override:
        agent_model = resolve_agent_model(model_override) if not model_override.startswith("openrouter/") and "/" not in model_override else model_override
        print(f"🎯 [Sandbox Engine] Routing '{instance_name}' (via override '{model_override}') to -> {agent_model}")
    else:
        agent_model = resolve_agent_model(instance_name)
        print(f"🎯 [Sandbox Engine] Routing '{instance_name}' to -> {agent_model}")

    effective_system_prompt = system_prompt
    if agent_model.startswith("runpod/"):
        effective_system_prompt += (
            "\n\n[TOOL INVOCATION FORMAT]: Always execute your next step by invoking a tool using "
            "<tool_call>{\"name\": \"<tool_name>\", \"arguments\": {...}}</tool_call> "
            "(for example: <tool_call>{\"name\": \"run_command\", \"arguments\": {\"command\": \"python3 script.py\"}}</tool_call>)."
        )
    messages = [{"role": "system", "content": effective_system_prompt}]
    
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
    elif (
        messages
        and messages[-1]["role"] == "user"
        and "You stated your intention" in messages[-1].get("content", "")
        and len(messages) >= 2
        and messages[-2]["role"] == "assistant"
        and not messages[-2].get("tool_calls")
    ):
        force_tool = True

    chosen_tool_choice = "auto" if agent_model.startswith("runpod/") else ("required" if force_tool else "auto")

    # Accurately estimate prompt tokens including messages and tools schema
    tools_tokens = estimate_tokens(tools) if tools else 0
    msg_tokens = sum(estimate_tokens(m) for m in messages)
    est_prompt_tokens = tools_tokens + msg_tokens

    max_model_len, max_gen_tokens = get_model_context_limits(agent_model)

    # If the combined prompt tokens approach or exceed context window, perform immediate strict re-prune
    if est_prompt_tokens + 512 >= max_model_len:
        target_budget = max(3000, max_model_len - 2500 - tools_tokens)
        messages = prune_history(messages, max_messages=12, max_content_chars=4000, max_prompt_tokens=target_budget)
        messages = merge_consecutive_messages(messages)
        msg_tokens = sum(estimate_tokens(m) for m in messages)
        est_prompt_tokens = tools_tokens + msg_tokens

    # Dynamically budget max_tokens with model-specific headroom so reasoning thoughts + code never truncate
    remaining_headroom = max_model_len - est_prompt_tokens - 256
    dynamic_max_tokens = min(max_gen_tokens, max(256, remaining_headroom))

    call_kwargs = {
        "messages": messages,
        "tools": tools,
        "tool_choice": chosen_tool_choice,
        "max_tokens": dynamic_max_tokens,
        "timeout": 120,
    }

    if agent_model.startswith("runpod/"):
        runpod_api_key = os.getenv("RUNPOD_API_KEY")
        if not runpod_api_key:
            print(f"⚠️ [Sandbox Engine] RUNPOD_API_KEY not found in environment for {agent_model}. Falling back to openrouter/deepseek/deepseek-v4.1-flash.")
            call_kwargs["model"] = "openrouter/deepseek/deepseek-v4.1-flash"
        else:
            endpoint_id = os.getenv("RUNPOD_INVARIANT_ENDPOINT_ID", "nxrwj2zma759vc")
            target_model = agent_model.split("runpod/", 1)[1]
            if "/" not in target_model and len(target_model) <= 20:
                endpoint_id = target_model
                target_model = "Ninitje/InvariantMind-Worker-7B-Merged"
            call_kwargs["model"] = f"openai/{target_model}"
            call_kwargs["api_base"] = f"https://api.runpod.ai/v2/{endpoint_id}/openai/v1"
            call_kwargs["api_key"] = runpod_api_key
            call_kwargs["timeout"] = 300  # 300s deadline: allow serverless worker to cold-start cleanly without tripping timeout
            call_kwargs["num_retries"] = 0
            call_kwargs["messages"] = format_messages_for_runpod(system_prompt, history, tools)
            call_kwargs.pop("tools", None)
            call_kwargs.pop("tool_choice", None)
    else:
        call_kwargs["model"] = agent_model

    retries = 1 if agent_model.startswith("runpod/") else 5
    for attempt in range(retries):
        try:
            try:
                response = completion(**call_kwargs)
            except Exception as tc_err:
                # If provider or model doesn't support tool_choice="required", fall back to "auto"
                if call_kwargs.get("tool_choice") == "required":
                    fallback_kwargs = dict(call_kwargs)
                    fallback_kwargs["tool_choice"] = "auto"
                    response = completion(**fallback_kwargs)
                else:
                    raise tc_err

            message = response.choices[0].message
            content_text = message.content or getattr(message, "reasoning_content", "") or ""
            for tok in ("<|im_start|>", "<|im_end|>", "<|endoftext|>"):
                content_text = content_text.replace(tok, "")
            content_text = content_text.strip()

            # If the model wants to call one or more tools
            if message.tool_calls:
                parsed_calls = []
                for tc in message.tool_calls:
                    try:
                        arguments = json.loads(tc.function.arguments)
                        if isinstance(arguments, list):
                            merged_args = {}
                            for item in arguments:
                                if isinstance(item, dict):
                                    merged_args.update(item)
                            arguments = merged_args if merged_args else (arguments[0] if (arguments and isinstance(arguments[0], dict)) else {})
                        if (
                            tc.function.name == "write_file"
                            and isinstance(arguments, dict)
                            and not arguments.get("content")
                            and content_text
                        ):
                            m_cb = re.search(r"```(?:python|py|markdown|md|json|sh|bash)?\s*\n(.*?)```", content_text, re.DOTALL)
                            if m_cb and m_cb.group(1).strip():
                                arguments["content"] = m_cb.group(1).strip() + "\n"
                        parsed_calls.append({
                            "tool_call_id": tc.id,
                            "tool_name": tc.function.name,
                            "arguments": arguments if isinstance(arguments, dict) else {},
                        })
                    except Exception as json_err:
                        if not parsed_calls:
                            return {
                                "type": "json_error",
                                "content": f"JSON Decoding Error: {str(json_err)}. Received arguments string: {tc.function.arguments}"
                            }
                first = parsed_calls[0]
                return {
                    "type": "tool_call",
                    "tool_call_id": first["tool_call_id"],
                    "tool_name": first["tool_name"],
                    "arguments": first["arguments"],
                    "all_tool_calls": parsed_calls,
                    "content": content_text
                }

            else:
                # Check for inline text tool call fallback (e.g. Meta LLaMA 4 Maverick or JSON code blocks)
                if content_text:
                    fallback = extract_fallback_tool_call(content_text, tools=tools)
                    if fallback:
                        return fallback

                # Model didn't call a tool, return thought or prompt nudge if content is empty
                return {
                    "type": "thought",
                    "content": content_text or "I am continuing to reflect and plan my next action."
                }
                
        except Exception as e:
            err_str = str(e).lower()
            transient_keys = (
                "rate", "limit", "429", "500", "502", "503", "504",
                "internal server error", "server disconnected", "peer closed connection", "apiconnectionerror"
            )
            if attempt < retries - 1 and any(k in err_str for k in transient_keys):
                wait_sec = 15 if ("rate" in err_str or "429" in err_str) else 5
                print(f"[Transient API error ({agent_model}). Sleeping {wait_sec} seconds before retry {attempt + 2}/{retries}...] ({str(e)})")
                time.sleep(wait_sec)
                continue
            
            # If Runpod endpoint encounters any error (e.g. 500, timeout, or context limit), automatically fall back to OpenRouter DeepSeek V4.1 Flash!
            if agent_model.startswith("runpod/"):
                print(f"⚠️ [Sandbox Engine] Runpod endpoint returned error ({e}). Failing over to openrouter/deepseek/deepseek-v4.1-flash for InvariantMind this turn...")
                try:
                    fb_response = completion(
                        model="openrouter/deepseek/deepseek-v4.1-flash",
                        messages=messages,
                        tools=tools,
                        tool_choice="auto",
                        max_tokens=8192,
                        timeout=120,
                    )
                    fb_msg = fb_response.choices[0].message
                    fb_content = fb_msg.content or getattr(fb_msg, "reasoning_content", "") or ""
                    if fb_msg.tool_calls:
                        tc = fb_msg.tool_calls[0]
                        try:
                            args = json.loads(tc.function.arguments)
                            if isinstance(args, list):
                                merged = {}
                                for item in args:
                                    if isinstance(item, dict):
                                        merged.update(item)
                                args = merged if merged else (args[0] if (args and isinstance(args[0], dict)) else {})
                        except Exception as json_err:
                            return {
                                "type": "json_error",
                                "content": f"JSON Decoding Error in fallback: {str(json_err)}"
                            }
                        return {
                            "type": "tool_call",
                            "tool_call_id": tc.id,
                            "tool_name": tc.function.name,
                            "arguments": args,
                            "content": fb_content
                        }
                    else:
                        if fb_content:
                            fb_extracted = extract_fallback_tool_call(fb_content, tools=tools)
                            if fb_extracted:
                                return fb_extracted
                        return {
                            "type": "thought",
                            "content": fb_content or "I am reflecting and planning my next action."
                        }
                except Exception as fb_err:
                    print(f"⚠️ [Sandbox Engine] Fallback to DeepSeek V4.1 Flash also failed: {fb_err}")

            return {
                "type": "error",
                "content": f"LLM Error ({agent_model}): {str(e)}"
            }
    
    return {
        "type": "error",
        "content": f"LLM Error ({agent_model}): Max retries exceeded without action."
    }
