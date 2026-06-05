from __future__ import annotations

import unittest

from pc_ai_agent.server import INDEX_HTML


class ServerUITests(unittest.TestCase):
    def test_voice_controls_are_rendered(self) -> None:
        self.assertIn("Голосовое управление", INDEX_HTML)
        self.assertIn("SpeechRecognition", INDEX_HTML)
        self.assertIn("startVoice", INDEX_HTML)
        self.assertIn("speakReply", INDEX_HTML)


if __name__ == "__main__":
    unittest.main()
