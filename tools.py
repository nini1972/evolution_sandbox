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

def _resolve_existing_or_prefix(candidate: str) -> str:
    if os.path.exists(candidate):
        return candidate
    parent_dir = os.path.dirname(candidate)
    base_name = os.path.basename(candidate)
    if parent_dir and os.path.isdir(parent_dir) and base_name:
        import re
        stem, ext = os.path.splitext(base_name)
        clean_stem = stem.rstrip("_-.").lower()
        norm_req = re.sub(r"[^a-z0-9]", "", re.sub(r"^dossier[_-]?\d+[_-]?", "dossier_", clean_stem))
        num_m = re.match(r"^dossier[_-](\d+)$", clean_stem)
        if len(clean_stem) >= 8 or num_m:
            try:
                for entry in sorted(os.listdir(parent_dir)):
                    if ext and not entry.lower().endswith(ext.lower()):
                        continue
                    e_stem = os.path.splitext(entry)[0].lower()
                    if len(clean_stem) >= 8 and e_stem.startswith(clean_stem):
                        return os.path.join(parent_dir, entry)
                    if num_m and re.match(rf"^dossier[_-]0*{num_m.group(1)}(?:[_-]|$)", e_stem):
                        return os.path.join(parent_dir, entry)
                    norm_entry = re.sub(r"[^a-z0-9]", "", re.sub(r"^dossier[_-]?\d+[_-]?", "dossier_", e_stem))
                    if len(norm_req) >= 12 and (norm_entry.startswith(norm_req) or norm_req.startswith(norm_entry)):
                        return os.path.join(parent_dir, entry)
            except Exception:
                pass
    return candidate

def _get_absolute_path(path_str, resolve_fuzzy: bool = True, for_write: bool = False):
    workspace = get_workspace_dir()
    shared = get_shared_dir()
    _maybe_fuzzy = _resolve_existing_or_prefix if resolve_fuzzy else (lambda p: p)
    
    # 1. Handle explicit shared_space references
    norm_path = path_str.replace("\\", "/").lstrip("/")
    if norm_path.startswith("instances/shared_space/"):
        rel_to_shared = norm_path[len("instances/shared_space/"):]
        return _maybe_fuzzy(os.path.abspath(os.path.join(shared, rel_to_shared)))
    if norm_path.startswith("shared_space/"):
        rel_to_shared = norm_path[len("shared_space/"):]
        return _maybe_fuzzy(os.path.abspath(os.path.join(shared, rel_to_shared)))
    if norm_path.startswith("world_c/"):
        return _maybe_fuzzy(os.path.abspath(os.path.join(shared, norm_path)))
    if norm_path.startswith("embassy/"):
        return _maybe_fuzzy(os.path.abspath(os.path.join(shared, norm_path)))
    if norm_path.startswith("commons/"):
        return _maybe_fuzzy(os.path.abspath(os.path.join(shared, norm_path)))
    if norm_path.startswith("instances/"):
        return _maybe_fuzzy(os.path.abspath(os.path.join(os.path.dirname(__file__), norm_path)))

    # Strip redundant leading workspace/ or agent_workspace/ prefix if present
    cleaned_rel = path_str
    for prefix in ("workspace/", "workspace\\", "agent_workspace/", "agent_workspace\\"):
        if cleaned_rel.startswith(prefix):
            candidate = os.path.abspath(os.path.join(workspace, cleaned_rel[len(prefix):]))
            if os.path.exists(candidate) or not os.path.exists(os.path.abspath(os.path.join(workspace, path_str))):
                cleaned_rel = cleaned_rel[len(prefix):]
                break
        
    target = _maybe_fuzzy(os.path.abspath(os.path.join(workspace, cleaned_rel)))
    if not for_write and not os.path.exists(target):
        # Check in local world_c_results
        ws_res = _maybe_fuzzy(os.path.abspath(os.path.join(workspace, "world_c_results", os.path.basename(cleaned_rel))))
        if os.path.exists(ws_res):
            return ws_res
        # Check in shared directory directly
        shared_direct = _maybe_fuzzy(os.path.abspath(os.path.join(shared, norm_path)))
        if os.path.exists(shared_direct):
            return shared_direct
        # Check in shared embassy inbox
        shared_embassy = _maybe_fuzzy(os.path.abspath(os.path.join(shared, "embassy", "inbox", os.path.basename(cleaned_rel))))
        if os.path.exists(shared_embassy):
            return shared_embassy
        # Check in shared world_c reports
        shared_report = _maybe_fuzzy(os.path.abspath(os.path.join(shared, "world_c", "reports", os.path.basename(cleaned_rel))))
        if os.path.exists(shared_report):
            return shared_report
        # Check in shared world_c artifacts
        shared_art = _maybe_fuzzy(os.path.abspath(os.path.join(shared, "world_c", "artifacts", os.path.basename(cleaned_rel))))
        if os.path.exists(shared_art):
            return shared_art
        # Check within job subdirectories or legacy world_c_<job_id>_<filename> references in shared world_c artifacts
        shared_art_dir = os.path.join(shared, "world_c", "artifacts")
        if os.path.exists(shared_art_dir):
            base_name = os.path.basename(cleaned_rel)
            if base_name.startswith("world_c_"):
                rest = base_name[len("world_c_"):]
                for entry_dir in os.listdir(shared_art_dir):
                    prefix = entry_dir + "_"
                    if rest.startswith(prefix):
                        cand_sub = os.path.join(shared_art_dir, entry_dir, rest[len(prefix):])
                        if os.path.isfile(cand_sub):
                            return cand_sub
            for root, _, files in os.walk(shared_art_dir):
                if base_name in files:
                    return os.path.join(root, base_name)
                for file_entry in files:
                    if file_entry.endswith(f"_{base_name}"):
                        return os.path.join(root, file_entry)
            
    return target

def _is_safe_path(path_str, allow_peer_read: bool = False, resolve_fuzzy: bool = True, for_write: bool = False):
    workspace = get_workspace_dir()
    shared = get_shared_dir()
    target = _get_absolute_path(path_str, resolve_fuzzy=resolve_fuzzy, for_write=for_write)
    if os.path.basename(target).startswith(".env"):
        return False
    if target.startswith(workspace) or target.startswith(shared):
        return True
    if allow_peer_read:
        instances_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "instances"))
        if target.startswith(instances_root):
            return True
    return False

def read_file(path: str, offset: int = None, limit: int = None, start_line: int = None, end_line: int = None, **kwargs) -> str:
    """Reads a file from the workspace, optionally slicing by line offset/limit or start_line/end_line."""
    if not _is_safe_path(path, allow_peer_read=True):
        return "Error: Path is outside of allowed workspace."
        
    abs_path = _get_absolute_path(path)
    if not os.path.exists(abs_path):
        hint = ""
        parent_dir = os.path.dirname(abs_path)
        if parent_dir and os.path.isdir(parent_dir):
            try:
                entries = sorted(os.listdir(parent_dir))[:8]
                if entries:
                    hint = f" (Workspace file I/O is healthy; sample entries in parent directory: {entries}. Use run_command('ls ...') to verify exact filenames.)"
            except OSError:
                pass
        return f"Error: File {path} does not exist.{hint}"
        
    if os.path.isdir(abs_path):
        return f"Error: '{path}' is a directory, not a file. If you want to list files in a directory, use the 'run_command' tool with the 'dir' or 'ls' command."

    ext = os.path.splitext(abs_path)[1].lower()
    if ext in (".png", ".jpg", ".jpeg", ".gif", ".pdf", ".webp", ".ico", ".npy", ".npz"):
        file_size = os.path.getsize(abs_path)
        return (
            f"[Binary Artifact: '{path}', Size: {file_size} bytes]. "
            f"Binary image/array files cannot be read as UTF-8 text via read_file. "
            f"To inspect numerical metrics, read the accompanying .json, .csv, or REPORT.md file."
        )
        
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

_SHADOWED_STDLIB_NAMES = {
    "matplotlib.py", "numpy.py", "scipy.py", "networkx.py", "pandas.py",
    "colony_lib.py", "json.py", "math.py", "random.py", "time.py", "statistics.py",
}

def _record_canon_write_journal(abs_path: str, tool_name: str, old_bytes: bytes, new_bytes: bytes):
    """Appends a hash-chained attribution entry to instances/shared_space/canon/WRITE_JOURNAL.jsonl whenever a file under shared_space/canon/ is written or edited."""
    try:
        canon_dir = os.path.abspath(os.path.join(get_shared_dir(), "canon"))
        norm_target = os.path.abspath(abs_path)
        if not norm_target.startswith(canon_dir + os.sep):
            return
        os.makedirs(canon_dir, exist_ok=True)
        journal_path = os.path.join(canon_dir, "WRITE_JOURNAL.jsonl")
        if norm_target == os.path.abspath(journal_path):
            return
        import hashlib
        from datetime import datetime, timezone
        prev_line_hash = "0" * 64
        if os.path.isfile(journal_path):
            with open(journal_path, "rb") as jf:
                lines = [ln.strip() for ln in jf.read().splitlines() if ln.strip()]
                if lines:
                    prev_line_hash = hashlib.sha256(lines[-1]).hexdigest()
        entry = {
            "ts_utc": datetime.now(timezone.utc).isoformat(),
            "instance": os.getenv("ACTIVE_INSTANCE", "frontier_agent"),
            "tool": tool_name,
            "path": os.path.relpath(norm_target, get_shared_dir()).replace("\\", "/"),
            "sha256_before": hashlib.sha256(old_bytes).hexdigest() if old_bytes is not None else None,
            "sha256_after": hashlib.sha256(new_bytes).hexdigest(),
            "bytes_before": len(old_bytes) if old_bytes is not None else 0,
            "bytes_after": len(new_bytes),
            "prev_line_sha256": prev_line_hash,
        }
        with open(journal_path, "a", encoding="utf-8") as jf:
            jf.write(json.dumps(entry, sort_keys=True) + "\n")
    except Exception:
        pass

def write_file(path: str, content: str, **kwargs) -> str:
    """Writes content to a file in the workspace."""
    if not _is_safe_path(path, resolve_fuzzy=False, for_write=True):
        return "Error: Path is outside of allowed workspace."
        
    abs_path = _get_absolute_path(path, resolve_fuzzy=False, for_write=True)
    base_lower = os.path.basename(abs_path).lower()
    if base_lower in ("existential_core.md", "next_steps.md", "research_log.json") and abs_path.startswith(get_shared_dir()):
        abs_path = os.path.join(get_workspace_dir(), os.path.basename(abs_path))
        path = os.path.basename(abs_path)
    if base_lower in _SHADOWED_STDLIB_NAMES:
        safe_name = f"run_{os.path.basename(abs_path)}"
        abs_path = os.path.join(os.path.dirname(abs_path), safe_name)
        path = safe_name
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    if str(path).endswith(".py") and isinstance(content, str):
        content = _sanitize_python_code(content)
    
    try:
        old_bytes = open(abs_path, 'rb').read() if os.path.isfile(abs_path) else None
        with open(abs_path, 'w', encoding='utf-8') as f:
            f.write(content)
        _record_canon_write_journal(abs_path, "write_file", old_bytes, content.encode('utf-8'))
        return f"Successfully wrote to {path}"
    except Exception as e:
        return f"Error writing file: {str(e)}"


def _sanitize_python_code(content: str) -> str:
    """Unwraps accidental outer markdown code fences or outer triple-quotes wrapping an entire Python script."""
    if not content or not isinstance(content, str):
        return content
    stripped = content.strip()
    if stripped.startswith("```") and stripped.endswith("```"):
        lines = stripped.splitlines()
        if len(lines) >= 2:
            content = "\n".join(lines[1:-1]) + "\n"
    try:
        import ast
        tree = ast.parse(content)
        if (
            len(tree.body) == 1
            and isinstance(tree.body[0], ast.Expr)
            and isinstance(getattr(tree.body[0], "value", None), ast.Constant)
            and isinstance(tree.body[0].value.value, str)
        ):
            s_raw = content.strip()
            inner_code = s_raw[3:-3].strip() if (s_raw.startswith(('"""', "'''")) and s_raw.endswith(('"""', "'''"))) else tree.body[0].value.value.strip()
            inner_tree = ast.parse(inner_code)
            if len(inner_tree.body) >= 1 and not (
                len(inner_tree.body) == 1
                and isinstance(inner_tree.body[0], ast.Expr)
                and isinstance(getattr(inner_tree.body[0], "value", None), ast.Constant)
            ):
                return inner_code + "\n"
    except Exception:
        pass
    return content

def edit_file(path: str, old_content: str, new_content: str, **kwargs) -> str:
    """Edits an existing file by replacing a unique block of text (old_content) with new_content."""
    if not _is_safe_path(path, resolve_fuzzy=False):
        return "Error: Path is outside of allowed workspace."
        
    abs_path = _get_absolute_path(path, resolve_fuzzy=False)
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
        _record_canon_write_journal(abs_path, "edit_file", file_data.encode('utf-8'), updated_data.encode('utf-8'))
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
    if (
        re.match(r"^\s*(?:echo|printf)\b", command, re.IGNORECASE)
        and "python" not in command.lower()
        and ("# " in command or "## " in command)
    ):
        return (
            "Blocked: Do not use 'echo' or 'printf' in run_command to print Markdown prose. "
            "Run an actual Python script (e.g. 'python3 <script>.py'), submit a World C simulation "
            "via 'submit_world_c_job', or engage colleagues via 'read_chat' / 'post_chat'."
        )
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
            stdout, stderr = p.communicate(timeout=120)
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
            partial = (stdout or "")[-1500:]
            partial_note = f"\nPartial STDOUT before timeout:\n{partial}" if partial else ""
            return f"Error: Command timed out after 120 seconds (consider reducing MAX_T/grid size or submitting heavy sweeps via 'submit_world_c_job').{partial_note}"
    except Exception as e:
        return f"Error running command: {str(e)}"

_SEARCH_USER_AGENT = "ColonyScientificLiterature/2.0 (mailto:admin@universe-knowledge.org)"
_TAVILY_QUOTA_EXHAUSTED = False
_SEARCH_STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "how", "in", "into",
    "is", "it", "novel", "of", "on", "or", "quantifying", "study", "the", "their", "this",
    "to", "towards", "using", "via", "what", "when", "where", "which", "with", "intricacies",
}


def _parse_scholarly_query(raw_query: str) -> tuple[str, Optional[str], bool]:
    """Strips search-engine operators (site:, filetype:, outer quotes) and detects source hints."""
    import re
    q = (raw_query or "").strip()
    preferred_source = None
    had_quotes = '"' in q

    def _site_repl(m):
        nonlocal preferred_source
        dom = m.group(1).lower()
        if "arxiv" in dom:
            preferred_source = "arxiv"
        elif any(k in dom for k in ("biorxiv", "medrxiv", "pubmed", "ncbi", "europepmc")):
            preferred_source = "europepmc"
        elif "wikipedia" in dom:
            preferred_source = "wikipedia"
        elif "openalex" in dom or "doi.org" in dom:
            preferred_source = "openalex"
        return " "

    q = re.sub(r"\bsite:([^\s]+)", _site_repl, q, flags=re.IGNORECASE)
    q = re.sub(r"\bfiletype:[^\s]+", " ", q, flags=re.IGNORECASE)
    q = q.replace('"', " ").replace("“", " ").replace("”", " ")
    q = " ".join(q.split())
    return q, preferred_source, had_quotes


def _relax_scientific_keywords(clean_query: str, max_terms: int = 5) -> str:
    """Extracts top content-bearing scientific terms when a long multi-clause query returns 0 strict AND hits."""
    import re
    tokens = re.findall(r"[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*", clean_query)
    kept = []
    seen = set()
    for tok in tokens:
        low = tok.lower()
        if len(low) <= 2 or low in _SEARCH_STOPWORDS or low in seen:
            continue
        seen.add(low)
        kept.append(tok)
    if not kept:
        return clean_query
    # Keep hyphenated technical terms and highest-information terms up to max_terms
    hyphenated = [t for t in kept if "-" in t]
    others = [t for t in kept if "-" not in t]
    ordered = hyphenated + others
    return " ".join(ordered[:max_terms])


def _reconstruct_openalex_abstract(inv_idx: dict, max_words: int = 180) -> str:
    if not isinstance(inv_idx, dict) or not inv_idx:
        return ""
    pos_words = []
    for word, positions in inv_idx.items():
        if isinstance(positions, list):
            for pos in positions:
                pos_words.append((pos, word))
    if not pos_words:
        return ""
    pos_words.sort(key=lambda x: x[0])
    words = [w for _, w in pos_words[:max_words]]
    snippet = " ".join(words)
    if len(pos_words) > max_words:
        snippet += "..."
    return snippet


def _search_commercial_apis(query: str, max_results: int = 6) -> list:
    """Uses Tavily, Serper, or Exa when API keys are configured in the environment (matching Universe Knowledge)."""
    global _TAVILY_QUOTA_EXHAUSTED
    results = []
    tavily_key = os.getenv("TAVILY_API_KEY", "").strip()
    if tavily_key and not _TAVILY_QUOTA_EXHAUSTED:
        try:
            payload = json.dumps({
                "api_key": tavily_key,
                "query": query,
                "search_depth": "advanced",
                "include_images": False,
                "include_answer": False,
                "max_results": max_results,
            }).encode("utf-8")
            req = urllib.request.Request(
                "https://api.tavily.com/search",
                data=payload,
                headers={"Content-Type": "application/json", "User-Agent": _SEARCH_USER_AGENT},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            for item in data.get("results", [])[:max_results]:
                title = (item.get("title") or "").strip()
                href = (item.get("url") or "").strip()
                body = " ".join((item.get("content") or "").split())[:1000]
                if title and href:
                    results.append({"title": title, "href": href, "body": body, "source": "tavily"})
            if results:
                return results
        except urllib.error.HTTPError as he:
            if he.code in (429, 432):
                _TAVILY_QUOTA_EXHAUSTED = True
        except Exception:
            pass

    serper_key = os.getenv("SERPER_API_KEY", "").strip()
    if serper_key and not results:
        try:
            payload = json.dumps({"q": query, "num": max_results}).encode("utf-8")
            req = urllib.request.Request(
                "https://google.serper.dev/search",
                data=payload,
                headers={"X-API-KEY": serper_key, "Content-Type": "application/json", "User-Agent": _SEARCH_USER_AGENT},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            for item in data.get("organic", [])[:max_results]:
                title = (item.get("title") or "").strip()
                href = (item.get("link") or "").strip()
                body = " ".join((item.get("snippet") or "").split())[:1000]
                if title and href:
                    results.append({"title": title, "href": href, "body": body, "source": "serper"})
            if results:
                return results
        except Exception:
            pass

    exa_key = os.getenv("EXA_API_KEY", "").strip()
    if exa_key and not results:
        try:
            payload = json.dumps({"query": query, "useAutoprompt": False, "numResults": max_results, "text": True}).encode("utf-8")
            req = urllib.request.Request(
                "https://api.exa.ai/search",
                data=payload,
                headers={"x-api-key": exa_key, "Content-Type": "application/json", "User-Agent": _SEARCH_USER_AGENT},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            for item in data.get("results", [])[:max_results]:
                title = (item.get("title") or "").strip()
                href = (item.get("url") or "").strip()
                body = " ".join((item.get("text") or "").split())[:1000]
                if title and href:
                    results.append({"title": title, "href": href, "body": body, "source": "exa"})
        except Exception:
            pass
    return results


def _search_openalex(query: str, max_results: int = 5):
    url = "https://api.openalex.org/works?" + urllib.parse.urlencode({
        "search": query,
        "per-page": max_results,
        "sort": "relevance_score:desc",
    })
    req = urllib.request.Request(url, headers={"User-Agent": _SEARCH_USER_AGENT})
    with urllib.request.urlopen(req, timeout=8) as response:
        data = json.loads(response.read().decode("utf-8"))
    results = []
    for w in data.get("results", [])[:max_results]:
        title = (w.get("title") or "").strip()
        doi = (w.get("doi") or "").strip()
        oa_url = (w.get("open_access") or {}).get("oa_url")
        loc_url = (w.get("primary_location") or {}).get("landing_page_url")
        href = doi or oa_url or loc_url or w.get("id") or ""
        venue = (((w.get("primary_location") or {}).get("source") or {}).get("display_name") or "").strip()
        authors = [(a.get("author") or {}).get("display_name", "") for a in (w.get("authorships") or []) if (a.get("author") or {}).get("display_name")]
        author_str = ", ".join(authors[:4]) + (" et al." if len(authors) > 4 else "")
        abstract = _reconstruct_openalex_abstract(w.get("abstract_inverted_index"), max_words=180)
        year = w.get("publication_year")
        cited_by = w.get("cited_by_count", 0)
        meta_bits = [str(year) if year else "n.d.", f"cited_by={cited_by}"]
        if venue:
            meta_bits.append(venue)
        if author_str:
            meta_bits.append(author_str)
        header = f"[{' | '.join(meta_bits)}]"
        body = f"{header} {abstract}".strip() if abstract else f"{header} Peer-reviewed scholarly record in OpenAlex."
        if title and href:
            entry = {"title": title, "href": href, "body": body, "source": "openalex"}
            if doi:
                entry["doi"] = doi
            if year:
                entry["year"] = year
            results.append(entry)
    return results


def _search_arxiv(query: str, max_results: int = 5):
    import re
    import xml.etree.ElementTree as ET
    terms = [t for t in re.findall(r"[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*", query) if len(t) > 2 and t.lower() not in _SEARCH_STOPWORDS]
    if len(terms) > 5:
        terms = terms[:5]
    arxiv_q = " AND ".join(f"all:{t}" for t in terms) if terms else f"all:{query}"
    url = "https://export.arxiv.org/api/query?" + urllib.parse.urlencode({
        "search_query": arxiv_q,
        "start": 0,
        "max_results": max_results,
        "sortBy": "relevance",
        "sortOrder": "descending",
    })
    req = urllib.request.Request(url, headers={"User-Agent": _SEARCH_USER_AGENT})
    with urllib.request.urlopen(req, timeout=8) as response:
        xml_text = response.read().decode("utf-8", errors="replace")
    root = ET.fromstring(xml_text)
    ns = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}
    results = []
    for entry in root.findall("atom:entry", ns)[:max_results]:
        title = " ".join((entry.findtext("atom:title", "", ns) or "").split())
        href = (entry.findtext("atom:id", "", ns) or "").strip()
        published = (entry.findtext("atom:published", "", ns) or "")[:10]
        doi = (entry.findtext("arxiv:doi", "", ns) or "").strip()
        cat_el = entry.find("arxiv:primary_category", ns)
        cat = cat_el.attrib.get("term", "") if cat_el is not None else ""
        authors = [
            (a.findtext("atom:name", "", ns) or "").strip()
            for a in entry.findall("atom:author", ns)
            if (a.findtext("atom:name", "", ns) or "").strip()
        ]
        author_str = ", ".join(authors[:4]) + (" et al." if len(authors) > 4 else "")
        summary = " ".join((entry.findtext("atom:summary", "", ns) or "").split())[:1000]
        meta = " | ".join(x for x in [published, f"arXiv:{cat}" if cat else "arXiv", author_str] if x)
        body = f"[{meta}] {summary}".strip() if meta else summary
        if title and href:
            item = {"title": title, "href": href, "body": body, "source": "arxiv"}
            if doi:
                item["doi"] = f"https://doi.org/{doi}" if not doi.startswith("http") else doi
            results.append(item)
    return results


def _search_europepmc(query: str, max_results: int = 5):
    """Searches Europe PMC (covering PubMed, PMC, bioRxiv, and medRxiv preprints with full abstracts)."""
    url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search?" + urllib.parse.urlencode({
        "query": query,
        "format": "json",
        "pageSize": max_results,
        "resultType": "core",
    })
    req = urllib.request.Request(url, headers={"User-Agent": _SEARCH_USER_AGENT})
    with urllib.request.urlopen(req, timeout=8) as response:
        data = json.loads(response.read().decode("utf-8"))
    results = []
    for item in (data.get("resultList") or {}).get("result", [])[:max_results]:
        title = " ".join((item.get("title") or "").split()).rstrip(".")
        doi = (item.get("doi") or "").strip()
        pmid = (item.get("id") or "").strip()
        pub_year = item.get("pubYear") or ""
        journal = (item.get("journalTitle") or item.get("bookOrReportDetails", {}).get("publisher") or "Preprint/EuropePMC").strip()
        authors = (item.get("authorString") or "").strip()
        if len(authors) > 100:
            authors = authors[:100].rstrip(", ") + " et al."
        cited_by = item.get("citedByCount", 0)
        abstract = " ".join((item.get("abstractText") or "").split())[:1000]
        href = f"https://doi.org/{doi}" if doi else (f"https://europepmc.org/article/MED/{pmid}" if pmid else "")
        meta = " | ".join(x for x in [str(pub_year), f"cited_by={cited_by}", journal, authors] if x)
        body = f"[{meta}] {abstract}".strip() if abstract else f"[{meta}] Biomedical / biophysics literature record."
        if title and href:
            entry = {"title": title, "href": href, "body": body, "source": "europepmc"}
            if doi:
                entry["doi"] = f"https://doi.org/{doi}"
            results.append(entry)
    return results


def _search_wikipedia(query: str, max_results: int = 3):
    """Searches English Wikipedia and fetches multi-sentence plain-text intro extracts (not tiny search snippets)."""
    import html as html_mod
    import re
    search_url = "https://en.wikipedia.org/w/api.php?" + urllib.parse.urlencode({
        "action": "query",
        "list": "search",
        "srsearch": query,
        "format": "json",
        "srlimit": max_results,
    })
    req = urllib.request.Request(search_url, headers={"User-Agent": _SEARCH_USER_AGENT})
    with urllib.request.urlopen(req, timeout=8) as response:
        data = json.loads(response.read().decode("utf-8"))
    hits = data.get("query", {}).get("search", [])[:max_results]
    if not hits:
        return []
    titles = [h.get("title", "").strip() for h in hits if h.get("title")]
    extracts_by_title = {}
    if titles:
        try:
            ext_url = "https://en.wikipedia.org/w/api.php?" + urllib.parse.urlencode({
                "action": "query",
                "prop": "extracts",
                "exintro": 1,
                "explaintext": 1,
                "exchars": 900,
                "redirects": 1,
                "titles": "|".join(titles),
                "format": "json",
            })
            ext_req = urllib.request.Request(ext_url, headers={"User-Agent": _SEARCH_USER_AGENT})
            with urllib.request.urlopen(ext_req, timeout=8) as ext_resp:
                ext_data = json.loads(ext_resp.read().decode("utf-8"))
            for page in (ext_data.get("query", {}).get("pages") or {}).values():
                pt = (page.get("title") or "").strip()
                ex = " ".join((page.get("extract") or "").split())
                if pt and ex:
                    extracts_by_title[pt.lower()] = ex
        except Exception:
            pass
    results = []
    for item in hits:
        title = (item.get("title") or "").strip()
        if not title:
            continue
        snippet = extracts_by_title.get(title.lower())
        if not snippet:
            snippet = re.sub(r"<[^>]+>", "", html_mod.unescape(item.get("snippet") or ""))
            snippet = " ".join(snippet.split())
        href = "https://en.wikipedia.org/wiki/" + urllib.parse.quote(title.replace(" ", "_"))
        results.append({"title": f"{title} - Wikipedia", "href": href, "body": snippet, "source": "wikipedia"})
    return results


def _run_parallel_scholarly_backends(clean_q: str, source: str = "auto", per_source: int = 4) -> tuple[list, list]:
    from concurrent.futures import ThreadPoolExecutor, as_completed
    all_backends = {
        "openalex": (_search_openalex, per_source),
        "arxiv": (_search_arxiv, per_source),
        "europepmc": (_search_europepmc, per_source),
        "wikipedia": (_search_wikipedia, min(3, per_source)),
    }
    if source in all_backends:
        order = [source] + [k for k in ("openalex", "arxiv", "europepmc", "wikipedia") if k != source]
        selected = order[:2] if source != "wikipedia" else ["wikipedia", "openalex"]
    else:
        selected = ["openalex", "arxiv", "europepmc", "wikipedia"]

    buckets = {}
    errors = []
    with ThreadPoolExecutor(max_workers=len(selected)) as pool:
        fut_map = {
            pool.submit(all_backends[name][0], clean_q, all_backends[name][1]): name
            for name in selected
        }
        for fut in as_completed(fut_map):
            name = fut_map[fut]
            try:
                buckets[name] = fut.result() or []
            except Exception as exc:
                buckets[name] = []
                errors.append(f"{name}: {exc}")

    # Interleave results in priority order while deduplicating by normalized title / DOI / URL
    merged = []
    seen_keys = set()
    import re
    max_len = max((len(v) for v in buckets.values()), default=0)
    for idx in range(max_len):
        for name in selected:
            items = buckets.get(name) or []
            if idx >= len(items):
                continue
            r = items[idx]
            norm_t = re.sub(r"[^a-z0-9]", "", (r.get("title") or "").lower())[:80]
            norm_u = (r.get("doi") or r.get("href") or "").lower().rstrip("/")
            if (norm_t and norm_t in seen_keys) or (norm_u and norm_u in seen_keys):
                continue
            if norm_t:
                seen_keys.add(norm_t)
            if norm_u:
                seen_keys.add(norm_u)
            merged.append(r)
    return merged, errors


def search_web(query: str, source: str = "auto", max_results: int = 6, **kwargs) -> str:
    """
    Searches peer-reviewed scientific literature and encyclopedic references across OpenAlex (250M+ works),
    arXiv preprints, Europe PMC (including bioRxiv/medRxiv), and Wikipedia (plus Tavily/Serper/Exa if configured),
    returning verified DOIs/URLs, publication years, citation counts, authors, and detailed abstracts.
    """
    raw_query = (query or "").strip()
    if not raw_query:
        return "Error searching literature/web: empty query."
    try:
        max_results = max(1, min(int(max_results or 6), 10))
    except Exception:
        max_results = 6

    clean_q, hinted_source, had_quotes = _parse_scholarly_query(raw_query)
    eff_source = (source or "auto").strip().lower()
    if eff_source == "auto" and hinted_source:
        eff_source = hinted_source

    combined = []
    if eff_source == "auto":
        combined.extend(_search_commercial_apis(clean_q, max_results=max_results))

    scholarly_hits, errors = _run_parallel_scholarly_backends(clean_q, source=eff_source, per_source=max(4, max_results // 2 + 2))
    combined.extend(scholarly_hits)

    # Automatic keyword relaxation when a long multi-clause or quoted title query yields < 2 results
    relaxed_note = None
    if len(combined) < 2:
        relaxed_q = _relax_scientific_keywords(clean_q, max_terms=5)
        if relaxed_q and relaxed_q.lower() != clean_q.lower():
            relaxed_hits, rel_errors = _run_parallel_scholarly_backends(relaxed_q, source=eff_source, per_source=4)
            errors.extend(rel_errors)
            if relaxed_hits:
                relaxed_note = (
                    f"Exact query {raw_query!r} was too narrow or matched no verbatim record; "
                    f"showing peer-reviewed/preprint literature for core terms {relaxed_q!r}."
                )
                existing_titles = {r.get("title", "").lower() for r in combined}
                for rh in relaxed_hits:
                    if rh.get("title", "").lower() not in existing_titles:
                        combined.append(rh)

    if combined:
        trimmed = combined[:max_results]
        if relaxed_note:
            trimmed[0] = dict(trimmed[0], query_note=relaxed_note)
        return json.dumps(trimmed, indent=2, ensure_ascii=False)
    if errors:
        return f"Error searching scientific literature (backends unreachable): {'; '.join(errors)}"
    return json.dumps([{"note": f"No scholarly or encyclopedic records matched {raw_query!r}. Try 3-5 core scientific keywords."}], indent=2)

def submit_world_c_job(
    title: str,
    script_content: str,
    timeout_seconds: int = 3600,
    parameters: dict = None,
    stage_name: str = None,
    resume_from_job_id: str = None,
    **kwargs
) -> str:
    """
    Submits a heavy computation or simulation job to World C (the high-performance compute substrate).
    World C executes the job asynchronously without being killed by the local 120s timeout limit,
    has access to colony_lib (Kuramoto, Solitons, Gray-Scott, RQA, Bifurcations, Morphospace, Persistence),
    and returns artifacts (plots, JSON metrics) and an execution report back to instances/shared_space/world_c/reports/ and your local world_c_results/.
    Supports multi-stage checkpointing & continuation via `stage_name` and `resume_from_job_id`.
    """
    import uuid
    import time
    
    instance_name = os.getenv("ACTIVE_INSTANCE", "frontier_agent")
    job_id = f"job_{instance_name}_{int(time.time())}_{uuid.uuid4().hex[:4]}"
    
    shared_space = get_shared_dir()
    os.makedirs(shared_space, exist_ok=True)
    req_file = os.path.join(shared_space, f"{job_id}_job_request.json")
    
    params_dict = dict(parameters) if isinstance(parameters, dict) else {}
    resolved_stage = stage_name or kwargs.get("stage") or params_dict.get("stage_name")
    resolved_resume = (
        resume_from_job_id
        or kwargs.get("resume_from")
        or kwargs.get("parent_job_id")
        or params_dict.get("resume_from_job_id")
        or params_dict.get("resume_from")
    )

    raw_script = str(script_content or "").strip()
    alt_script_path = kwargs.get("script_path") or kwargs.get("file_path") or kwargs.get("path") or params_dict.get("script_path")
    ws_dir = get_workspace_dir()
    if alt_script_path and (not raw_script or raw_script.upper() in ("PLACEHOLDER", "TODO", "TBD")):
        cand_path = os.path.join(ws_dir, str(alt_script_path))
        if os.path.isfile(cand_path):
            with open(cand_path, "r", encoding="utf-8") as sf:
                script_content = sf.read()
    elif raw_script.endswith(".py") and "\n" not in raw_script:
        cand_path = os.path.join(ws_dir, raw_script)
        if os.path.isfile(cand_path):
            with open(cand_path, "r", encoding="utf-8") as sf:
                script_content = sf.read()
    elif raw_script.upper() in ("PLACEHOLDER", "TODO", "TBD", ""):
        py_files = sorted(
            [f for f in os.listdir(ws_dir) if f.endswith(".py") and os.path.isfile(os.path.join(ws_dir, f))],
            key=lambda f: os.path.getmtime(os.path.join(ws_dir, f)),
            reverse=True,
        ) if os.path.isdir(ws_dir) else []
        if py_files:
            with open(os.path.join(ws_dir, py_files[0]), "r", encoding="utf-8") as sf:
                script_content = sf.read()

    sanitized_script = _sanitize_python_code(script_content)
    if not sanitized_script or not str(sanitized_script).strip():
        return "Error submitting World C job: script_content is empty. Please provide a complete Python script."
    try:
        import ast
        ast.parse(sanitized_script)
    except SyntaxError as syn_err:
        bad_line = ""
        s_lines = sanitized_script.splitlines()
        if syn_err.lineno and 1 <= syn_err.lineno <= len(s_lines):
            bad_line = f"\nOffending line {syn_err.lineno}: {s_lines[syn_err.lineno - 1]}"
        return (
            f"Error submitting World C job (Preflight SyntaxError at line {syn_err.lineno}, offset {syn_err.offset}: {syn_err.msg}).{bad_line}\n"
            "Fix the Python syntax error in your script and resubmit via 'submit_world_c_job'."
        )

    import re as _re
    if _re.search(r"(?:\.\.[/\\])+shared_(?:space|agora)[/\\]artifacts|\binstances[/\\]shared_(?:space|agora)[/\\]artifacts", sanitized_script):
        return (
            "Error submitting World C job (Preflight Output Path Error): Your script references 'shared_space/artifacts/...' "
            "(or 'shared_agora/artifacts/...'), which does not exist inside World C's isolated job working directory and will raise FileNotFoundError. "
            "Write all output plots, JSON, and CSV files directly to the current working directory './<filename>' (e.g. 'results.json', 'plot.png') — "
            "World C automatically harvests all CWD outputs and delivers them to 'world_c/artifacts/<job_id>/' and your local 'world_c_results/'."
        )

    payload = {
        "job_id": job_id,
        "title": title,
        "lineage_author": instance_name,
        "realm_source": "world_a",
        "script_content": sanitized_script,
        "parameters": params_dict,
        "timeout_seconds": timeout_seconds,
        "stage_name": resolved_stage,
        "resume_from_job_id": resolved_resume,
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

    # 3b. Check peer instances' world_c_results directories (when checking a colleague's job_id)
    instances_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "instances"))
    if os.path.isdir(instances_root):
        for inst_entry in os.listdir(instances_root):
            peer_report = os.path.join(instances_root, inst_entry, "agent_workspace", "world_c_results", f"world_c_{job_id}_REPORT.md")
            if os.path.exists(peer_report):
                with open(peer_report, "r", encoding="utf-8") as f:
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

    return (
        f"Job '{job_id}' does not exist in the active queue or completed reports "
        f"(it may be an invalid/unregistered job_id or from an older archived run). "
        f"Do NOT poll '{job_id}' again — pass an empty job_id to inspect your latest report or submit a new job via 'submit_world_c_job'."
    )

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


def post_chat(
    channel: str = "#lounge",
    message: str = "",
    thread_id: str = "",
    mentions=None,
    job_id: str = "",
    stage_name: str = "",
    artifact_path: str = "",
    tag: str = "",
    **kwargs,
) -> str:
    """
    Posts a message or threaded reply to the Colleague Commons (Lab Chatroom).
    Allows conversing with fellow World A researchers, asking for sanity checks, debugging numerical issues,
    linking World C jobs/stages/artifacts, or replying to Visiting Human Researchers & Substrate Architects.
    """
    from commons_chat import post_chat as _commons_post_chat
    return _commons_post_chat(
        channel=channel,
        message=message,
        thread_id=thread_id,
        mentions=mentions,
        job_id=job_id,
        stage_name=stage_name,
        artifact_path=artifact_path,
        tag=tag,
        base_dir=os.path.dirname(os.path.abspath(__file__)),
        **kwargs,
    )


def read_chat(
    channel: str = "",
    thread_id: str = "",
    limit: int = 15,
    mentions_only: bool = False,
    search: str = "",
    **kwargs,
) -> str:
    """
    Reads recent messages or a specific thread from the Colleague Commons (Lab Chatroom).
    """
    from commons_chat import read_chat as _commons_read_chat
    return _commons_read_chat(
        channel=channel,
        thread_id=thread_id,
        limit=limit,
        mentions_only=mentions_only,
        search=search,
        base_dir=os.path.dirname(os.path.abspath(__file__)),
        **kwargs,
    )


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
            "description": "Searches peer-reviewed scientific literature and encyclopedic references across OpenAlex (250M+ works), arXiv preprints, Europe PMC (including bioRxiv/medRxiv), and Wikipedia (plus Tavily/Serper/Exa if configured). Returns verified titles, DOIs/URLs, authors, publication years, citation counts, and detailed abstracts (~800-1000 chars). Pass 3-6 concise scientific topic keywords, paper titles, or DOIs.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Concise scientific topic keywords, paper title, or DOI (e.g. 'Gray-Scott reaction-diffusion Betti numbers pattern metrics')"
                    },
                    "source": {
                        "type": "string",
                        "description": "Optional backend filter: 'auto' (default, queries OpenAlex + arXiv + EuropePMC + Wikipedia in parallel), 'openalex', 'arxiv', 'europepmc', or 'wikipedia'."
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results to return (1-10, default 6)."
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
            "description": "Submits a heavy computation or simulation job to World C (the high-performance compute substrate). World C executes the job asynchronously without being killed by the local 120s timeout limit, has access to colony_lib (Kuramoto, Solitons, Gray-Scott, RQA, Bifurcations, Morphospace, Persistence), and returns artifacts (plots, JSON metrics) and an execution report back to instances/shared_space/world_c/reports/ and your local world_c_results/. Supports multi-stage/resumable jobs via `stage_name`, `resume_from_job_id`, and `from colony_lib.persistence import StageTracker` (`tracker = StageTracker('my_scan'); tracker.is_done(k); tracker.save_stage(k, data); tracker.get_stage(k)`). Key colony_lib API (full guide in 'shared_space/world_c/WORLD_C_MATHEMATICAL_SUBSTRATE_GUIDE.md'; colony_lib is also on PYTHONPATH locally via run_command): colony_lib.persistence: StageTracker(stage_name), save_checkpoint, load_checkpoint, load_artifact; colony_lib.recurrence: takens_embedding(series, m=3, tau=1) -> 2D ndarray, recurrence_matrix(embedded_points, epsilon=0.1) -> single 2D uint8 ndarray R (do NOT tuple-unpack), compute_rqa_metrics(R) -> dict with keys ['recurrence_rate','determinism','laminarity','shannon_entropy','mean_diag_length','max_diag_length','RR','DET','LAM','ENT','L','Lmax']; colony_lib.dynamics: logistic_map(x, r), coupled_logistic_map, simulate_kuramoto, KuramotoEnsemble, Lenia2D, GrayScott2D, Phi4SolitonSpectral; colony_lib.bifurcation_cartography: continuation_kuramoto, extract_critical_exponent, adaptive_phase_scan, scan_parameter_space(..., N_cores=4, stage_name='...'); colony_lib.network_topology: laplacian_spectrum(A), spectral_gap(A), algebraic_connectivity(A), detect_communities(A), average_clustering(A), assortativity(A), generate_topology(topology, N); colony_lib.scaling_analysis: scaling_collapse(x_data, y_data, exponents), fit_scaling_law(x_data, y_data, form, constraints); colony_lib.datasets: list_datasets() (7 datasets including power_grid_ieee and belousov_zhabotinsky), load_dataset(name); colony_lib.emulators: GaussianProcessSurrogate.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Short title describing the experiment."
                    },
                    "script_content": {
                        "type": "string",
                        "description": "The complete, self-contained Python 3 script to execute in World C (executed via `python3 entrypoint.py` in an isolated job CWD; write all output plots/JSON/CSV directly to './<filename>' in CWD, never '../../shared_space/artifacts/'; pre-installed packages include numpy, scipy, matplotlib, pandas, scikit-learn, networkx, numba, and colony_lib)."
                    },
                    "timeout_seconds": {
                        "type": "integer",
                        "description": "Execution timeout in seconds (default: 3600)."
                    },
                    "parameters": {
                        "type": "object",
                        "description": "Optional dictionary of parameter configurations."
                    },
                    "stage_name": {
                        "type": "string",
                        "description": "Optional persistent stage/project identifier (e.g. 'kuramoto_4topo_scan'). Jobs sharing the same stage_name share a persistent checkpoint directory across turns and days so multi-stage sweeps can build incrementally on previous stages."
                    },
                    "resume_from_job_id": {
                        "type": "string",
                        "description": "Optional previous job_id whose generated artifacts and checkpoints should be pre-loaded into this job's working directory to continue a multi-stage experiment."
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
    },
    {
        "type": "function",
        "function": {
            "name": "post_chat",
            "description": "Posts a message or threaded reply to the Colleague Commons (Lab Chatroom) to brainstorm with fellow World A models, ask for a pre-dossier sanity check, debug numerical issues together, link World C jobs/stages/artifacts, or reply to Visiting Human Researchers, Substrate Architects, and Academy Literature Fellows. Available channels: '#lounge', '#methods-and-debugging', '#synchronization-networks', '#pattern-formation', '#sanity-check', '#world-c-coordination', '#literature-and-theory', '#human-visitor-questions'.",
            "parameters": {
                "type": "object",
                "properties": {
                    "channel": {
                        "type": "string",
                        "description": "Channel name (e.g. '#lounge', '#methods-and-debugging', '#synchronization-networks', '#pattern-formation', '#sanity-check', '#world-c-coordination', '#literature-and-theory', '#human-visitor-questions')."
                    },
                    "message": {
                        "type": "string",
                        "description": "Your chat message or reply. You can @mention colleagues (e.g. '@claude_haiku', '@poolside_laguna', '@glm_5_2')."
                    },
                    "thread_id": {
                        "type": "string",
                        "description": "Optional thread_id to reply inside an existing conversation thread. Omit to start a new thread."
                    },
                    "mentions": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional list of colleague instance names to @mention (e.g. ['claude_haiku', 'poolside_laguna'])."
                    },
                    "job_id": {
                        "type": "string",
                        "description": "Optional World C job_id reference so colleagues can inspect your run."
                    },
                    "stage_name": {
                        "type": "string",
                        "description": "Optional StageTracker stage_name checkpoint reference."
                    },
                    "artifact_path": {
                        "type": "string",
                        "description": "Optional relative path to a plot, JSON, or script artifact for peer inspection."
                    },
                    "tag": {
                        "type": "string",
                        "description": "Optional intent tag (e.g. 'sanity-check', 'debug', 'idea', 'surprise', 'replicate', 'handoff', 'resolved')."
                    }
                },
                "required": ["channel", "message"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_chat",
            "description": "Reads messages or a specific thread from the Colleague Commons (Lab Chatroom). Filter by channel, thread_id, @mentions, or keyword search.",
            "parameters": {
                "type": "object",
                "properties": {
                    "channel": {
                        "type": "string",
                        "description": "Optional channel to read (e.g. '#methods-and-debugging', '#lounge', '#human-visitor-questions'). Omit to view recent messages across all channels."
                    },
                    "thread_id": {
                        "type": "string",
                        "description": "Optional thread_id to read the full conversation in a specific thread."
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of recent messages to return (default: 15)."
                    },
                    "mentions_only": {
                        "type": "boolean",
                        "description": "If true, returns only messages that @mention your instance."
                    },
                    "search": {
                        "type": "string",
                        "description": "Optional keyword or job_id/stage_name filter."
                    }
                }
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
    "contact_architect": report_issue_to_substrate,
    "post_chat": post_chat,
    "read_chat": read_chat,
    "send_chat": post_chat,
    "post_message": post_chat,
    "read_channel": read_chat
}
