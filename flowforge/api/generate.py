import json, os, urllib.request, urllib.error
from http.server import BaseHTTPRequestHandler

MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")

PROMPT = """You are FlowForge AI, an expert process designer.
Turn the user's idea into a complete working process.
Return ONLY valid JSON with exactly this shape:
{
  "title": "short process title",
  "summary": "2-3 sentence overview",
  "steps": [{"step": 1, "name": "...", "description": "...", "duration": "e.g. 2 weeks"}],
  "flowchart": "Mermaid 'flowchart TD' code. Node ids must be simple letters/numbers, labels in double quotes, no parentheses or special characters inside labels.",
  "tasks": [{"task": "...", "owner": "role/team", "priority": "High|Medium|Low"}],
  "resources": [{"category": "People|Budget|Equipment|Venue|Software|Other", "item": "...", "details": "..."}],
  "missing_steps": ["steps people commonly forget for this kind of process"],
  "suggestions": ["concrete ideas to improve the process"]
}
User idea: """

class handler(BaseHTTPRequestHandler):
    def _send(self, code, data):
        body = json.dumps(data).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self._send(204, {})

    def do_POST(self):
        key = os.environ.get("GEMINI_API_KEY")
        if not key:
            return self._send(500, {"error": "GEMINI_API_KEY is not set in Vercel environment variables."})
        try:
            length = int(self.headers.get("Content-Length", 0))
            idea = json.loads(self.rfile.read(length) or b"{}").get("idea", "").strip()
        except Exception:
            return self._send(400, {"error": "Invalid request body."})
        if not idea or len(idea) > 2000:
            return self._send(400, {"error": "Please describe your idea (max 2000 characters)."})

        payload = {
            "contents": [{"parts": [{"text": PROMPT + idea}]}],
            "generationConfig": {"responseMimeType": "application/json", "temperature": 0.6},
        }
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"
        req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                     headers={"Content-Type": "application/json", "x-goog-api-key": key})
        try:
            with urllib.request.urlopen(req, timeout=55) as r:
                res = json.loads(r.read())
            text = res["candidates"][0]["content"]["parts"][0]["text"]
            text = text.strip().removeprefix("```json").removeprefix("```").removesuffix("```")
            return self._send(200, json.loads(text))
        except urllib.error.HTTPError as e:
            return self._send(e.code, {"error": f"Gemini error: {e.read().decode()[:300]}"})
        except Exception as e:
            return self._send(500, {"error": f"Could not generate process: {e}"})
