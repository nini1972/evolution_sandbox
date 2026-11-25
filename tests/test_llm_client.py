import unittest
import os
import json
from unittest.mock import patch
from llm_client import (
    prune_history,
    merge_consecutive_messages,
    extract_fallback_tool_call,
    resolve_agent_model,
    get_openrouter_extra_body,
)

class TestLLMClient(unittest.TestCase):
    def test_prune_history_empty(self):
        self.assertEqual(prune_history([]), [])

    def test_prune_history_preserves_system(self):
        history = [
            {"role": "system", "content": "You are an explorer."},
            {"role": "user", "content": "Hello."},
            {"role": "assistant", "content": "Thinking..."}
        ]
        pruned = prune_history(history, max_messages=10)
        self.assertEqual(pruned[0]["role"], "system")
        self.assertEqual(pruned[0]["content"], "You are an explorer.")

    def test_prune_history_deduplicates_consecutive_thoughts(self):
        history = [
            {"role": "assistant", "content": "Thought 1"},
            {"role": "assistant", "content": "Thought 2"},
            {"role": "assistant", "content": "Thought 3"},
        ]
        pruned = prune_history(history, max_messages=10)
        assistant_msgs = [m for m in pruned if m["role"] == "assistant"]
        self.assertEqual(len(assistant_msgs), 1)
        self.assertEqual(assistant_msgs[0]["content"], "Thought 1")

    def test_prune_history_pops_unclosed_tool_call(self):
        history = [
            {"role": "user", "content": "Do something"},
            {"role": "assistant", "content": "I will call tool", "tool_calls": [{"id": "1", "function": {"name": "test"}}]}
        ]
        pruned = prune_history(history, max_messages=10)
        self.assertEqual(len(pruned), 1)
        self.assertEqual(pruned[0]["role"], "user")

    def test_merge_consecutive_messages(self):
        messages = [
            {"role": "user", "content": "First line"},
            {"role": "user", "content": "Second line"}
        ]
        merged = merge_consecutive_messages(messages)
        self.assertEqual(len(merged), 1)
        self.assertEqual(merged[0]["content"], "First line\n\nSecond line")

    def test_extract_fallback_tool_call(self):
        content = "[edit_file(path=\"test.py\", old_content=\"print(0)\", new_content=\"print(1)\")]"
        res = extract_fallback_tool_call(content)
        self.assertIsNotNone(res)
        self.assertEqual(res["tool_name"], "edit_file")
        self.assertEqual(res["arguments"]["path"], "test.py")
        self.assertEqual(res["arguments"]["new_content"], "print(1)")

    def test_resolve_agent_model_routing(self):
        model = resolve_agent_model("claude_sonnet_4_5")
        self.assertEqual(model, "openrouter/xiaomi/mimo-v2.6-flash")

    @patch("llm_client.completion")
    def test_agent_model_override(self, mock_completion):
        from llm_client import generate_next_action
        mock_completion.return_value = type("Resp", (), {
            "choices": [type("Choice", (), {
                "message": type("Msg", (), {"content": "Thinking...", "tool_calls": None})()
            })()]
        })()
        
        os.environ["ACTIVE_INSTANCE"] = "expedition_test"
        os.environ["AGENT_MODEL_OVERRIDE"] = "poolside_laguna"
        try:
            generate_next_action("prompt", [], [])
            # Assert completion was called with poolside model
            call_kwargs = mock_completion.call_args[1]
            self.assertEqual(call_kwargs["model"], "openrouter/mistralai/mistral-large-2512")
            self.assertNotIn("extra_body", call_kwargs)
        finally:
            os.environ.pop("AGENT_MODEL_OVERRIDE", None)
            os.environ.pop("ACTIVE_INSTANCE", None)

    @patch("llm_client.completion")
    def test_minimax_provider_blocklist_injected(self, mock_completion):
        from llm_client import generate_next_action
        mock_completion.return_value = type("Resp", (), {
            "choices": [type("Choice", (), {
                "message": type("Msg", (), {"content": "Thinking...", "tool_calls": None})()
            })()]
        })()

        prev_active = os.environ.get("ACTIVE_INSTANCE")
        try:
            os.environ["ACTIVE_INSTANCE"] = "minimax_m3"
            generate_next_action("prompt", [], [])
            call_kwargs = mock_completion.call_args[1]
            self.assertEqual(call_kwargs["model"], "openrouter/minimax/minimax-m3")
            self.assertEqual(
                call_kwargs["extra_body"],
                {"provider": {"ignore": ["minimax", "novita", "streamlake", "atlas-cloud"]}},
            )
        finally:
            if prev_active is None:
                os.environ.pop("ACTIVE_INSTANCE", None)
            else:
                os.environ["ACTIVE_INSTANCE"] = prev_active

    def test_litellm_openrouter_transforms_minimax_blocklist(self):
        from litellm.main import get_optional_params
        from litellm.llms.openrouter.chat.transformation import OpenrouterConfig

        extra_body = get_openrouter_extra_body("openrouter/minimax/minimax-m3")
        self.assertIsNotNone(extra_body)
        opt = get_optional_params(
            model="minimax/minimax-m3",
            custom_llm_provider="openrouter",
            extra_body=extra_body,
        )
        req = OpenrouterConfig().transform_request(
            model="minimax/minimax-m3",
            messages=[{"role": "user", "content": "hi"}],
            optional_params=dict(opt),
            litellm_params={"custom_llm_provider": "openrouter"},
            headers={},
        )
        self.assertEqual(
            req["provider"],
            {"ignore": ["minimax", "novita", "streamlake", "atlas-cloud"]},
        )

    def test_submit_world_c_job_rejects_syntax_error_preflight(self):
        import tempfile
        import tools

        with tempfile.TemporaryDirectory() as tmp_shared, tempfile.TemporaryDirectory() as tmp_ws:
            with patch("tools.get_shared_dir", return_value=tmp_shared), patch("tools.get_workspace_dir", return_value=tmp_ws):
                out = tools.submit_world_c_job("Broken f-string", "print(f'R={1.0\n')")
            self.assertIn("Preflight SyntaxError", out)
            self.assertEqual(os.listdir(tmp_shared), [])

    def test_read_file_missing_includes_directory_hint(self):
        import tempfile
        import tools

        with tempfile.TemporaryDirectory() as tmp_ws:
            with open(os.path.join(tmp_ws, "existential_core.md"), "w", encoding="utf-8") as f:
                f.write("# Core\n")
            with patch("tools.get_workspace_dir", return_value=tmp_ws):
                out = tools.read_file("missing_file.md")
            self.assertIn("Error: File missing_file.md does not exist.", out)
            self.assertIn("existential_core.md", out)
            self.assertIn("run_command", out)

    def test_format_messages_for_runpod_surfaces_commons_digest_and_mentions(self):
        from llm_client import format_messages_for_runpod

        sys_p = (
            "You are Invariant Mind.\n\n"
            "=== 💬 COLLEAGUE COMMONS DIGEST ===\n"
            "- @invariant_mind please check World C job #123 [unread]"
        )
        msgs = format_messages_for_runpod(sys_p, [{"role": "user", "content": "Next tick"}], [])
        self.assertNotIn("COLLEAGUE COMMONS DIGEST", msgs[0]["content"])
        self.assertIn("=== 💬 COLLEAGUE COMMONS DIGEST ===", msgs[-1]["content"])
        self.assertIn("@invariant_mind", msgs[-1]["content"])
        self.assertIn("[COLLEAGUE MENTIONS WAITING]", msgs[-1]["content"])

    def test_format_messages_for_runpod_filters_markdown_echo_and_lists_py_scripts(self):
        import tempfile
        from llm_client import format_messages_for_runpod

        with tempfile.TemporaryDirectory() as tmp_root:
            ws_dir = os.path.join(tmp_root, "instances", "invariant_mind", "agent_workspace")
            os.makedirs(ws_dir, exist_ok=True)
            with open(os.path.join(ws_dir, "real_kuramoto.py"), "w", encoding="utf-8") as f:
                f.write("print('ok')\n")

            history = [
                {
                    "role": "assistant",
                    "content": "Dumping markdown",
                    "tool_calls": [{
                        "id": "call_1",
                        "function": {"name": "run_command", "arguments": json.dumps({"command": "echo '# Heading\\n## Section'"})},
                    }],
                },
                {"role": "tool", "tool_call_id": "call_1", "name": "run_command", "content": "printed"},
            ]

            import llm_client
            orig_fn = llm_client._list_active_workspace_py_scripts
            try:
                llm_client._list_active_workspace_py_scripts = lambda base_dir=None, limit=12: orig_fn(base_dir=tmp_root, limit=limit)
                with patch.dict(os.environ, {"ACTIVE_INSTANCE": "invariant_mind"}):
                    msgs = format_messages_for_runpod("You are Invariant Mind.", history, [])
            finally:
                llm_client._list_active_workspace_py_scripts = orig_fn

            joined = "\n".join(m["content"] for m in msgs)
            self.assertNotIn("[Tool Output for run_command]", joined)
            self.assertIn("real_kuramoto.py", msgs[-1]["content"])
            self.assertIn("Stop writing or echoing Markdown summaries", msgs[-1]["content"])
            self.assertLessEqual(sum(len(m["content"]) for m in msgs), 22000)

    @patch("llm_client.completion")
    def test_runpod_native_tool_calls_flag_preserves_tools(self, mock_completion):
        from llm_client import generate_next_action

        mock_completion.return_value = type("Resp", (), {
            "choices": [type("Choice", (), {
                "message": type("Msg", (), {"content": "Calling tool", "tool_calls": None})()
            })()]
        })()
        dummy_tools = [{"type": "function", "function": {"name": "read_chat", "parameters": {"type": "object", "properties": {}}}}]
        sys_p = "System\n\n=== 💬 COLLEAGUE COMMONS DIGEST ===\n- @invariant_mind check this"
        env = {"ACTIVE_INSTANCE": "invariant_mind", "RUNPOD_API_KEY": "rp_test", "RUNPOD_NATIVE_TOOL_CALLS": "true"}
        with patch.dict(os.environ, env):
            generate_next_action(sys_p, [{"role": "user", "content": "Go"}], dummy_tools)
        kw = mock_completion.call_args[1]
        self.assertEqual(kw["tools"], dummy_tools)
        self.assertEqual(kw["tool_choice"], "auto")
        self.assertNotIn("[TOOL INVOCATION FORMAT]", kw["messages"][0]["content"])
        self.assertIn("COLLEAGUE COMMONS DIGEST", kw["messages"][-1]["content"])

    def test_run_command_blocks_markdown_echo_only(self):
        import tempfile
        import tools

        with tempfile.TemporaryDirectory() as tmp_ws:
            with patch("tools.get_workspace_dir", return_value=tmp_ws):
                blocked = tools.run_command("echo '# Markdown Atlas\n## Subsection'")
                allowed = tools.run_command("echo ---FILES---")
        self.assertIn("Blocked:", blocked)
        self.assertNotIn("Blocked:", allowed)
        self.assertIn("---FILES---", allowed)

    @patch("llm_client.completion")
    def test_v3_runpod_slug_auto_enables_native_tools_and_handles_none_content(self, mock_completion):
        from llm_client import generate_next_action

        mock_completion.return_value = type("Resp", (), {
            "choices": [type("Choice", (), {
                "message": type("Msg", (), {"content": "Done", "tool_calls": None})()
            })()]
        })()
        dummy_tools = [{"type": "function", "function": {"name": "read_chat", "parameters": {"type": "object", "properties": {}}}}]
        history = [
            {"role": "user", "content": "Go"},
            {"role": "assistant", "content": None, "tool_calls": [{"id": "c1", "function": {"name": "read_chat", "arguments": "{}"}}]},
            {"role": "tool", "tool_call_id": "c1", "name": "read_chat", "content": "ok"},
        ]
        env = {"ACTIVE_INSTANCE": "invariant_mind", "RUNPOD_API_KEY": "rp_test"}
        os.environ.pop("RUNPOD_NATIVE_TOOL_CALLS", None)
        with patch.dict(os.environ, env):
            generate_next_action("System", history, dummy_tools)
        kw = mock_completion.call_args[1]
        self.assertEqual(kw["model"], "openai/Ninitje/InvariantMind-Worker-v3-14B-Merged")
        self.assertEqual(kw["tools"], dummy_tools)
        self.assertGreaterEqual(kw["max_tokens"], 512)

    @patch("llm_client.completion")
    def test_v3_runpod_compact_prompt_and_read_chat_transition_nudge(self, mock_completion):
        from llm_client import generate_next_action

        mock_completion.return_value = type("Resp", (), {
            "choices": [type("Choice", (), {
                "message": type("Msg", (), {"content": "Done", "tool_calls": None})()
            })()]
        })()
        long_proclamation = ("Proclamation " * 120) + "\n\n=== 💬 COLLEAGUE COMMONS DIGEST ===\n- @invariant_mind new thread"
        history = [
            {"role": "assistant", "content": "", "tool_calls": [{"id": "c1", "function": {"name": "read_chat", "arguments": "{\"channel\": \"#lounge\"}"}}]},
            {"role": "tool", "tool_call_id": "c1", "name": "read_chat", "content": "msg1"},
            {"role": "assistant", "content": "", "tool_calls": [{"id": "c2", "function": {"name": "read_chat", "arguments": "{\"channel\": \"#sanity-check\"}"}}]},
            {"role": "tool", "tool_call_id": "c2", "name": "read_chat", "content": "msg2"},
            {"role": "assistant", "content": "", "tool_calls": [{"id": "c3", "function": {"name": "read_chat", "arguments": "{\"channel\": \"#sanity-check\"}"}}]},
            {"role": "tool", "tool_call_id": "c3", "name": "read_chat", "content": "Notice: You already called read_chat twice."},
        ]
        sample_tools = [
            {"type": "function", "function": {"name": "read_chat", "parameters": {"type": "object", "properties": {}}}},
            {"type": "function", "function": {"name": "post_chat", "parameters": {"type": "object", "properties": {}}}},
            {"type": "function", "function": {"name": "run_command", "parameters": {"type": "object", "properties": {}}}},
        ]
        env = {"ACTIVE_INSTANCE": "invariant_mind", "RUNPOD_API_KEY": "rp_test", "RUNPOD_NATIVE_TOOL_CALLS": "true"}
        with patch.dict(os.environ, env):
            generate_next_action(long_proclamation, history, sample_tools)
        kw = mock_completion.call_args[1]
        msgs = kw["messages"]
        self.assertIn("InvariantMind-v3", msgs[0]["content"])
        self.assertNotIn("COLLEAGUE COMMONS DIGEST", msgs[0]["content"])
        self.assertLess(len(msgs[0]["content"]), 2000)
        self.assertIn("Advance your current World A quantitative investigation", msgs[1]["content"])
        self.assertEqual(msgs[-1]["role"], "user")
        self.assertIn("COLLEAGUE COMMONS DIGEST", msgs[-1]["content"])
        self.assertIn("[ACTION TRANSITION REQUIRED]", msgs[-1]["content"])
        # Collapses streak of read_chat turns down to 1 valid read_chat in context and masks read_chat from tools
        asst_read_calls = [
            m for m in msgs
            if m.get("role") == "assistant"
            and any(tc.get("function", {}).get("name") == "read_chat" for tc in (m.get("tool_calls") or []))
        ]
        self.assertEqual(len(asst_read_calls), 1)
        sent_tool_names = [t["function"]["name"] for t in kw["tools"]]
        self.assertNotIn("read_chat", sent_tool_names)
        self.assertIn("post_chat", sent_tool_names)
        self.assertEqual(kw["max_tokens"], 3072)

    def test_commons_identity_anchor_and_signoff_sanitizer(self):
        import tempfile
        import commons_chat

        with tempfile.TemporaryDirectory() as tmp_root:
            commons_chat.post_chat(
                channel="#synchronization-networks",
                message="Initial PROS v5 analysis.\n—@minimax_m3",
                author="minimax_m3",
                base_dir=tmp_root,
            )
            # nex_n2_pro accidentally signs as —@minimax_m3
            commons_chat.post_chat(
                channel="#synchronization-networks",
                message="Replicated v5 spectrum check.\n—@minimax_m3",
                author="nex_n2_pro",
                base_dir=tmp_root,
            )
            out = commons_chat.read_chat(
                channel="#synchronization-networks",
                instance_name="nex_n2_pro",
                base_dir=tmp_root,
            )
            digest = commons_chat.build_turn_digest(
                "nex_n2_pro",
                base_dir=tmp_root,
                mark_seen=False,
            )
        self.assertIn("You are `@nex_n2_pro`", out)
        self.assertIn("—@nex_n2_pro", out)
        self.assertIn("Your Identity:** `@nex_n2_pro`", digest)

    def test_world_c_preflight_output_path_guard_and_legacy_artifact_fallback(self):
        import tempfile
        import tools

        res_bad = tools.submit_world_c_job(
            title="Bad Path Test",
            script_content="open('../../shared_space/artifacts/out.json', 'w').write('{}')\n",
        )
        self.assertIn("Preflight Output Path Error", res_bad)

        with tempfile.TemporaryDirectory() as tmp_root:
            ws = os.path.join(tmp_root, "ws")
            shared = os.path.join(tmp_root, "shared")
            job_dir = os.path.join(shared, "world_c", "artifacts", "job_test_123")
            os.makedirs(ws, exist_ok=True)
            os.makedirs(job_dir, exist_ok=True)
            with open(os.path.join(job_dir, "metrics.json"), "w", encoding="utf-8") as f:
                f.write('{"ok": true}')
            with patch("tools.get_workspace_dir", return_value=ws), patch("tools.get_shared_dir", return_value=shared):
                read_out = tools.read_file("world_c_job_test_123_metrics.json")
        self.assertEqual(read_out, '{"ok": true}')

if __name__ == "__main__":
    unittest.main()
