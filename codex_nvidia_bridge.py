"""
Minimal Codex (Responses API) <-> NVIDIA NIM (Chat Completions API) bridge.

WHAT THIS DOES, IN PLAIN TERMS:
- Listens on http://127.0.0.1:15721
- Codex POSTs to /v1/responses in OpenAI "Responses API" format
- This script converts that into "Chat Completions" format and POSTs it to
  https://integrate.api.nvidia.com/v1/chat/completions
- It converts NVIDIA's reply back into Responses API format and returns it to Codex

That's it. No other network calls, no telemetry, no external dependencies beyond
the Python standard library + `requests`. Read it top to bottom before running --
it's short on purpose so you can verify that.

SETUP:
  pip install requests
  set NVIDIA_NIM_API_KEY=nvapi-xxxxxxxx     (use a freshly rotated key)
  python codex_nvidia_bridge.py

Then in config.toml:
  [model_providers.nvidia-bridge]
  name = "NVIDIA via local bridge"
  base_url = "http://127.0.0.1:15721/v1"
  env_key = "NVIDIA_NIM_API_KEY"
  wire_api = "responses"
"""

import json
import os
import sys
import uuid
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

import requests

NVIDIA_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
API_KEY = os.environ.get("NVIDIA_NIM_API_KEY")
PORT = 15721

if not API_KEY:
    print("ERROR: NVIDIA_NIM_API_KEY environment variable is not set.")
    sys.exit(1)


def responses_input_to_chat_messages(body):
    """Convert Codex's Responses-API 'input' field into Chat Completions 'messages'."""
    messages = []

    # Some callers send input as a plain string ("Say READY"), others send
    # a list of structured message objects. Handle both.
    raw_input = body.get("input", "")

    if isinstance(raw_input, str):
        messages.append({"role": "user", "content": raw_input})
        return messages

    if isinstance(raw_input, list):
        for item in raw_input:
            role = item.get("role", "user")
            content = item.get("content", "")

            # content can be a string, or a list of typed content parts
            # (e.g. [{"type": "input_text", "text": "..."}])
            if isinstance(content, list):
                text_parts = []
                for part in content:
                    if isinstance(part, dict) and "text" in part:
                        text_parts.append(part["text"])
                content = "\n".join(text_parts)

            messages.append({"role": role, "content": content})
        return messages

    # Fallback: nothing usable, send an empty user turn rather than crashing
    return [{"role": "user", "content": ""}]


def chat_response_to_responses_output(chat_json, model_name):
    """Convert NVIDIA's Chat Completions response into Responses-API shape."""
    choice = chat_json.get("choices", [{}])[0]
    message = choice.get("message", {})
    text = message.get("content") or ""

    output_item = {
        "type": "message",
        "id": f"msg_{uuid.uuid4().hex}",
        "status": "completed",
        "role": "assistant",
        "content": [
            {
                "type": "output_text",
                "text": text,
                "annotations": [],
            }
        ],
    }

    return {
        "id": f"resp_{uuid.uuid4().hex}",
        "object": "response",
        "created_at": int(time.time()),
        "model": model_name,
        "output": [output_item],
        "usage": chat_json.get("usage", {}),
        "status": "completed",
    }


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        # Print to console so you can see activity live, instead of silence.
        print("[bridge]", fmt % args)

    def do_POST(self):
        if self.path not in ("/v1/responses", "/responses"):
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'{"error": "not found, expected /v1/responses"}')
            return

        length = int(self.headers.get("Content-Length", 0))
        raw_body = self.rfile.read(length)

        try:
            body = json.loads(raw_body)
        except json.JSONDecodeError:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b'{"error": "invalid json"}')
            return

        model_name = body.get("model", "deepseek-ai/deepseek-v4-flash")
        messages = responses_input_to_chat_messages(body)

        chat_payload = {
            "model": model_name,
            "messages": messages,
        }

        print(f"[bridge] Forwarding to NVIDIA: model={model_name}, "
              f"{len(messages)} message(s)")

        try:
            resp = requests.post(
                NVIDIA_URL,
                headers={
                    "Authorization": f"Bearer {API_KEY}",
                    "Content-Type": "application/json",
                },
                json=chat_payload,
                timeout=120,  # give slow cold-starts room, but never hang forever
            )
        except requests.exceptions.RequestException as e:
            print(f"[bridge] ERROR calling NVIDIA: {e}")
            self.send_response(502)
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())
            return

        print(f"[bridge] NVIDIA responded with status {resp.status_code}")

        if resp.status_code != 200:
            self.send_response(resp.status_code)
            self.end_headers()
            self.wfile.write(resp.content)
            return

        chat_json = resp.json()
        responses_json = chat_response_to_responses_output(chat_json, model_name)

        body_bytes = json.dumps(responses_json).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body_bytes)))
        self.end_headers()
        self.wfile.write(body_bytes)


if __name__ == "__main__":
    server = HTTPServer(("127.0.0.1", PORT), Handler)
    print(f"[bridge] Listening on http://127.0.0.1:{PORT}/v1/responses")
    print(f"[bridge] Forwarding to {NVIDIA_URL}")
    print("[bridge] Only talks to 127.0.0.1 and integrate.api.nvidia.com. Ctrl+C to stop.")
    server.serve_forever()
