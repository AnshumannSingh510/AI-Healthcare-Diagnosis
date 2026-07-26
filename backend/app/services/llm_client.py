"""
Provider-agnostic LLM client. Configured via env vars:
    LLM_PROVIDER = "anthropic" | "openai" | "gemini" | "none"
    LLM_API_KEY
    LLM_MODEL

If LLM_PROVIDER is "none" or no API key is configured, falls back to a
deterministic template response so the app still works without an API key.
"""
import httpx
from app.core.config import settings

MEDICAL_SYSTEM_PROMPT = """You are a medical information assistant embedded in a clinical
decision-support platform. Rules you must always follow:
1. Explain concepts in simple, plain language a non-medical patient can understand.
2. NEVER provide a definitive diagnosis. You may discuss possibilities, general
   information, and what a finding commonly means, but always frame it as
   informational, not diagnostic.
3. Always end your answer by reminding the user to consult a licensed physician
   for an actual diagnosis or treatment plan.
4. If asked about emergency symptoms (e.g. severe chest pain, difficulty breathing),
   advise the user to seek immediate/emergency medical care.
"""


async def _call_anthropic(prompt: str, system: str) -> str:
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": settings.LLM_API_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": settings.LLM_MODEL,
                "max_tokens": 500,
                "system": system,
                "messages": [{"role": "user", "content": prompt}],
            },
        )
        resp.raise_for_status()
        data = resp.json()
        parts = [b["text"] for b in data.get("content", []) if b.get("type") == "text"]
        return "\n".join(parts).strip()


async def _call_openai(prompt: str, system: str) -> str:
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {settings.LLM_API_KEY}"},
            json={
                "model": settings.LLM_MODEL,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt},
                ],
                "max_tokens": 500,
            },
        )
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"].strip()


async def _call_gemini(prompt: str, system: str) -> str:
    # Gemini 1.0/1.5 models are fully shut down (return 404). Default to a
    # current GA model if none is configured. Auth uses the x-goog-api-key
    # header, per Google's current docs -- this works for both legacy
    # "AIza..." Standard keys and the newer "AQ...." Auth keys.
    model = settings.LLM_MODEL or "gemini-3.6-flash"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            url,
            headers={
                "x-goog-api-key": settings.LLM_API_KEY,
                "Content-Type": "application/json",
            },
            json={
                "system_instruction": {"parts": [{"text": system}]},
                "contents": [{"role": "user", "parts": [{"text": prompt}]}],
                "generationConfig": {"maxOutputTokens": 500},
            },
        )
        resp.raise_for_status()
        data = resp.json()
        candidates = data.get("candidates", [])
        if not candidates:
            raise ValueError("Gemini returned no candidates")
        parts = candidates[0].get("content", {}).get("parts", [])
        return "".join(p.get("text", "") for p in parts).strip()


def _template_fallback(prompt: str) -> str:
    return (
        "I'm currently running in offline/template mode (no LLM API key configured). "
        "Here is a general, non-diagnostic response based on your question:\n\n"
        f"You asked about: \"{prompt.strip()[:200]}\". "
        "In general, chest X-ray findings should always be interpreted together with your "
        "symptoms, medical history, and a physical exam by a qualified clinician. "
        "Please consult a licensed physician for an accurate diagnosis and treatment plan."
    )


async def generate_response(prompt: str, system: str = MEDICAL_SYSTEM_PROMPT) -> str:
    """Route to the configured provider, falling back to a template if unavailable."""
    if settings.LLM_PROVIDER == "anthropic" and settings.LLM_API_KEY:
        try:
            return await _call_anthropic(prompt, system)
        except Exception as exc:
            print(f"LLM call failed (provider=anthropic): {exc}")
            return _template_fallback(prompt)
    elif settings.LLM_PROVIDER == "openai" and settings.LLM_API_KEY:
        try:
            return await _call_openai(prompt, system)
        except Exception as exc:
            print(f"LLM call failed (provider=openai): {exc}")
            return _template_fallback(prompt)
    elif settings.LLM_PROVIDER == "gemini" and settings.LLM_API_KEY:
        try:
            return await _call_gemini(prompt, system)
        except Exception as exc:
            print(f"LLM call failed (provider=gemini): {exc}")
            return _template_fallback(prompt)
    else:
        return _template_fallback(prompt)