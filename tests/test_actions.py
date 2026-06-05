from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from pc_ai_agent.actions import ActionError, execute_action, is_dangerous_command, list_files, read_text_file, write_text_file


class ActionTests(unittest.TestCase):
    def test_blocks_dangerous_commands(self) -> None:
        self.assertTrue(is_dangerous_command("rm -rf /tmp/demo"))
        with self.assertRaises(ActionError):
            execute_action({"type": "run_command", "command": "shutdown now"})

    def test_file_actions_are_workspace_scoped(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            old_workspace = os.environ.get("PCAI_WORKSPACE")
            os.environ["PCAI_WORKSPACE"] = tmp
            try:
                result = write_text_file("notes/todo.txt", "hello")
                self.assertTrue(result.ok)
                self.assertEqual(read_text_file("notes/todo.txt").data, "hello")
                listed = list_files("notes")
                self.assertEqual(listed.data, [{"name": "todo.txt", "type": "file"}])
                with self.assertRaises(ActionError):
                    write_text_file(str(Path(tmp).parent / "outside.txt"), "no")
            finally:
                if old_workspace is None:
                    os.environ.pop("PCAI_WORKSPACE", None)
                else:
                    os.environ["PCAI_WORKSPACE"] = old_workspace

    def test_unknown_action_is_rejected(self) -> None:
        with self.assertRaises(ActionError):
            execute_action({"type": "delete_everything"})


if __name__ == "__main__":
    unittest.main()
