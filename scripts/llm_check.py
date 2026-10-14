"""Check which LLM providers work on this machine, and which Gemini models your key can use.

Run:  .venv/bin/python scripts/llm_check.py
Never prints the key. Sends only a tiny test prompt (no company data).
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from dotenv import load_dotenv  # noqa: E402

from nodus.llm import GEMINI_MODELS, OLLAMA_MODEL, LLMError, Gemini, Ollama  # noqa: E402

load_dotenv()
TEST = 'Reply with JSON only: {"ok": true}'

key = os.environ.get("GEMINI_API_KEY")
if not key:
    print("Gemini: no GEMINI_API_KEY in .env (optional)")
else:
    from google import genai
    names = sorted(m.name.removeprefix("models/") for m in genai.Client(api_key=key).models.list()
                   if "generateContent" in (m.supported_actions or []))
    print(f"Gemini: key works; {len(names)} text models available, e.g.:",
          ", ".join(n for n in names if "flash" in n)[:400])
    for model in GEMINI_MODELS.split(","):
        try:
            print(f"  {model}: OK ->", Gemini(key, model).complete(TEST)[:40])
        except LLMError as e:
            print(f"  {model}: FAILED ({str(e)[:160]})")

try:
    print(f"Ollama ({OLLAMA_MODEL}): OK ->", Ollama().complete(TEST)[:40])
except LLMError as e:
    print(f"Ollama ({OLLAMA_MODEL}): not available ({str(e)[:120]})")
