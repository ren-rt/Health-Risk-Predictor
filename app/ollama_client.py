import os
import requests

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")


def get_ai_advice(vitals: dict, risk_level: str) -> str:
    """
    Calls the local Ollama model to generate a plain-English clinical
    summary + next steps. Returns a fallback string if Ollama is
    unreachable, so the rest of the app keeps working (see Fallback
    Plan in the project doc: Ollama is optional).
    """
    prompt = (
        "You are assisting a clinician, not replacing one. "
        f"Patient vitals: {vitals}. "
        f"Predicted maternal health risk level: {risk_level}. "
        "In 3-4 short sentences, explain in plain English what this risk "
        "level generally means and suggest reasonable next steps. "
        "Do not give a definitive diagnosis."
    )

    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False},
            timeout=90,
        )
        response.raise_for_status()
        return response.json().get("response", "").strip()
    except requests.exceptions.RequestException as e:
        return (
            "AI advice unavailable (Ollama not reachable). "
            "Risk level and blockchain logging are unaffected. "
            f"[{e.__class__.__name__}]"
        )