import unittest
import os
import json
from unittest.mock import patch
from llm_client import prune_history, merge_consecutive_messages, extract_fallback_tool_call, resolve_agent_model

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
        content = "[edit_file(path=\"test.py\", content=\"print(1)\")]"
        res = extract_fallback_tool_call(content)
        self.assertIsNotNone(res)
        self.assertEqual(res["tool_name"], "edit_file")
        self.assertEqual(res["arguments"]["path"], "test.py")

    def test_resolve_agent_model_routing(self):
        model = resolve_agent_model("claude_sonnet_4_5")
        self.assertEqual(model, "openrouter/anthropic/claude-sonnet-4")

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
            self.assertEqual(call_kwargs["model"], "openrouter/poolside/laguna-s-2.1")
        finally:
            os.environ.pop("AGENT_MODEL_OVERRIDE", None)
            os.environ.pop("ACTIVE_INSTANCE", None)

if __name__ == "__main__":
    unittest.main()
