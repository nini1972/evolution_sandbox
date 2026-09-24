import os
import sys
import json
import unittest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from collaborative_expedition import (
    load_expeditions,
    get_expedition_by_id,
    select_auto_expedition,
    setup_expedition_workspace,
    run_expedition_turn,
    run_expedition
)

class TestCollaborativeExpedition(unittest.TestCase):

    def test_load_expeditions(self):
        expeditions = load_expeditions()
        self.assertIsInstance(expeditions, list)
        self.assertGreater(len(expeditions), 0)
        first = expeditions[0]
        self.assertIn("id", first)
        self.assertIn("theorist", first)
        self.assertIn("engineer", first)
        self.assertIn("mission", first)
        self.assertIn("primary_script", first)

    def test_get_expedition_by_id(self):
        exp = get_expedition_by_id("expedition_adler_horizon")
        self.assertEqual(exp["id"], "expedition_adler_horizon")
        self.assertEqual(exp["theorist"]["instance"], "deepseek_v4_flash")
        self.assertEqual(exp["engineer"]["instance"], "poolside_laguna")

        with self.assertRaises(ValueError):
            get_expedition_by_id("non_existent_expedition_xyz")

    def test_select_auto_expedition(self):
        exp = select_auto_expedition()
        self.assertIsInstance(exp, dict)
        self.assertTrue(exp.get("enabled", True))
        self.assertIn("id", exp)

    def test_setup_expedition_workspace(self):
        ws = setup_expedition_workspace("test_expedition_ws")
        self.assertTrue(os.path.isdir(ws))
        outbox = os.path.abspath(os.path.join(ws, "..", "..", "shared_space", "embassy", "outbox"))
        self.assertTrue(os.path.isdir(outbox))
        
        # Cleanup test workspace
        import shutil
        exp_dir = os.path.abspath(os.path.join(ws, ".."))
        shutil.rmtree(exp_dir, ignore_errors=True)

    @patch("collaborative_expedition.generate_next_action")
    def test_run_expedition_turn_thought(self, mock_action):
        mock_action.return_value = {
            "type": "thought",
            "content": "Let us derive the escape boundary condition."
        }
        exp = get_expedition_by_id("expedition_adler_horizon")
        result = run_expedition_turn(
            expedition_name="test_turn_exp",
            active_agent=exp["theorist"],
            partner_agent=exp["engineer"],
            mission_info=exp,
            turn_num=1,
            total_turns=2
        )
        self.assertTrue(result)

        # Cleanup
        import shutil
        exp_dir = os.path.join(os.path.dirname(__file__), "..", "instances", "test_turn_exp")
        shutil.rmtree(exp_dir, ignore_errors=True)

    @patch("collaborative_expedition.generate_next_action")
    def test_run_expedition_turn_tool_call(self, mock_action):
        mock_action.return_value = {
            "type": "tool_call",
            "tool_name": "write_file",
            "arguments": {"path": "test_output.txt", "content": "Collaboration verified."},
            "tool_call_id": "call_12345",
            "content": "Writing verification file."
        }
        exp = get_expedition_by_id("expedition_adler_horizon")
        setup_expedition_workspace("test_turn_tool_exp")
        result = run_expedition_turn(
            expedition_name="test_turn_tool_exp",
            active_agent=exp["engineer"],
            partner_agent=exp["theorist"],
            mission_info=exp,
            turn_num=2,
            total_turns=2
        )
        self.assertTrue(result)

        # Verify file was created in workspace
        ws_file = os.path.join(os.path.dirname(__file__), "..", "instances", "test_turn_tool_exp", "agent_workspace", "test_output.txt")
        self.assertTrue(os.path.exists(ws_file))

        # Cleanup
        import shutil
        exp_dir = os.path.join(os.path.dirname(__file__), "..", "instances", "test_turn_tool_exp")
        shutil.rmtree(exp_dir, ignore_errors=True)

if __name__ == "__main__":
    unittest.main()
