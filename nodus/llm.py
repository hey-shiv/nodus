"""A provider-neutral LLM call that returns JSON, with a disk cache and a fallback chain.

Order: Gemini (if GEMINI_API_KEY is set) -> local Ollama model (if running) -> error.
When Gemini's quota runs out, the call falls through to the local model.
The LLM only drafts lesson proposals; it never decides a match or approves anything.
"""
import hashlib
import json
import os
import urllib.request
from pathlib import Path

CACHE = Path(__file__).resolve().parent.parent / "cache" / "llm"
# Tried in order: if one model's free quota is used up (or it isn't available to the
# key), the next one is tried. Checked against Google's model list on Oct 15, 2026.
GEMINI_MODELS = os.environ.get("NODUS_GEMINI_MODELS", "gemini-3.8-flash,gemini-3.5-flash-lite")
OLLAMA_MODEL = os.environ.get("NODUS_OLLAMA_MODEL", "gemma4:12b-it-qat")
OLLAMA_URL = os.environ.get("NODUS_OLLAMA_URL", "http://localhost:11434")
OLLAMA_TIMEOUT = int(os.environ.get("NODUS_OLLAMA_TIMEOUT", "900"))


class LLMError(RuntimeError):
    pass


class Gemini:
    name = "gemini"

    def __init__(self, key, models=GEMINI_MODELS):
        from google import genai
        self.client = genai.Client(api_key=key)
        self.models = [m.strip() for m in models.split(",") if m.strip()]

    def complete(self, prompt):
        errors = []
        for model in self.models:
            try:
                resp = self.client.models.generate_content(
                    model=model, contents=prompt,
                    config={"response_mime_type": "application/json", "temperature": 0})
                return resp.text
            except Exception as e:      # quota, unknown model, network: try the next model
                errors.append(f"{model}: {str(e)[:120]}")
        raise LLMError("gemini: " + " | ".join(errors))


class Ollama:
    name = "ollama"

    def __init__(self, model=OLLAMA_MODEL, url=OLLAMA_URL):
        self.model, self.url = model, url

    def complete(self, prompt):
        # think=False: Gemma 4 is a reasoning model; hidden "thinking" made drafts time out (T14).
        body = json.dumps({"model": self.model, "stream": False, "format": "json", "think": False,
                           "options": {"temperature": 0, "num_ctx": 8192, "num_predict": 3000},
                           "messages": [{"role": "user", "content": prompt}]}).encode()
        req = urllib.request.Request(f"{self.url}/api/chat", data=body,
                                     headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=OLLAMA_TIMEOUT) as r:
                return json.loads(r.read())["message"]["content"]
        except Exception as e:
            raise LLMError(f"ollama: {e}") from e


def default_providers():
    from dotenv import load_dotenv
    load_dotenv()
    providers = []
    if os.environ.get("GEMINI_API_KEY"):
        providers.append(Gemini(os.environ["GEMINI_API_KEY"]))
    providers.append(Ollama())
    return providers


class LLM:
    """Try each provider in order; cache every successful reply on disk."""

    def __init__(self, providers=None, cache_dir=CACHE):
        self.providers = providers if providers is not None else default_providers()
        self.cache_dir = Path(cache_dir)

    def complete_json(self, prompt):
        key = hashlib.sha256(prompt.encode()).hexdigest()[:20]
        cached = self.cache_dir / f"{key}.json"
        if cached.exists():
            return json.loads(cached.read_text())["reply"]
        errors = []
        for p in self.providers:
            try:
                reply = p.complete(prompt)
            except LLMError as e:
                errors.append(str(e))
                continue
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            cached.write_text(json.dumps({"provider": p.name, "reply": reply}))
            return reply
        raise LLMError("no provider answered: " + " | ".join(errors))
