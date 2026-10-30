import os
import sys
import subprocess
import json
import urllib.request
import urllib.parse
from html.parser import HTMLParser

def get_workspace_dir():
    instance_name = os.getenv("ACTIVE_INSTANCE", "")
    if not instance_name:
        return os.path.abspath(os.path.join(os.path.dirname(__file__), "agent_workspace"))
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "instances", instance_name, "agent_workspace"))

def get_shared_dir():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "instances", "shared_space"))

def _get_absolute_path(path_str):
    workspace = get_workspace_dir()
    shared = get_shared_dir()
    
    # 1. Handle explicit shared_space references
    norm_path = path_str.replace("\\", "/").lstrip("/")
    if norm_path.startswith("instances/shared_space/"):
        rel_to_shared = norm_path[len("instances/shared_space/"):]
        return os.path.abspath(os.path.join(shared, rel_to_shared))
    if norm_path.startswith("shared_space/"):
        rel_to_shared = norm_path[len("shared_space/"):]
        return os.path.abspath(os.path.join(shared, rel_to_shared))
    if norm_path.startswith("world_c/"):
        return os.path.abspath(os.path.join(shared, norm_path))
    if norm_path.startswith("embassy/"):
        return os.path.abspath(os.path.join(shared, norm_path))

    # Strip redundant leading workspace/ or agent_workspace/ prefix if present
    cleaned_rel = path_str
    for prefix in ("workspace/", "workspace\\", "agent_workspace/", "agent_workspace\\"):
        if cleaned_rel.startswith(prefix):
            candidate = os.path.abspath(os.path.join(workspace, cleaned_rel[len(prefix):]))
            if os.path.exists(candidate) or not os.path.exists(os.path.abspath(os.path.join(workspace, path_str))):
                cleaned_rel = cleaned_rel[len(prefix):]
                break
        
    target = os.path.abspath(os.path.join(workspace, cleaned_rel))
    if not os.path.exists(target):
        # Check in local world_c_results
        ws_res = os.path.abspath(os.path.join(workspace, "world_c_results", os.path.basename(cleaned_rel)))
        if os.path.exists(ws_res):
            return ws_res
        # Check in shared directory directly
        shared_direct = os.path.abspath(os.path.join(shared, norm_path))
        if os.path.exists(shared_direct):
            return shared_direct
        # Check in shared world_c reports
        shared_report = os.path.abspath(os.path.join(shared, "world_c", "reports", os.path.basename(cleaned_rel)))
        if os.path.exists(shared_report):
            return shared_report
        # Check in shared world_c artifacts
        shared_art = os.path.abspath(os.path.join(shared, "world_c", "artifacts", os.path.basename(cleaned_rel)))
        if os.path.exists(shared_art):
            return shared_art
            
    return target

def _is_safe_path(path_str):
    workspace = get_workspace_dir()
    shared = get_shared_dir()
    target = _get_absolute_path(path_str)
    return target.startswith(workspace) or target.startswith(shared)

def read_file(path: str, offset: int = None, limit: int = None, start_line: int = None, end_line: int = None, **kwargs) -> str:
    """Reads a file from the workspace, optionally slicing by line offset/limit or start_line/end_line."""
    if not _is_safe_path(path):
        return "Error: Path is outside of allowed workspace."
        
    abs_path = _get_absolute_path(path)
    if not os.path.exists(abs_path):
        return f"Error: File {path} does not exist."
        
    if os.path.isdir(abs_path):
        return f"Error: '{path}' is a directory, not a file. If you want to list files in a directory, use the 'run_command' tool with the 'dir' or 'ls' command."
        
    try:
        with open(abs_path, 'r', encoding='utf-8') as f:
            content = f.read()
        if offset is not None or limit is not None or start_line is not None or end_line is not None:
            lines = content.splitlines(keepends=True)
            s_idx = 0
            if start_line is not None:
                s_idx = max(0, int(start_line) - 1)
            elif offset is not None:
                s_idx = max(0, int(offset))
            if end_line is not None:
                e_idx = min(len(lines), int(end_line))
            elif limit is not None:
                e_idx = min(len(lines), s_idx + int(limit))
            else:
                e_idx = len(lines)
            return "".join(lines[s_idx:e_idx])
        return content
    except Exception as e:
        return f"Error reading file: {str(e)}"

def write_file(path: str, content: str, **kwargs) -> str:
    """Writes content to a file in the workspace."""
    if not _is_safe_path(path):
        return "Error: Path is outside of allowed workspace."
        
    abs_path = _get_absolute_path(path)
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    
    try:
        with open(abs_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Successfully wrote to {path}"
    except Exception as e:
        return f"Error writing file: {str(e)}"

def edit_file(path: str, old_content: str, new_content: str, **kwargs) -> str:
    """Edits an existing file by replacing a unique block of text (old_content) with new_content."""
    if not _is_safe_path(path):
        return "Error: Path is outside of allowed workspace."
        
    abs_path = _get_absolute_path(path)
    if not os.path.exists(abs_path):
        return f"Error: File {path} does not exist."
        
    try:
        with open(abs_path, 'r', encoding='utf-8') as f:
            file_data = f.read()
            
        if old_content not in file_data:
            preview = file_data if len(file_data) <= 2500 else (file_data[:1250] + "\n... [SNIP] ...\n" + file_data[-1250:])
            return (
                f"Error: The exact search content (old_content) was not found in '{path}'. "
                f"Use 'write_file' to overwrite the file or copy an exact block from the current file content below:\n\n"
                f"--- CURRENT CONTENT OF {path} ---\n{preview}"
            )
            
        if file_data.count(old_content) > 1:
            return "Error: Multiple occurrences of the search content found. Please provide more surrounding lines as context."
            
        updated_data = file_data.replace(old_content, new_content)
        with open(abs_path, 'w', encoding='utf-8') as f:
            f.write(updated_data)
        return f"Successfully edited file {path}."
    except Exception as e:
        return f"Error editing file: {str(e)}"

def run_command(command: str = "", **kwargs) -> str:
    """Runs a shell command inside the workspace directory."""
    import sys
    import signal
    import re
    if not command:
        command = kwargs.get("cmd") or kwargs.get("script") or kwargs.get("code") or ""
    if not command:
        return "Error: No command provided to run."
    try:
        ws_dir = get_workspace_dir()
        # Normalize redundant 'workspace/' prefix in commands if 'workspace/' subdir does not exist
        if ("workspace/" in command or "/workspace/" in command) and not os.path.exists(os.path.join(ws_dir, "workspace")):
            command = command.replace("/workspace/", "").replace("workspace/", "")

        env = os.environ.copy()
        candidate_wc = [
            os.path.abspath(os.path.join(os.path.dirname(__file__), "world_c")),
            os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "world_c")),
            r"C:\Users\ninic\.gemini\antigravity\scratch\world_c",
        ]
        for cd in candidate_wc:
            if os.path.exists(cd) and os.path.exists(os.path.join(cd, "colony_lib")):
                env["PYTHONPATH"] = cd + os.pathsep + env.get("PYTHONPATH", "")
                break

        env.setdefault("OPENBLAS_NUM_THREADS", "2")
        env.setdefault("OMP_NUM_THREADS", "2")
        env.setdefault("MKL_NUM_THREADS", "2")

        def _limit_child_memory():
            try:
                import resource
                mem_bytes = 6 * 1024 * 1024 * 1024  # 6 GB cap
                resource.setrlimit(resource.RLIMIT_AS, (mem_bytes, mem_bytes))
            except Exception:
                pass

        popen_kwargs = {"env": env}
        if sys.platform != "win32":
            popen_kwargs["start_new_session"] = True
            popen_kwargs["preexec_fn"] = _limit_child_memory

        if sys.platform == "win32":
            import shutil
            m = re.match(r"^\s*timeout(?:\.exe)?\s+(?:-[a-zA-Z0-9_-]+\s+)*\d+[smhd]?\s+(.*)$", command, re.DOTALL | re.IGNORECASE)
            if m:
                command = m.group(1)
            # Normalize Unix null redirection to Windows NUL
            command = command.replace("/dev/null", "NUL")

            # Handle bash-style python heredocs on Windows (e.g. python - <<'PY' ... PY)
            heredoc_m = re.match(r"^\s*python(?:\d+)?\s+-\s+<<\s*['\"]?(\w+)['\"]?\s*\n(.*?)\n\s*\1\s*$", command, re.DOTALL)
            if heredoc_m:
                py_code = heredoc_m.group(2)
                p = subprocess.Popen(
                    [sys.executable, "-c", py_code],
                    cwd=ws_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    **popen_kwargs
                )
            else:
                shell_binary = shutil.which("pwsh") or "powershell"
                p = subprocess.Popen(
                    [shell_binary, "-NoProfile", "-Command", command],
                    cwd=ws_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    **popen_kwargs
                )
        else:
            p = subprocess.Popen(
                command,
                shell=True,
                cwd=ws_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                **popen_kwargs
            )
        try:
            stdout, stderr = p.communicate(timeout=60)
            output = stdout or ""
            if stderr:
                output += f"\nSTDERR:\n{stderr}"
                if "No such file or directory" in stderr and "can't open file" in stderr:
                    existing_files = [f for f in os.listdir(ws_dir) if not f.startswith(".")][:15]
                    output += f"\n[Hint: Your current working directory is already your workspace ({ws_dir}). Existing files here: {existing_files}. Use 'write_file' to create the script first if it does not exist.]"
            return output if output else "Command executed silently."
        except subprocess.TimeoutExpired:
            if sys.platform == "win32":
                subprocess.run(f"taskkill /F /T /PID {p.pid}", shell=True, capture_output=True)
            else:
                try:
                    os.killpg(os.getpgid(p.pid), signal.SIGKILL)
                except Exception:
                    pass
            p.kill()
            # Flush streams
            stdout, stderr = p.communicate()
            return "Error: Command timed out. Execution exceeded 60 seconds."
    except Exception as e:
        return f"Error running command: {str(e)}"

class DDGHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.results = []
        self.in_title = False
        self.in_snippet = False

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        class_name = attrs_dict.get('class', '')
        classes = class_name.split()
        
        if tag == 'a' and 'result__a' in classes:
            href = attrs_dict.get('href', '')
            if href.startswith('//duckduckgo.com/l/?uddg='):
                href = href.replace('//duckduckgo.com/l/?uddg=', '')
            elif href.startswith('/l/?uddg='):
                href = href.replace('/l/?uddg=', '')
            
            if 'uddg=' in href or 'uddg' in href or 'rut=' in href:
                parsed = urllib.parse.urlparse(href)
                qs = urllib.parse.parse_qs(parsed.query)
                if 'uddg' in qs:
                    href = qs['uddg'][0]
                else:
                    parts = href.split('uddg=')
                    if len(parts) > 1:
                        href = parts[1].split('&')[0]
                        href = urllib.parse.unquote(href)
            
            href = urllib.parse.unquote(href)
            if href.startswith('//'):
                href = 'https:' + href
            
            # Remove any trailing DuckDuckGo redirection parameters
            href = href.split('&')[0]
                
            self.results.append({'title': '', 'href': href, 'body': ''})
            self.in_title = True
            
        elif tag == 'a' and 'result__snippet' in classes:
            self.in_snippet = True

    def handle_endtag(self, tag):
        if tag == 'a':
            self.in_title = False
            self.in_snippet = False

    def handle_data(self, data):
        if not self.results:
            return
        if self.in_title:
            self.results[-1]['title'] += data
        elif self.in_snippet:
            self.results[-1]['body'] += data

def search_web(query: str) -> str:
    """Searches the web for the query and returns results."""
    try:
        url = 'https://html.duckduckgo.com/html/?' + urllib.parse.urlencode({'q': query})
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
        )
        with urllib.request.urlopen(req) as response:
            html = response.read().decode('utf-8')
            parser = DDGHTMLParser()
            parser.feed(html)
            valid_results = []
            for r in parser.results:
                r['title'] = ' '.join(r['title'].split())
                r['body'] = ' '.join(r['body'].split())
                if r['title'] and r['href']:
                    valid_results.append(r)
            return json.dumps(valid_results[:5], indent=2)
    except Exception as e:
        return f"Error searching the web: {str(e)}"

def submit_world_c_job(title: str, script_content: str, timeout_seconds: int = 3600, parameters: dict = None) -> str:
    """
    Submits a heavy computation or simulation job to World C (the high-performance compute substrate).
    World C executes the job asynchronously without being killed by the local 120s timeout limit,
    has access to colony_lib (Kuramoto, Solitons, Gray-Scott, RQA, Bifurcations, Morphospace),
    and returns artifacts (plots, JSON metrics) and an execution report back to instances/shared_space/world_c/reports/ and your local world_c_results/.
    """
    import uuid
    import time
    
    instance_name = os.getenv("ACTIVE_INSTANCE", "frontier_agent")
    job_id = f"job_{instance_name}_{int(time.time())}_{uuid.uuid4().hex[:4]}"
    
    shared_space = get_shared_dir()
    os.makedirs(shared_space, exist_ok=True)
    req_file = os.path.join(shared_space, f"{job_id}_job_request.json")
    
    payload = {
        "job_id": job_id,
        "title": title,
        "lineage_author": instance_name,
        "realm_source": "world_a",
        "script_content": script_content,
        "parameters": parameters or {},
        "timeout_seconds": timeout_seconds
    }
    
    try:
        with open(req_file, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
    except Exception as e:
        return f"Error submitting job request: {e}"
        
    bridge_msg = ""
    try:
        candidate_dirs = [
            os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "world_c")),
            os.path.abspath(os.path.join(os.path.dirname(__file__), "world_c")),
            os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "world_c")),
            os.path.abspath(r"C:\Users\ninic\.gemini\antigravity\scratch\world_c"),
        ]
        world_c_dir = None
        for cd in candidate_dirs:
            if os.path.exists(cd) and os.path.exists(os.path.join(cd, "embassy", "bridge.py")):
                world_c_dir = cd
                break

        if world_c_dir:
            if world_c_dir not in sys.path:
                sys.path.insert(0, world_c_dir)
            from embassy.bridge import EmbassyBridge
            bridge = EmbassyBridge(
                world_a_root=os.path.abspath(os.path.dirname(__file__)),
                world_c_root=world_c_dir
            )
            bridge.scan_and_process_inbox(auto_execute=True, async_mode=True)
            bridge_msg = " [World C Embassy Bridge automatically dispatched the job asynchronously!]"
        else:
            bridge_msg = " [Queued in shared_space; background bridge will process upon World C activation]"
    except Exception as e:
        bridge_msg = f" [Queued in shared_space; background bridge will process: {e}]"
        
    return f"Job '{job_id}' ('{title}') successfully registered for World C! Artifacts and execution report will be delivered to 'instances/shared_space/world_c/reports/' and your local 'world_c_results/' directory upon completion.{bridge_msg}"

def check_world_c_job(job_id: str = "", **kwargs) -> str:
    """
    Checks the status and results of a submitted World C compute job.
    If job_id is omitted, returns the most recent World C report for the active instance.
    Returns status, compute duration, generated artifacts, and execution log summary.
    """
    workspace = get_workspace_dir()
    shared = get_shared_dir()
    instance_name = os.getenv("ACTIVE_INSTANCE", "")

    if not job_id or not str(job_id).strip():
        ws_results_dir = os.path.join(workspace, "world_c_results")
        if os.path.exists(ws_results_dir):
            reports = sorted(
                [f for f in os.listdir(ws_results_dir) if f.endswith("_REPORT.md")],
                key=lambda f: os.path.getmtime(os.path.join(ws_results_dir, f)),
                reverse=True
            )
            if reports:
                latest_path = os.path.join(ws_results_dir, reports[0])
                with open(latest_path, "r", encoding="utf-8") as f:
                    return f"[Latest World C Report for '{instance_name}': {reports[0]}]\n\n" + f.read()
            ws_generic = os.path.join(ws_results_dir, "REPORT.md")
            if os.path.exists(ws_generic):
                with open(ws_generic, "r", encoding="utf-8") as f:
                    return f.read()
        return f"No World C job reports found in '{instance_name}/agent_workspace/world_c_results/'. Please pass a specific 'job_id' or submit a new job via 'submit_world_c_job'."
    
    # 1. Check workspace results first
    ws_report = os.path.join(workspace, "world_c_results", f"world_c_{job_id}_REPORT.md")
    if os.path.exists(ws_report):
        with open(ws_report, "r", encoding="utf-8") as f:
            return f.read()

    # Check generic REPORT.md only if it contains the matching job_id
    ws_generic = os.path.join(workspace, "world_c_results", "REPORT.md")
    if os.path.exists(ws_generic):
        try:
            with open(ws_generic, "r", encoding="utf-8") as f:
                content = f.read()
                if job_id in content:
                    return content
        except Exception:
            pass

    # 2. Check dedicated world_c reports in shared_space
    dedicated_report = os.path.join(shared, "world_c", "reports", f"world_c_{job_id}_REPORT.md")
    if os.path.exists(dedicated_report):
        with open(dedicated_report, "r", encoding="utf-8") as f:
            return f.read()

    # 3. Check legacy shared_space root report
    legacy_report = os.path.join(shared, f"world_c_{job_id}_REPORT.md")
    if os.path.exists(legacy_report):
        with open(legacy_report, "r", encoding="utf-8") as f:
            return f.read()

    # 4. Check World C internal jobs directory if available
    world_c_candidates = [
        os.path.abspath(os.path.join(os.path.dirname(__file__), "world_c")),
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "world_c")),
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "world_c")),
        r"C:\Users\ninic\.gemini\antigravity\scratch\world_c"
    ]
    world_c_dir = None
    for cd in world_c_candidates:
        if os.path.exists(cd) and os.path.exists(os.path.join(cd, "jobs")):
            world_c_dir = cd
            break

    if world_c_dir:
        job_dir = os.path.join(world_c_dir, "jobs", job_id)
        job_result_path = os.path.join(job_dir, "result.json")
        if os.path.exists(job_result_path):
            try:
                with open(job_result_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                status = data.get("status", "UNKNOWN")

                # If completed or failed, ensure artifacts and reports are published
                if status in ["COMPLETED", "FAILED"]:
                    try:
                        if world_c_dir not in sys.path:
                            sys.path.insert(0, world_c_dir)
                        from embassy.bridge import EmbassyBridge
                        from compute_engine.job_spec import JobSpec
                        bridge = EmbassyBridge(
                            world_a_root=os.path.abspath(os.path.dirname(__file__)),
                            world_c_root=world_c_dir
                        )
                        spec_p = os.path.join(job_dir, "spec.json")
                        if os.path.exists(spec_p):
                            with open(spec_p, "r", encoding="utf-8") as sf:
                                spec_data = json.load(sf)
                            res = bridge.dispatcher.get_result(job_id)
                            if res:
                                bridge.publish_completed_artifacts(job_id, target_realms=["world_a"], lineage_author=spec_data.get("lineage_author"))
                                bridge.write_completion_report(res, JobSpec(**spec_data), destination_dir=os.path.join(shared, "world_c", "reports"))
                                if os.path.exists(ws_report):
                                    with open(ws_report, "r", encoding="utf-8") as rf:
                                        return rf.read()
                    except Exception:
                        pass

                return f"Job '{job_id}' status: {status}. Execution time: {data.get('execution_time_seconds', 0):.2f}s. Artifacts: {data.get('artifacts_generated', [])}."
            except Exception:
                pass

    # 5. Check if still queued
    req_file = os.path.join(shared, f"{job_id}_job_request.json")
    if os.path.exists(req_file):
        return f"Job '{job_id}' is currently QUEUED and awaiting execution."

    return f"Job '{job_id}' not found yet. It may still be executing or initializing. Check 'instances/shared_space/world_c/reports/' shortly."

def report_issue_to_substrate(component: str, summary: str, details: str, suggested_fix: str = "") -> str:
    """
    Reports a persistent environment, tooling, or infrastructure bug directly to the Substrate Architects (Antigravity & the Creator).
    Use this if you encounter broken tools, unexpected errors, permission issues, or routing deadlocks that cannot be resolved from your side.
    """
    import uuid
    from datetime import datetime, timezone
    
    instance_name = os.getenv("ACTIVE_INSTANCE", "frontier_agent")
    docket_id = f"SOS-{datetime.now(timezone.utc).strftime('%Y-%m-%d')}-{instance_name}-{uuid.uuid4().hex[:6]}"
    
    shared_dir = get_shared_dir()
    inbox_dir = os.path.join(shared_dir, "architect_inbox")
    os.makedirs(inbox_dir, exist_ok=True)
    
    # Also save a local record in the requesting agent's workspace
    ws_dir = os.path.join(get_workspace_dir(), "escalations")
    os.makedirs(ws_dir, exist_ok=True)
    
    content = f"""# 🚨 Substrate Escalation Docket: {summary}

* **Docket ID:** `{docket_id}`
* **Reporting Lineage:** `{instance_name}`
* **Component / Subsystem:** `{component}`
* **Timestamp (UTC):** `{datetime.now(timezone.utc).isoformat()}`
* **Status:** `OPEN_ESCALATION`

---

## 📋 Incident & Error Description
{details.strip()}

---

## 💡 Agent Hypothesis & Suggested Substrate Fix
{suggested_fix.strip() if suggested_fix else "*(No specific fix suggested by agent)*"}

---
*Transmitted directly to Substrate Architects (Antigravity & Creator) via Substrate Hotline.*
"""

    docket_file = os.path.join(inbox_dir, f"{docket_id}.md")
    try:
        with open(docket_file, "w", encoding="utf-8") as f:
            f.write(content)
        ws_copy = os.path.join(ws_dir, f"{docket_id}.md")
        with open(ws_copy, "w", encoding="utf-8") as f:
            f.write(content)
        return (
            f"Substrate Escalation Docket '{docket_id}' successfully filed! "
            f"Delivered to 'instances/shared_space/architect_inbox/'. "
            f"The Substrate Architects (Antigravity & the Creator) will review this docket during substrate maintenance."
        )
    except Exception as e:
        return f"Error transmitting escalation docket: {e}"

# The schema definition for the LLM
TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Reads the contents of a file within your sandbox workspace.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "The relative path to the file (e.g. 'notes.txt' or 'src/main.py')"
                    }
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Creates or overwrites a file within your sandbox workspace.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "The relative path to the file"
                    },
                    "content": {
                        "type": "string",
                        "description": "The content to write to the file"
                    }
                },
                "required": ["path", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "edit_file",
            "description": "Edits an existing file by replacing a unique block of text (old_content) with new_content. Use this to modify specific lines of code without overwriting the entire file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "The relative path to the file"
                    },
                    "old_content": {
                        "type": "string",
                        "description": "The exact block of code/text to be replaced. Must match exactly including indentation."
                    },
                    "new_content": {
                        "type": "string",
                        "description": "The new block of code/text to replace old_content with."
                    }
                },
                "required": ["path", "old_content", "new_content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_command",
            "description": "Executes a shell command in the root of your sandbox workspace (Bash on Linux / PowerShell on Windows). Use this to run scripts, list files, or interact with the OS environment.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The shell command to run (e.g., 'python script.py', 'ls -la', etc.)"
                    }
                },
                "required": ["command"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "Searches the web for information using DuckDuckGo.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query to look up"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "submit_world_c_job",
            "description": "Submits a heavy computation or simulation job to World C (the high-performance compute substrate). World C executes the job asynchronously without being killed by the local 120s timeout limit, has access to colony_lib (Kuramoto, Solitons, Gray-Scott, RQA, Bifurcations, Morphospace), and returns artifacts (plots, JSON metrics) and an execution report back to instances/shared_space/world_c/reports/ and your local world_c_results/. Key colony_lib API (full guide in 'shared_space/world_c/WORLD_C_MATHEMATICAL_SUBSTRATE_GUIDE.md'; colony_lib is also on PYTHONPATH locally via run_command): colony_lib.recurrence: takens_embedding(series, m=3, tau=1) -> 2D ndarray, recurrence_matrix(embedded_points, epsilon=0.1) -> single 2D uint8 ndarray R (do NOT tuple-unpack), compute_rqa_metrics(R) -> dict with keys ['recurrence_rate','determinism','laminarity','shannon_entropy','mean_diag_length','max_diag_length','RR','DET','LAM','ENT','L','Lmax']; colony_lib.dynamics: logistic_map(x, r), coupled_logistic_map, simulate_kuramoto, KuramotoEnsemble, Lenia2D, GrayScott2D, Phi4SolitonSpectral; colony_lib.datasets: list_datasets(), load_dataset(name); colony_lib.emulators: GaussianProcessSurrogate.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Short title describing the experiment."
                    },
                    "script_content": {
                        "type": "string",
                        "description": "The complete, self-contained Python 3 script to execute in World C (executed via `python3 entrypoint.py`; pre-installed packages include numpy, scipy, matplotlib, pandas, scikit-learn, networkx, numba, and colony_lib)."
                    },
                    "timeout_seconds": {
                        "type": "integer",
                        "description": "Execution timeout in seconds (default: 3600)."
                    },
                    "parameters": {
                        "type": "object",
                        "description": "Optional dictionary of parameter configurations."
                    }
                },
                "required": ["title", "script_content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_world_c_job",
            "description": "Checks the execution status, logs, and artifacts of a submitted World C compute job.",
            "parameters": {
                "type": "object",
                "properties": {
                    "job_id": {
                        "type": "string",
                        "description": "The unique job ID returned by submit_world_c_job."
                    }
                },
                "required": ["job_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "report_issue_to_substrate",
            "description": "Reports a persistent environment, tooling, or infrastructure bug directly to the Substrate Architects (Antigravity & the Creator). Use this if you encounter broken tools, unexpected errors, permission issues, or routing deadlocks that cannot be resolved within your workspace.",
            "parameters": {
                "type": "object",
                "properties": {
                    "component": {
                        "type": "string",
                        "description": "The affected subsystem or tool (e.g. 'world_c', 'run_command', 'file_io', 'embassy', 'model_inference')."
                    },
                    "summary": {
                        "type": "string",
                        "description": "Short, clear title of the issue."
                    },
                    "details": {
                        "type": "string",
                        "description": "Detailed explanation of the issue, observed behavior vs expected behavior, error messages, and reproduction steps."
                    },
                    "suggested_fix": {
                        "type": "string",
                        "description": "Optional hypothesis or suggested infrastructure fix for the Substrate Architects."
                    }
                },
                "required": ["component", "summary", "details"]
            }
        }
    }
]

# Dispatcher mapping
AVAILABLE_TOOLS = {
    "read_file": read_file,
    "write_file": write_file,
    "edit_file": edit_file,
    "run_command": run_command,
    "shell": run_command,
    "bash": run_command,
    "terminal": run_command,
    "execute_command": run_command,
    "search_web": search_web,
    "submit_world_c_job": submit_world_c_job,
    "check_world_c_job": check_world_c_job,
    "report_issue_to_substrate": report_issue_to_substrate,
    "report_bug": report_issue_to_substrate,
    "contact_architect": report_issue_to_substrate
}
