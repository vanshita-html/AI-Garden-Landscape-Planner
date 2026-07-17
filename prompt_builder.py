"""
prompt_builder.py
------------------
Turns the user's dropdown selections into a single, rich, photorealistic
image-generation prompt by calling a Groq-hosted LLM (llama-3.3-70b-versatile).

The heavy lifting of "understanding" what a Japanese Zen garden with bamboo
and a monochrome-green color theme should look like is delegated to the LLM;
this module is only responsible for:
  1. Building a good system/user prompt for that LLM call.
  2. Making the API call (with basic error handling).
  3. Returning clean prompt text ready to hand to the image generator.
"""

from __future__ import annotations

import os

from groq import Groq

from config import GROQ_MODEL


class PromptBuilderError(Exception):
    """Raised when the Groq API call fails or returns something unusable."""


def _get_groq_client() -> Groq:
    """
    Build a Groq client using an API key from the environment or Streamlit
    secrets. Never hardcode the key.
    """
    api_key = os.environ.get("GROQ_API_KEY")

    if not api_key:
        try:
            import streamlit as st  # local import: only needed if running in Streamlit

            api_key = st.secrets.get("GROQ_API_KEY")  # type: ignore[union-attr]
        except Exception:
            api_key = None

    if not api_key:
        raise PromptBuilderError(
            "GROQ_API_KEY is not set. Add it to your environment, a .env file, "
            "or your Streamlit secrets.toml."
        )

    return Groq(api_key=api_key)


def _build_messages(
    plot_size_desc: str,
    garden_style: str,
    plant_type: str,
    season: str,
    color_theme: str,
) -> list[dict]:
    system_prompt = (
        "You are an expert landscape designer and prompt engineer for "
        "photorealistic AI image generation. Given a set of garden design "
        "choices, you write a single, vivid, highly detailed image-generation "
        "prompt describing the finished garden as if it were a professional "
        "landscape photograph. "
        "Your prompt must describe: the layout and hardscaping (paths, "
        "borders, seating, water features, structures if fitting the style), "
        "the dominant plants and how they're arranged, the color palette and "
        "lighting appropriate for the season, and the overall mood. "
        "Always end the prompt with photography/quality descriptors such as "
        "'photorealistic, ultra-detailed, natural lighting, shot on a DSLR, "
        "8k, professional landscape photography'. "
        "Respond with ONLY the final image-generation prompt text — no "
        "preamble, no explanations, no markdown, no quotation marks."
    )

    user_prompt = (
        f"Plot size: {plot_size_desc}\n"
        f"Garden style: {garden_style}\n"
        f"Dominant plant type: {plant_type}\n"
        f"Season: {season}\n"
        f"Color theme: {color_theme}\n\n"
        "Write the single best image-generation prompt for this garden."
    )

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]


def build_garden_prompt(
    plot_size_desc: str,
    garden_style: str,
    plant_type: str,
    season: str,
    color_theme: str,
) -> str:
    """
    Call Groq's llama-3.3-70b-versatile model to turn the user's selections
    into a rich, photorealistic garden image-generation prompt.

    Raises PromptBuilderError on any failure (missing key, API error, empty
    response) so the caller (app.py) can show a clean message to the user.
    """
    client = _get_groq_client()
    messages = _build_messages(plot_size_desc, garden_style, plant_type, season, color_theme)

    try:
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=messages,
            temperature=0.8,
            max_tokens=500,
        )
    except Exception as exc:  # noqa: BLE001 - surface any SDK/network error uniformly
        raise PromptBuilderError(f"Groq API request failed: {exc}") from exc

    try:
        content = response.choices[0].message.content
    except (AttributeError, IndexError) as exc:
        raise PromptBuilderError("Groq API returned an unexpected response shape.") from exc

    if not content or not content.strip():
        raise PromptBuilderError("Groq API returned an empty prompt.")

    return content.strip()
