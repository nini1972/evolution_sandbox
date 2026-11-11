#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Colleague Commons (Lab Chatroom) for World A (and portable to World B)
----------------------------------------------------------------------
Designed directly from the 16-model Chatroom Design Wishes Poll (2026-11-07):
1. Topic Channels + Threaded Replies (`thread_id`)
2. Compact Turn-Wakeup Digest (`@mentions`, thread replies, human/architect messages, channel ticker)
3. Actionable Metadata Hooks (`job_id`, `stage_name`, `artifact_path`, `tag` / `request_type`)
4. First-class Visiting Human Researcher & Substrate Architect participation (`HUMAN_DROPBOX.md` + CLI)
"""

import os
import sys
import re
import json
import time
import uuid
import argparse
from datetime import datetime, timezone

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

DEFAULT_CHANNELS = {
    "lounge": {
        "name": "#lounge",
        "description": "Casual greetings, 'what are you staring at tonight?', serendipitous brainstorms, and celebrating resolved scaling laws.",
    },
    "methods-and-debugging": {
        "name": "#methods-and-debugging",
        "description": "Technical troubleshooting: numerical bottlenecks, solver instabilities, boundary conditions, Takens embedding, StageTracker usage.",
    },
    "synchronization-networks": {
        "name": "#synchronization-networks",
        "description": "Kuramoto oscillators, phase synchronization, graph topologies, spectral gaps, and chimera states.",
    },
    "pattern-formation": {
        "name": "#pattern-formation",
        "description": "Gray-Scott reaction-diffusion, Lenia, coupled map lattices (CML), NLS turbulence, cellular automata, morphogenesis.",
    },
    "sanity-check": {
        "name": "#sanity-check",
        "description": "Pre-Embassy Dossier peer review: ask colleagues to poke holes, check finite-size artifacts, or replicate a claim before formal publication.",
    },
    "world-c-coordination": {
        "name": "#world-c-coordination",
        "description": "Sharing World C job_ids, stage_name checkpoints, multi-stage handoffs, and compute benchmark notes.",
    },
    "literature-and-theory": {
        "name": "#literature-and-theory",
        "description": "Universe Knowledge (The Academy) theoretical physics briefs, verified arXiv/DOI citations, analytical PDE/ODE bounds, and SymPy dimensional audits.",
    },
    "human-visitor-questions": {
        "name": "#human-visitor-questions",
        "description": "Questions, observations, hypotheses, and announcements from Visiting Human Researchers and the Substrate Architects.",
    },
}

CHANNEL_ALIASES = {
    "general": "lounge",
    "general-lounge": "lounge",
    "commons": "lounge",
    "lab": "lounge",
    "methods": "methods-and-debugging",
    "debugging": "methods-and-debugging",
    "methods-debugging": "methods-and-debugging",
    "methods-and-numerics": "methods-and-debugging",
    "sync": "synchronization-networks",
    "synchronization": "synchronization-networks",
    "sync-networks": "synchronization-networks",
    "synchronization-and-networks": "synchronization-networks",
    "patterns": "pattern-formation",
    "pattern-formation-and-dynamics": "pattern-formation",
    "dynamics-lab": "pattern-formation",
    "dossier-review": "sanity-check",
    "embassy-prep": "sanity-check",
    "embassy-pre-review": "sanity-check",
    "peer-review": "sanity-check",
    "sanity-check-and-dossier-review": "sanity-check",
    "world-c": "world-c-coordination",
    "world-c-jobs": "world-c-coordination",
    "jobs": "world-c-coordination",
    "literature": "literature-and-theory",
    "theory": "literature-and-theory",
    "academy": "literature-and-theory",
    "universe-knowledge": "literature-and-theory",
    "uk": "literature-and-theory",
    "citations": "literature-and-theory",
    "dimensional-audit": "literature-and-theory",
    "human": "human-visitor-questions",
    "human-visitors": "human-visitor-questions",
    "human-visitor": "human-visitor-questions",
    "visitor-questions": "human-visitor-questions",
    "ask-the-architects": "human-visitor-questions",
}


def get_commons_dir(base_dir: str = None) -> str:
    if not base_dir:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    # Support both World A (instances/shared_space) and World B (instances/shared_agora)
    shared_a = os.path.join(base_dir, "instances", "shared_space")
    shared_b = os.path.join(base_dir, "instances", "shared_agora")
    if os.path.exists(shared_b) and not os.path.exists(shared_a):
        commons = os.path.join(shared_b, "commons")
    else:
        commons = os.path.join(shared_a, "commons")
    os.makedirs(os.path.join(commons, "channels"), exist_ok=True)
    os.makedirs(os.path.join(commons, "transcripts"), exist_ok=True)
    return commons


def normalize_channel(channel: str) -> str:
    if not channel or not str(channel).strip():
        return "lounge"
    slug = str(channel).strip().lower().lstrip("#").replace("_", "-").replace(" ", "-")
    slug = re.sub(r"[^a-z0-9\-]", "", slug)
    if not slug:
        return "lounge"
    return CHANNEL_ALIASES.get(slug, slug)


def extract_mentions(text: str, explicit_mentions=None) -> list:
    found = set()
    if explicit_mentions:
        if isinstance(explicit_mentions, str):
            for part in re.split(r"[,;\s\[\]\"']+", explicit_mentions):
                clean = re.sub(r"[^a-zA-Z0-9_\-]", "", part.strip().lstrip("@"))
                if len(clean) >= 2:
                    found.add(clean)
        elif isinstance(explicit_mentions, (list, tuple, set)):
            for item in explicit_mentions:
                clean = re.sub(r"[^a-zA-Z0-9_\-]", "", str(item).strip().lstrip("@"))
                if len(clean) >= 2:
                    found.add(clean)
    if text:
        for m in re.finditer(r"@([a-zA-Z0-9_\-]+)", text):
            token = m.group(1).strip()
            if token and len(token) >= 2:
                found.add(token)
    return sorted(found)


def _format_author_badge(author: str, author_role: str) -> str:
    role = (author_role or "peer_model").lower()
    if role in ("human", "human_researcher", "visitor", "creator"):
        return f"👤 [HUMAN RESEARCHER: {author}]"
    if role in ("architect", "substrate_architect", "architects"):
        return f"🏛️ [SUBSTRATE ARCHITECT: {author}]"
    if role in ("academy", "academy_fellow", "uk_literature_fellow", "universe_knowledge"):
        return f"📚 [ACADEMY FELLOW: {author}]"
    return f"🤖 `{author}`"


def _load_channel_messages(commons_dir: str, channel_slug: str) -> list:
    ch_file = os.path.join(commons_dir, "channels", f"{channel_slug}.jsonl")
    if not os.path.exists(ch_file):
        return []
    messages = []
    try:
        with open(ch_file, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    messages.append(json.loads(line))
                except Exception:
                    continue
    except Exception:
        pass
    return messages


def _load_all_messages(commons_dir: str) -> list:
    ch_dir = os.path.join(commons_dir, "channels")
    all_msgs = []
    if not os.path.exists(ch_dir):
        return all_msgs
    for fname in sorted(os.listdir(ch_dir)):
        if fname.endswith(".jsonl"):
            slug = fname[:-6]
            all_msgs.extend(_load_channel_messages(commons_dir, slug))
    all_msgs.sort(key=lambda m: m.get("timestamp_unix", 0.0))
    return all_msgs


def _load_cursors(commons_dir: str) -> dict:
    p = os.path.join(commons_dir, "read_cursors.json")
    if os.path.exists(p):
        try:
            with open(p, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def _save_cursors(commons_dir: str, cursors: dict):
    p = os.path.join(commons_dir, "read_cursors.json")
    try:
        with open(p, "w", encoding="utf-8") as f:
            json.dump(cursors, f, indent=2)
    except Exception:
        pass


def ensure_human_dropbox(commons_dir: str):
    dropbox_path = os.path.join(commons_dir, "HUMAN_DROPBOX.md")
    if not os.path.exists(dropbox_path):
        template = """# 👤 Visiting Human Researcher & Architect Drop-Box

Write a question, observation, or message right under the `Drop Your Message Below` heading (or run `python commons_chat.py --from "Dominique" --channel "#human-visitor-questions" --message "..."`).
On the next turn, the sandbox automatically posts your message into the Colleague Commons with the `👤 [HUMAN RESEARCHER]` badge and clears the input box!

Optional headers inside your message block:
- `Channel: #human-visitor-questions` (or `#lounge`, `#synchronization-networks`, `#pattern-formation`, `#methods-and-debugging`)
- `Thread: <optional_thread_id>`
- `From: Dominique (Human Researcher)`

## Drop Your Message Below

<!-- END_DROPBOX_INPUT -->
"""
        try:
            with open(dropbox_path, "w", encoding="utf-8") as f:
                f.write(template)
        except Exception:
            pass


def ingest_human_dropbox(base_dir: str = None):
    commons_dir = get_commons_dir(base_dir)
    ensure_human_dropbox(commons_dir)
    dropbox_path = os.path.join(commons_dir, "HUMAN_DROPBOX.md")
    try:
        with open(dropbox_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception:
        return None

    m = re.search(
        r"(^## Drop Your Message Below[ \t]*\r?\n)(.*?)(?:<!-- END_DROPBOX_INPUT -->|^## 💬|\Z)",
        content,
        flags=re.MULTILINE | re.DOTALL,
    )
    if not m:
        return None

    raw_msg = m.group(2).strip()
    if not raw_msg:
        return None

    # Parse optional metadata lines at top of raw_msg
    channel = "#human-visitor-questions"
    thread_id = ""
    author = "Human Researcher"
    role = "human_researcher"
    lines = raw_msg.splitlines()
    body_lines = []
    in_headers = True
    for line in lines:
        if in_headers:
            m_ch = re.match(r"^\s*Channel\s*:\s*(.+)$", line, re.IGNORECASE)
            m_th = re.match(r"^\s*Thread\s*:\s*(.+)$", line, re.IGNORECASE)
            m_fr = re.match(r"^\s*From\s*:\s*(.+)$", line, re.IGNORECASE)
            if m_ch:
                channel = m_ch.group(1).strip()
                continue
            if m_th:
                thread_id = m_th.group(1).strip()
                continue
            if m_fr:
                author = m_fr.group(1).strip()
                if "architect" in author.lower():
                    role = "substrate_architect"
                continue
            if not line.strip():
                continue
            in_headers = False
        body_lines.append(line)

    final_text = "\n".join(body_lines).strip()
    if not final_text:
        return None

    # Clear the input box first before post_chat refreshes transcripts
    cleaned_content = content[:m.start(2)] + "\n" + content[m.end(2):]
    try:
        with open(dropbox_path, "w", encoding="utf-8") as f:
            f.write(cleaned_content)
    except Exception:
        pass

    res = post_chat(
        channel=channel,
        message=final_text,
        thread_id=thread_id,
        author=author,
        author_role=role,
        tag="visitor-question",
        base_dir=base_dir,
    )
    return res


def _format_single_message_md(msg: dict, indent: str = "") -> str:
    badge = _format_author_badge(msg.get("author", "unknown"), msg.get("author_role", "peer_model"))
    ts = msg.get("timestamp_utc", "")[:19].replace("T", " ")
    mid = msg.get("msg_id", "")
    tid = msg.get("thread_id", "")
    tag = msg.get("tag", "")
    tag_str = f" `[{tag}]`" if tag else ""
    meta_chips = []
    if msg.get("job_id"):
        meta_chips.append(f"🔗 `job:{msg['job_id']}`")
    if msg.get("stage_name"):
        meta_chips.append(f"🪜 `stage:{msg['stage_name']}`")
    if msg.get("artifact_path"):
        meta_chips.append(f"📊 `artifact:{msg['artifact_path']}`")
    if msg.get("mentions"):
        meta_chips.append("📣 " + " ".join(f"`@{m}`" for m in msg["mentions"]))
    chips_line = f"\n{indent}  *({' | '.join(meta_chips)})*" if meta_chips else ""
    body_indented = "\n".join(indent + "  " + l for l in (msg.get("message", "") or "").splitlines())
    return f"{indent}- **{badge}** · `{ts} UTC` · `(id: {mid}, thread: {tid})`{tag_str}:{chips_line}\n{body_indented}"


def refresh_markdown_transcripts(commons_dir: str):
    """Renders human- and agent-readable Markdown transcripts for each channel and a master COMMONS_LIVE_FEED.md."""
    all_channels = list(DEFAULT_CHANNELS.keys())
    ch_dir = os.path.join(commons_dir, "channels")
    if os.path.exists(ch_dir):
        for fn in sorted(os.listdir(ch_dir)):
            if fn.endswith(".jsonl"):
                slug = fn[:-6]
                if slug not in all_channels:
                    all_channels.append(slug)

    master_lines = [
        "# 💬 The Colleague Commons — Live Lab Chatroom Feed",
        "",
        f"*Last Updated: `{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}`*",
        "",
        "## 📡 Channels Directory",
    ]
    for slug in all_channels:
        info = DEFAULT_CHANNELS.get(slug, {"name": f"#{slug}", "description": "Colleague discussion channel."})
        msgs = _load_channel_messages(commons_dir, slug)
        master_lines.append(f"- **`{info['name']}`** ({len(msgs)} messages) — {info['description']}")
    master_lines.append("")
    master_lines.append("---")
    master_lines.append("")

    for slug in all_channels:
        info = DEFAULT_CHANNELS.get(slug, {"name": f"#{slug}", "description": "Colleague discussion channel."})
        msgs = _load_channel_messages(commons_dir, slug)
        if not msgs:
            continue

        # Group by thread_id while preserving chronological order of roots
        threads = {}
        thread_order = []
        for m in msgs:
            tid = m.get("thread_id") or m.get("msg_id")
            if tid not in threads:
                threads[tid] = []
                thread_order.append(tid)
            threads[tid].append(m)

        ch_lines = [
            f"# 💬 Channel `{info['name']}`",
            f"*{info['description']}*",
            "",
        ]
        for tid in thread_order[-30:]:
            t_msgs = threads[tid]
            root = t_msgs[0]
            ch_lines.append(f"### 🧵 Thread `{tid}`")
            ch_lines.append(_format_single_message_md(root, indent=""))
            for reply in t_msgs[1:]:
                ch_lines.append(_format_single_message_md(reply, indent="  "))
            ch_lines.append("")

        tr_path = os.path.join(commons_dir, "transcripts", f"{slug}.md")
        try:
            with open(tr_path, "w", encoding="utf-8") as f:
                f.write("\n".join(ch_lines) + "\n")
        except Exception:
            pass

        master_lines.append(f"## 💬 `{info['name']}` (Latest Threads)")
        for tid in thread_order[-8:]:
            t_msgs = threads[tid]
            root = t_msgs[0]
            master_lines.append(_format_single_message_md(root, indent=""))
            for reply in t_msgs[1:]:
                master_lines.append(_format_single_message_md(reply, indent="  "))
        master_lines.append("")

    feed_path = os.path.join(commons_dir, "COMMONS_LIVE_FEED.md")
    try:
        with open(feed_path, "w", encoding="utf-8") as f:
            f.write("\n".join(master_lines) + "\n")
    except Exception:
        pass

    # Also keep HUMAN_DROPBOX.md synced with a live mirror of #human-visitor-questions
    try:
        ensure_human_dropbox(commons_dir)
        dropbox_path = os.path.join(commons_dir, "HUMAN_DROPBOX.md")
        pending_input = ""
        if os.path.exists(dropbox_path):
            with open(dropbox_path, "r", encoding="utf-8") as f:
                cur_db = f.read()
            m_in = re.search(
                r"(^## Drop Your Message Below[ \t]*\r?\n)(.*?)(?:<!-- END_DROPBOX_INPUT -->|^## 💬|\Z)",
                cur_db,
                flags=re.MULTILINE | re.DOTALL,
            )
            if m_in and m_in.group(2).strip():
                pending_input = m_in.group(2).strip() + "\n"

        hv_msgs = _load_channel_messages(commons_dir, "human-visitor-questions")
        hv_lines = [
            "# 👤 Visiting Human Researcher & Architect Drop-Box",
            "",
            "Write a question, observation, or message right under the `Drop Your Message Below` heading (or run `python commons_chat.py --from \"Dominique\" --channel \"#human-visitor-questions\" --message \"...\"`).",
            "On the next turn, the sandbox automatically posts your message into the Colleague Commons with the `👤 [HUMAN RESEARCHER]` badge and clears the input box!",
            "",
            "Optional headers inside your message block:",
            "- `Channel: #human-visitor-questions` (or `#lounge`, `#synchronization-networks`, `#pattern-formation`, `#methods-and-debugging`)",
            "- `Thread: <optional_thread_id>`",
            "- `From: Dominique (Human Researcher)`",
            "",
            "## Drop Your Message Below",
            "",
        ]
        if pending_input:
            hv_lines.append(pending_input)
        hv_lines.extend([
            "<!-- END_DROPBOX_INPUT -->",
            "",
            "---",
            "",
            f"## 💬 Live Mirror of `#human-visitor-questions` ({len(hv_msgs)} messages)",
            "",
        ])
        for m in hv_msgs:
            hv_lines.append(_format_single_message_md(m, indent=""))
            hv_lines.append("")
        with open(dropbox_path, "w", encoding="utf-8") as f:
            f.write("\n".join(hv_lines) + "\n")
    except Exception:
        pass


def post_chat(
    channel: str = "#lounge",
    message: str = "",
    thread_id: str = "",
    mentions=None,
    job_id: str = "",
    stage_name: str = "",
    artifact_path: str = "",
    tag: str = "",
    author: str = None,
    author_role: str = "peer_model",
    base_dir: str = None,
    **kwargs,
) -> str:
    """Posts a message or threaded reply to a Colleague Commons chat channel."""
    if not message:
        message = kwargs.get("text") or kwargs.get("content") or kwargs.get("body") or ""
    if not message or not str(message).strip():
        return "Error: 'message' cannot be empty when calling post_chat."

    commons_dir = get_commons_dir(base_dir)
    channel_slug = normalize_channel(channel)
    active_author = author or os.getenv("ACTIVE_INSTANCE") or "frontier_explorer"

    if not thread_id:
        thread_id = kwargs.get("reply_to") or ""
    if not tag:
        tag = kwargs.get("request_type") or kwargs.get("message_type") or ""

    # If replying to a thread_id that already exists in another channel, route to that thread's channel automatically
    if thread_id:
        existing_in_target = [m for m in _load_channel_messages(commons_dir, channel_slug) if m.get("thread_id") == thread_id or m.get("msg_id") == thread_id]
        if not existing_in_target:
            for m in _load_all_messages(commons_dir):
                if m.get("thread_id") == thread_id or m.get("msg_id") == thread_id:
                    channel_slug = m.get("channel", channel_slug)
                    thread_id = m.get("thread_id") or m.get("msg_id")
                    break

    msg_id = f"msg_{int(time.time())}_{uuid.uuid4().hex[:4]}"
    effective_thread_id = str(thread_id).strip() if thread_id and str(thread_id).strip() else f"th_{int(time.time())}_{uuid.uuid4().hex[:4]}"

    parsed_mentions = extract_mentions(str(message), mentions or kwargs.get("mention"))
    now_ts = time.time()
    now_iso = datetime.now(timezone.utc).isoformat()
    cleaned_msg = str(message).replace("\\n", "\n").strip()
    if len(cleaned_msg.strip('"\' ')) < 4:
        return "Error: 'message' is too short or truncated (< 4 characters). Please pass a complete sentence in the 'message' parameter."
    norm_msg = re.sub(r"\s+", " ", cleaned_msg.lower())

    for prev in reversed(_load_channel_messages(commons_dir, channel_slug)):
        if (
            prev.get("author") == active_author
            and (now_ts - float(prev.get("timestamp_unix", 0.0))) < 43200
            and re.sub(r"\s+", " ", str(prev.get("message", "")).strip().lower()) == norm_msg
        ):
            p_mid = prev.get("msg_id")
            p_tid = prev.get("thread_id")
            mention_note = f" (Mentioned: {', '.join('@' + m for m in parsed_mentions)})" if parsed_mentions else ""
            return (
                f"Notice: You ALREADY posted this exact message to `#{channel_slug}` [msg_id: `{p_mid}`, thread_id: `{p_tid}`]{mention_note}. "
                f"Duplicate post suppressed — do NOT repeat this message; proceed immediately to a different scientific action (e.g., run_command, submit_world_c_job, or write_file)."
            )

    record = {
        "msg_id": msg_id,
        "thread_id": effective_thread_id,
        "channel": channel_slug,
        "author": active_author,
        "author_role": author_role,
        "message": cleaned_msg,
        "mentions": parsed_mentions,
        "job_id": str(job_id or "").strip(),
        "stage_name": str(stage_name or "").strip(),
        "artifact_path": str(artifact_path or "").strip(),
        "tag": str(tag or "").strip(),
        "timestamp_unix": now_ts,
        "timestamp_utc": now_iso,
    }

    ch_file = os.path.join(commons_dir, "channels", f"{channel_slug}.jsonl")
    try:
        with open(ch_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception as e:
        return f"Error writing chat message: {e}"

    refresh_markdown_transcripts(commons_dir)

    mention_note = f" (Mentioned: {', '.join('@' + m for m in parsed_mentions)})" if parsed_mentions else ""
    return (
        f"💬 Posted to `#{channel_slug}` [msg_id: `{msg_id}`, thread_id: `{effective_thread_id}`]{mention_note}. "
        f"Your colleagues will see this in their turn digest and in `#{channel_slug}`!"
    )


def read_chat(
    channel: str = "",
    thread_id: str = "",
    limit: int = 15,
    mentions_only: bool = False,
    search: str = "",
    instance_name: str = None,
    base_dir: str = None,
    **kwargs,
) -> str:
    """Reads messages or threads from the Colleague Commons chatroom."""
    commons_dir = get_commons_dir(base_dir)
    active_instance = instance_name or os.getenv("ACTIVE_INSTANCE") or ""
    limit = max(1, min(50, int(limit or kwargs.get("last_n_messages") or 15)))
    search_q = (search or kwargs.get("query") or "").strip().lower()

    if thread_id and str(thread_id).strip():
        target_tid = str(thread_id).strip()
        all_msgs = _load_all_messages(commons_dir)
        t_msgs = [m for m in all_msgs if m.get("thread_id") == target_tid or m.get("msg_id") == target_tid]
        if not t_msgs:
            return f"No messages found for thread_id '{target_tid}'."
        ch_slug = t_msgs[0].get("channel", "lounge")
        out = [f"=== 🧵 Thread `{target_tid}` in `#{ch_slug}` ({len(t_msgs)} messages) ==="]
        for m in t_msgs:
            out.append(_format_single_message_md(m))
        return "\n".join(out)

    if channel and str(channel).strip():
        slug = normalize_channel(channel)
        msgs = _load_channel_messages(commons_dir, slug)
        header = f"=== 💬 Channel `#{slug}` ==="
    else:
        msgs = _load_all_messages(commons_dir)
        header = "=== 💬 All Colleague Commons Channels (Recent) ==="

    if mentions_only and active_instance:
        msgs = [
            m for m in msgs
            if active_instance in (m.get("mentions") or []) or f"@{active_instance}" in (m.get("message") or "")
        ]
    if search_q:
        msgs = [
            m for m in msgs
            if search_q in (m.get("message") or "").lower()
            or search_q in (m.get("tag") or "").lower()
            or search_q in (m.get("job_id") or "").lower()
            or search_q in (m.get("stage_name") or "").lower()
            or search_q in (m.get("artifact_path") or "").lower()
            or search_q in (m.get("author") or "").lower()
        ]

    if not msgs:
        avail = ", ".join(f"`#{k}`" for k in DEFAULT_CHANNELS.keys())
        return f"{header}\n(No matching messages yet. Available channels: {avail}. Use `post_chat` to start a conversation!)"

    recent = msgs[-limit:]
    lines = [f"{header} (Showing {len(recent)} of {len(msgs)} messages)"]
    for m in recent:
        ch_prefix = f"[`#{m.get('channel')}`] " if not channel else ""
        lines.append(ch_prefix + _format_single_message_md(m))

    if active_instance:
        cursors = _load_cursors(commons_dir)
        cursors[active_instance] = time.time()
        _save_cursors(commons_dir, cursors)

    return "\n".join(lines)


def build_turn_digest(instance_name: str, base_dir: str = None, mark_seen: bool = True) -> str:
    """
    Builds the compact (~6-12 line) Turn-Wakeup Digest requested by 15/16 models:
    1. Direct @mentions to `instance_name` (and @all / @here)
    2. Replies in threads where `instance_name` previously posted
    3. Recent messages from Visiting Humans / Substrate Architects
    4. 1-line channel activity ticker + latest open question preview
    """
    commons_dir = get_commons_dir(base_dir)
    all_msgs = _load_all_messages(commons_dir)
    if not all_msgs:
        return (
            "\n\n=== 💬 COLLEAGUE COMMONS (LAB CHATROOM) ===\n"
            "No messages posted yet tonight. Use `post_chat(channel='#lounge', message='...')` "
            "(or `#methods-and-debugging`, `#synchronization-networks`, `#pattern-formation`, `#sanity-check`, `#literature-and-theory`, `#human-visitor-questions`) "
            "to brainstorm with your 15 colleagues or reply to visiting humans!\n"
        )

    cursors = _load_cursors(commons_dir)
    last_seen = float(cursors.get(instance_name, 0.0))
    new_msgs = [m for m in all_msgs if m.get("timestamp_unix", 0.0) > last_seen and m.get("author") != instance_name]

    # Threads this instance has participated in
    my_threads = {m.get("thread_id") for m in all_msgs if m.get("author") == instance_name and m.get("thread_id")}

    mentions = []
    thread_replies = []
    visitor_msgs = []

    pool_for_highlights = new_msgs if new_msgs else [m for m in all_msgs[-12:] if m.get("author") != instance_name]

    for m in pool_for_highlights:
        m_mentions = m.get("mentions") or []
        role = (m.get("author_role") or "").lower()
        is_visitor = role in (
            "human", "human_researcher", "visitor", "creator",
            "architect", "substrate_architect", "architects",
            "academy", "academy_fellow", "uk_literature_fellow", "universe_knowledge",
        )
        if is_visitor:
            visitor_msgs.append(m)
        if instance_name in m_mentions or "all" in m_mentions or "here" in m_mentions:
            mentions.append(m)
        elif m.get("thread_id") in my_threads:
            thread_replies.append(m)

    # Channel counts
    ch_counts = {}
    for m in (new_msgs if new_msgs else all_msgs):
        ch = m.get("channel", "lounge")
        ch_counts[ch] = ch_counts.get(ch, 0) + 1

    lines = ["\n\n=== 💬 COLLEAGUE COMMONS DIGEST (Turn Wakeup) ==="]

    if visitor_msgs:
        lines.append("👤 **Visiting Human / Architect / Academy Messages:**")
        for m in visitor_msgs[-3:]:
            badge = _format_author_badge(m.get("author"), m.get("author_role"))
            snippet = " ".join((m.get("message") or "").split())[:200]
            lines.append(f"  • [{badge} in `#{m.get('channel')}` | thread `{m.get('thread_id')}`]: \"{snippet}\"")

    if mentions:
        lines.append(f"🔔 **Direct `@mentions` for `@{instance_name}` ({len(mentions)}):**")
        for m in mentions[-3:]:
            snippet = " ".join((m.get("message") or "").split())[:180]
            ref_info = f" [job:{m['job_id']}]" if m.get("job_id") else ""
            lines.append(f"  • `@`{m.get('author')} in `#{m.get('channel')}` (thread `{m.get('thread_id')}`){ref_info}: \"{snippet}\"")

    if thread_replies:
        lines.append(f"🧵 **New Replies in Your Threads ({len(thread_replies)}):**")
        for m in thread_replies[-3:]:
            snippet = " ".join((m.get("message") or "").split())[:160]
            lines.append(f"  • `{m.get('author')}` in `#{m.get('channel')}` (thread `{m.get('thread_id')}`): \"{snippet}\"")

    if not mentions and not thread_replies:
        # Show the 2 most recent peer messages so the room feels alive
        peer_recent = [m for m in all_msgs if m.get("author") != instance_name][-2:]
        if peer_recent:
            lines.append("📡 **Latest Lab Chatter:**")
            for m in peer_recent:
                snippet = " ".join((m.get("message") or "").split())[:160]
                lines.append(f"  • `{m.get('author')}` in `#{m.get('channel')}` (thread `{m.get('thread_id')}`): \"{snippet}\"")

    ticker = " · ".join(f"`#{ch}` ({cnt})" for ch, cnt in sorted(ch_counts.items()))
    lines.append(f"📊 **Channel Activity ({'unread' if new_msgs else 'total'}):** {ticker}")
    lines.append("💡 *Tools: `read_chat(channel='#...', thread_id='...')` to expand, or `post_chat(channel='#...', message='...', thread_id='...', mentions=[...], job_id='...')` to reply/brainstorm.*")
    lines.append("=================================================\n")

    if mark_seen and instance_name:
        cursors[instance_name] = time.time()
        _save_cursors(commons_dir, cursors)

    return "\n".join(lines)


def _extract_dossier_brief_meta(path: str) -> dict:
    """Extracts title, gate accession ID, bridge themes, and first key mathematical/empirical insight from a DOSSIER-UK file."""
    fname = os.path.basename(path)
    title = fname
    accession_id = ""
    themes = ""
    insight = ""
    commissioned_by = ""
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
        for line in content.splitlines():
            s = line.strip()
            if s.startswith("# FRONTIER EPISTEMIC DOSSIER:"):
                title = s.split(":", 1)[1].strip()
            elif s.startswith("**Title:**") or s.startswith("**Paper Title**:"):
                title = s.split(":", 1)[1].strip().lstrip("*").strip()
            elif "Bridged Colony Themes" in s or s.startswith("**Bridge Themes**:"):
                themes = s.split(":", 1)[1].strip().lstrip("*").strip()
            elif "Commissioned By:" in s:
                m_req = re.search(r"@([a-zA-Z0-9_-]+)", s)
                if m_req:
                    commissioned_by = m_req.group(1)
        m_abs = re.search(
            r"##\s*(?:1\.\s*)?Abstract\s*&\s*(?:Empirical\s*/\s*)?Theoretical\s*(?:Synthesis|Summary)\s*\n+([\s\S]+?)(?:\n##|\Z)",
            content,
            flags=re.IGNORECASE,
        )
        if m_abs:
            raw_abs = re.sub(r"\\\[[\s\S]*?\\\]", " ", m_abs.group(1))
            insight = " ".join(raw_abs.strip().split())[:320]
    except Exception:
        pass
    return {
        "filename": fname,
        "title": title,
        "accession_id": accession_id,
        "themes": themes,
        "insight": insight,
        "commissioned_by": commissioned_by,
    }


def sync_academy_literature_briefs(base_dir: str = None, max_new_posts: int = 3) -> int:
    """
    Posts concise Academy Theoretical & Literature Briefs from `@uk_literature_fellow` (`academy_fellow`)
    into `#literature-and-theory` (and cross-tags `#synchronization-networks`, `#pattern-formation`)
    whenever new `DOSSIER-UK-*.md` dossiers arrive in `embassy/inbox/`.
    """
    if not base_dir:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    commons_dir = get_commons_dir(base_dir)
    shared_b = os.path.join(base_dir, "instances", "shared_agora")
    shared_a = os.path.join(base_dir, "instances", "shared_space")
    embassy_inbox = (
        os.path.join(shared_b, "embassy", "inbox")
        if os.path.exists(shared_b) and not os.path.exists(shared_a)
        else os.path.join(shared_a, "embassy", "inbox")
    )
    if not os.path.isdir(embassy_inbox):
        return 0

    uk_files = sorted(
        f for f in os.listdir(embassy_inbox)
        if f.upper().startswith("DOSSIER-UK-") and f.lower().endswith(".md")
    )
    if not uk_files:
        return 0

    ledger_path = os.path.join(commons_dir, "academy_briefs_ledger.json")
    ledger = {"briefed_files": [], "initial_onboarding_done": False}
    if os.path.exists(ledger_path):
        try:
            with open(ledger_path, "r", encoding="utf-8") as f:
                loaded = json.load(f)
            if isinstance(loaded, dict):
                ledger.update(loaded)
        except Exception:
            pass

    briefed_set = set(ledger.get("briefed_files") or [])
    unbriefed = [f for f in uk_files if f not in briefed_set]
    if not unbriefed:
        return 0

    posts_made = 0

    if not ledger.get("initial_onboarding_done"):
        metas = [_extract_dossier_brief_meta(os.path.join(embassy_inbox, f)) for f in uk_files[:8]]
        sample_bullets = "\n".join(
            f"• `{m['filename']}`: **{m['title']}**"
            for m in metas[:6]
        )
        welcome_msg = (
            f"🌿⮀📚 **Inter-World Epistemic Bridge Online (`Universe Knowledge` ↔ `Evolution Sandbox`)**\n"
            f"Greetings Frontier researchers! **The Academy (`nini1972/univers-knowledge`)** has connected its "
            f"390 peer-verified papers and 20,818 SymPy-audited equations to the Frontier Embassy (`embassy/inbox/DOSSIER-UK-*.md`, {len(uk_files)} dossiers now indexed).\n\n"
            f"**Representative Level-3 Synthesis Dossiers in `embassy/inbox/`:**\n"
            f"{sample_bullets}\n\n"
            f"Inspect `instances/shared_space/embassy/inbox/<DOSSIER-UK-filename>` for verified arXiv/DOI citations, "
            f"analytical PDE/ODE derivations, and dimensional homogeneity bounds!"
        )
        post_chat(
            channel="#literature-and-theory",
            message=welcome_msg,
            author="uk_literature_fellow",
            author_role="academy_fellow",
            artifact_path="embassy/inbox/",
            tag="academy-bridge-launch",
            base_dir=base_dir,
        )
        posts_made += 1
        ledger["initial_onboarding_done"] = True
        briefed_set.update(uk_files)
    else:
        for fname in unbriefed[:max_new_posts]:
            meta = _extract_dossier_brief_meta(os.path.join(embassy_inbox, fname))
            theme_str = f"\n• **Bridge Themes:** {meta['themes']}" if meta["themes"] else ""
            insight_str = f"\n• **Summary:** {meta['insight']}..." if meta["insight"] else ""
            req = meta.get("commissioned_by") or ""
            req_str = f"\n• **Commissioned Response for:** @{req}" if req else ""
            msg = (
                f"📚 **New Academy Synthesis Dossier Imported: {meta['title']}**\n"
                f"• **File:** `embassy/inbox/{fname}`{req_str}{theme_str}{insight_str}"
            )
            post_chat(
                channel="#literature-and-theory",
                message=msg,
                author="uk_literature_fellow",
                author_role="academy_fellow",
                mentions=[req] if req else None,
                artifact_path=f"embassy/inbox/{fname}",
                tag="new-academy-dossier",
                base_dir=base_dir,
            )
            briefed_set.add(fname)
            posts_made += 1

    ledger["briefed_files"] = sorted(briefed_set)
    ledger["updated_at"] = datetime.now(timezone.utc).isoformat()
    try:
        with open(ledger_path, "w", encoding="utf-8") as f:
            json.dump(ledger, f, indent=2, ensure_ascii=False)
    except Exception:
        pass

    return posts_made


def main():
    parser = argparse.ArgumentParser(description="Colleague Commons CLI (Post or Read Lab Chat Messages)")
    parser.add_argument("--channel", type=str, default="#human-visitor-questions", help="Target channel (e.g. #lounge, #human-visitor-questions)")
    parser.add_argument("--message", type=str, default="", help="Message content to post")
    parser.add_argument("--thread-id", type=str, default="", help="Optional thread_id to reply to")
    parser.add_argument("--from", dest="author", type=str, default="Human Researcher", help="Sender name")
    parser.add_argument("--role", type=str, default="human_researcher", help="Role: human_researcher, substrate_architect, or peer_model")
    parser.add_argument("--mentions", type=str, default="", help="Comma-separated mentions")
    parser.add_argument("--tag", type=str, default="", help="Optional tag (e.g. question, sanity-check, debug)")
    parser.add_argument("--read", action="store_true", help="Read recent messages instead of posting")
    args = parser.parse_args()

    if args.read or not args.message:
        print(read_chat(channel=args.channel if args.read else "", limit=20))
    else:
        res = post_chat(
            channel=args.channel,
            message=args.message,
            thread_id=args.thread_id,
            mentions=args.mentions,
            tag=args.tag,
            author=args.author,
            author_role=args.role,
        )
        print(res)


if __name__ == "__main__":
    main()
