"""
Thin wrapper so the rest of the app doesn't care whether the user
plugs in a Google Gemini key, OpenAI key, or Anthropic key. 
Keys are supplied at runtime via the Streamlit sidebar (session_state) or environment variables.
"""
import json
import os
import re
import streamlit as st

try:
    import json_repair
except ImportError:
    json_repair = None


def get_provider_and_key():
    provider = st.session_state.get("llm_provider", "Google Gemini")
    key = st.session_state.get("llm_api_key", "").strip()
    if not key:
        if provider in ("Google Gemini", "Gemini"):
            key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY", "")
        elif provider == "OpenAI":
            key = os.environ.get("OPENAI_API_KEY", "")
        elif provider == "Anthropic":
            key = os.environ.get("ANTHROPIC_API_KEY", "")
    return provider, key


def call_llm(system: str, user: str, max_tokens: int = 4096, json_mode: bool = False) -> str:
    """
    Calls whichever provider is configured in the sidebar.
    Returns raw text. If json_mode, caller is expected to parse it.
    """
    provider, key = get_provider_and_key()

    if not key:
        raise RuntimeError(
            f"No API key set for {provider}. Please enter your {provider} API key in the sidebar."
        )

    if provider in ("Google Gemini", "Gemini"):
        try:
            from google import genai
            from google.genai import types
            client = genai.Client(api_key=key)
            
            config_args = {
                "max_output_tokens": max_tokens,
            }
            if system:
                config_args["system_instruction"] = system
            if json_mode:
                config_args["response_mime_type"] = "application/json"
                
            config = types.GenerateContentConfig(**config_args)
            resp = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=user,
                config=config,
            )
            return resp.text or ""
        except Exception as e1:
            try:
                import google.generativeai as ggenai
                ggenai.configure(api_key=key)
                gen_config = {}
                if json_mode:
                    gen_config["response_mime_type"] = "application/json"
                gmodel = ggenai.GenerativeModel(
                    "gemini-1.5-flash",
                    system_instruction=system if system else None,
                    generation_config=gen_config if gen_config else None
                )
                resp = gmodel.generate_content(user)
                return resp.text or ""
            except Exception as e2:
                raise RuntimeError(f"Google Gemini call failed: {e1} | {e2}")

    elif provider == "Anthropic":
        import anthropic
        client = anthropic.Anthropic(api_key=key)
        resp = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        return "".join(b.text for b in resp.content if b.type == "text")

    elif provider == "OpenAI":
        from openai import OpenAI
        client = OpenAI(api_key=key)
        kwargs = {
            "model": "gpt-4o-mini",
            "max_tokens": max_tokens,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        }
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}
        resp = client.chat.completions.create(**kwargs)
        return resp.choices[0].message.content or ""

    raise ValueError(f"Unknown provider: {provider}")


def call_llm_json(system: str, user: str, max_tokens: int = 4096) -> dict:
    """Calls the LLM and parses JSON out of the response robustly."""
    raw = call_llm(system, user, max_tokens=max_tokens, json_mode=True)
    if not raw or not raw.strip():
        raise ValueError("LLM returned empty response")

    cleaned = raw.strip()

    # Stripping markdown fences if present
    if "```" in cleaned:
        match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", cleaned, re.IGNORECASE)
        if match:
            cleaned = match.group(1).strip()
        else:
            cleaned = cleaned.replace("```json", "").replace("```", "").strip()

    # Extracting substring bounded by { ... } or [ ... ]
    first_brace = cleaned.find("{")
    last_brace = cleaned.rfind("}")
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        cleaned = cleaned[first_brace:last_brace + 1]

    # Attempt standard json parse
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # Fallback to json_repair if available
        if json_repair:
            parsed = json_repair.repair_json(raw, return_objects=True)
            if isinstance(parsed, dict) and parsed:
                return parsed
            if isinstance(parsed, list):
                return {"items": parsed}
        raise


def sidebar_llm_config():
    """Renders the shared sidebar block for choosing provider + entering API key."""
    st.sidebar.markdown("### 🔑 AI Configuration")
    provider = st.sidebar.selectbox("LLM Provider", ["Google Gemini", "OpenAI", "Anthropic"], key="llm_provider")
    st.sidebar.text_input(
        f"{provider} API Key",
        type="password",
        key="llm_api_key",
        help="Your key is only used for this session and is never stored or sent anywhere else.",
    )
    st.sidebar.caption(
        "Get a key from aistudio.google.com, platform.openai.com, or console.anthropic.com."
    )
