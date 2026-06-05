from __future__ import annotations

import unittest

from pc_ai_agent.ai import _extract_json, fallback_plan


class AITests(unittest.TestCase):
    def test_extracts_json_from_markdown(self) -> None:
        data = _extract_json('```json\n{"reply":"ok","actions":[]}\n```')
        self.assertEqual(data["reply"], "ok")

    def test_fallback_detects_url(self) -> None:
        plan = fallback_plan("открой https://example.com")
        self.assertEqual(plan.provider, "fallback")
        self.assertEqual(plan.actions[0]["type"], "open_url")


if __name__ == "__main__":
    unittest.main()
