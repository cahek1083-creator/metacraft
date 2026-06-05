from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from .actions import ActionError, action_preview, execute_action
from .ai import build_plan

INDEX_HTML = """<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>PC AI Controller</title>
  <style>
    :root { color-scheme: dark; font-family: Inter, system-ui, sans-serif; }
    body { margin: 0; background: #0f172a; color: #e2e8f0; }
    main { max-width: 920px; margin: 0 auto; padding: 32px 18px; }
    .card { background: #111827; border: 1px solid #334155; border-radius: 18px; padding: 20px; box-shadow: 0 20px 60px #0006; }
    textarea, select { box-sizing: border-box; border-radius: 14px; border: 1px solid #475569; background: #020617; color: #e2e8f0; padding: 14px; font: inherit; }
    textarea { width: 100%; min-height: 110px; resize: vertical; }
    select { min-height: 44px; padding: 0 12px; }
    button { border: 0; border-radius: 12px; padding: 11px 16px; background: #38bdf8; color: #082f49; font-weight: 700; cursor: pointer; }
    button.secondary { background: #334155; color: #e2e8f0; }
    button.danger { background: #fb7185; color: #4c0519; }
    button.voice { background: #a78bfa; color: #1e1b4b; }
    button:disabled { opacity: .55; cursor: wait; }
    label { display: inline-flex; gap: 8px; align-items: center; }
    pre { overflow-x: auto; white-space: pre-wrap; background: #020617; border-radius: 12px; padding: 12px; border: 1px solid #1e293b; }
    .actions { display: grid; gap: 12px; margin-top: 16px; }
    .action { border: 1px solid #334155; border-radius: 14px; padding: 14px; background: #0f172a; }
    .row { display: flex; gap: 10px; align-items: center; flex-wrap: wrap; margin-top: 12px; }
    .pill { font-size: 12px; background: #1e293b; border: 1px solid #475569; padding: 4px 8px; border-radius: 999px; }
    .warn { color: #fde68a; }
    .voice-panel { margin-top: 14px; padding: 14px; border: 1px solid #334155; border-radius: 14px; background: #0f172a; }
    .transcript { min-height: 24px; color: #bfdbfe; }
  </style>
</head>
<body>
<main>
  <h1>🤖 PC AI Controller</h1>
  <p class="warn">Нейросеть предлагает действия, но каждое выполнение требует вашего подтверждения.</p>
  <section class="card">
    <textarea id="prompt" placeholder="Например: открой https://example.com или покажи файлы в текущей папке"></textarea>
    <div class="voice-panel">
      <strong>🎙️ Голосовое управление</strong>
      <p class="warn">Нажмите «Начать запись», произнесите команду, затем проверьте текст. Выполнение действий всё равно требует подтверждения.</p>
      <div class="row">
        <button class="voice" id="startVoice">Начать запись</button>
        <button class="secondary" id="stopVoice" disabled>Остановить</button>
        <select id="voiceLang" aria-label="Язык распознавания речи">
          <option value="ru-RU">Русский</option>
          <option value="en-US">English</option>
        </select>
        <label><input type="checkbox" id="autoAsk" /> отправлять после распознавания</label>
        <label><input type="checkbox" id="speakReply" /> озвучивать ответ</label>
      </div>
      <p id="voiceStatus" class="pill">микрофон выключен</p>
      <p id="voiceTranscript" class="transcript"></p>
    </div>
    <div class="row">
      <button id="ask">Спросить AI</button>
      <button class="secondary" id="clear">Очистить</button>
      <span id="status" class="pill">готов</span>
    </div>
    <h2>Ответ</h2>
    <pre id="reply">Пока пусто.</pre>
    <div id="actions" class="actions"></div>
  </section>
</main>
<script>
const ask = document.querySelector('#ask');
const clear = document.querySelector('#clear');
const statusEl = document.querySelector('#status');
const reply = document.querySelector('#reply');
const actionsEl = document.querySelector('#actions');
const promptEl = document.querySelector('#prompt');
const startVoice = document.querySelector('#startVoice');
const stopVoice = document.querySelector('#stopVoice');
const voiceLang = document.querySelector('#voiceLang');
const voiceStatus = document.querySelector('#voiceStatus');
const voiceTranscript = document.querySelector('#voiceTranscript');
const autoAsk = document.querySelector('#autoAsk');
const speakReply = document.querySelector('#speakReply');
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
let recognition = null;
let finalTranscript = '';

function setStatus(text) { statusEl.textContent = text; }
function setVoiceStatus(text) { voiceStatus.textContent = text; }
function speak(text) {
  if (!speakReply.checked || !('speechSynthesis' in window)) return;
  window.speechSynthesis.cancel();
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = voiceLang.value;
  window.speechSynthesis.speak(utterance);
}
function renderActions(actions) {
  actionsEl.innerHTML = '';
  if (!actions.length) {
    actionsEl.innerHTML = '<p class="pill">Действий нет</p>';
    return;
  }
  actions.forEach((action, index) => {
    const box = document.createElement('div');
    box.className = 'action';
    const pre = document.createElement('pre');
    pre.textContent = JSON.stringify(action, null, 2);
    const run = document.createElement('button');
    run.className = 'danger';
    run.textContent = 'Выполнить это действие';
    run.onclick = async () => {
      if (!confirm('Подтвердить выполнение?\n' + JSON.stringify(action))) return;
      run.disabled = true;
      setStatus('выполняю...');
      const res = await fetch('/api/execute', {method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({action})});
      const data = await res.json();
      reply.textContent += '\n\n[Результат #' + (index + 1) + ']\n' + JSON.stringify(data, null, 2);
      speak(data.message || 'Действие выполнено');
      run.disabled = false;
      setStatus(res.ok ? 'готов' : 'ошибка');
    };
    box.append(pre, run);
    actionsEl.appendChild(box);
  });
}
async function askAi() {
  ask.disabled = true;
  setStatus('думаю...');
  actionsEl.innerHTML = '';
  try {
    const res = await fetch('/api/plan', {method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({message: promptEl.value})});
    const data = await res.json();
    reply.textContent = data.reply + '\n\nProvider: ' + data.provider;
    renderActions(data.actions || []);
    speak(data.reply || 'Ответ готов');
    setStatus(res.ok ? 'готов' : 'ошибка');
  } catch (err) {
    reply.textContent = String(err);
    setStatus('ошибка');
  } finally {
    ask.disabled = false;
  }
}
function setupVoiceRecognition() {
  if (!SpeechRecognition) {
    startVoice.disabled = true;
    setVoiceStatus('браузер не поддерживает распознавание речи');
    voiceTranscript.textContent = 'Откройте приложение в Chrome/Edge или другом браузере с Web Speech API.';
    return;
  }
  recognition = new SpeechRecognition();
  recognition.continuous = false;
  recognition.interimResults = true;
  recognition.maxAlternatives = 1;
  recognition.onstart = () => {
    finalTranscript = '';
    startVoice.disabled = true;
    stopVoice.disabled = false;
    setVoiceStatus('слушаю...');
    voiceTranscript.textContent = '';
  };
  recognition.onresult = (event) => {
    let interimTranscript = '';
    for (let i = event.resultIndex; i < event.results.length; i += 1) {
      const transcript = event.results[i][0].transcript.trim();
      if (event.results[i].isFinal) {
        finalTranscript = `${finalTranscript} ${transcript}`.trim();
      } else {
        interimTranscript = transcript;
      }
    }
    const visibleTranscript = finalTranscript || interimTranscript;
    voiceTranscript.textContent = visibleTranscript;
    if (visibleTranscript) promptEl.value = visibleTranscript;
  };
  recognition.onerror = (event) => {
    setVoiceStatus('ошибка микрофона: ' + event.error);
    startVoice.disabled = false;
    stopVoice.disabled = true;
  };
  recognition.onend = () => {
    startVoice.disabled = false;
    stopVoice.disabled = true;
    setVoiceStatus(finalTranscript ? 'команда распознана' : 'микрофон выключен');
    if (finalTranscript && autoAsk.checked) askAi();
  };
}
ask.onclick = askAi;
startVoice.onclick = () => {
  if (!recognition) return;
  recognition.lang = voiceLang.value;
  recognition.start();
};
stopVoice.onclick = () => {
  if (recognition) recognition.stop();
};
clear.onclick = () => {
  promptEl.value = '';
  reply.textContent = 'Пока пусто.';
  actionsEl.innerHTML = '';
  voiceTranscript.textContent = '';
  finalTranscript = '';
  setStatus('готов');
};
setupVoiceRecognition();
</script>
</body>
</html>"""


class Handler(BaseHTTPRequestHandler):
    def _send_json(self, payload: dict[str, Any], status: int = 200) -> None:
        encoded = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def _read_json(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length).decode("utf-8") if length else "{}"
        data = json.loads(raw)
        if not isinstance(data, dict):
            raise ValueError("JSON body must be an object")
        return data

    def do_GET(self) -> None:  # noqa: N802
        if self.path != "/":
            self.send_error(404)
            return
        encoded = INDEX_HTML.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def do_POST(self) -> None:  # noqa: N802
        try:
            body = self._read_json()
            if self.path == "/api/plan":
                message = str(body.get("message") or "").strip()
                if not message:
                    self._send_json({"reply": "Введите запрос.", "actions": [], "provider": "local"}, 400)
                    return
                self._send_json(build_plan(message).to_dict())
                return
            if self.path == "/api/execute":
                action = body.get("action")
                if not isinstance(action, dict):
                    self._send_json({"ok": False, "message": "action must be an object"}, 400)
                    return
                preview = action_preview(action)
                result = execute_action(action).to_dict()
                result["preview"] = preview
                self._send_json(result, 200 if result["ok"] else 422)
                return
            self.send_error(404)
        except (ValueError, ActionError, json.JSONDecodeError) as exc:
            self._send_json({"ok": False, "message": str(exc)}, 400)
        except Exception as exc:  # pragma: no cover - defensive HTTP boundary
            self._send_json({"ok": False, "message": f"Unexpected error: {exc}"}, 500)


def run(host: str = "127.0.0.1", port: int = 8765) -> None:
    server = ThreadingHTTPServer((host, port), Handler)
    print(f"PC AI Controller: http://{host}:{port}")
    server.serve_forever()


def main() -> None:
    parser = argparse.ArgumentParser(description="Safe AI-assisted PC controller")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=8765, type=int)
    args = parser.parse_args()
    run(args.host, args.port)


if __name__ == "__main__":
    main()
