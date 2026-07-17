"""
image_generator.py
--------------------
Generates a photorealistic garden image from a text prompt using
Hugging Face Inference Providers, via huggingface_hub's InferenceClient
with provider="auto" (lets HF route the request to whichever provider
currently serves the chosen model).

Includes basic retry-with-backoff logic and clear error handling so the
Streamlit app can show a friendly message instead of a raw traceback.
"""

from __future__ import annotations

import os
import time

from huggingface_hub import InferenceClient
from huggingface_hub.errors import HfHubHTTPError
from PIL import Image

from config import DEFAULT_HF_IMAGE_MODEL

MAX_RETRIES = 3
BASE_BACKOFF_SECONDS = 2  # doubles each retry: 2s, 4s, 8s...


class ImageGeneratorError(Exception):
    """Raised when image generation fails after all retries are exhausted."""


def _get_hf_token() -> str:
    """
    Build a Hugging Face token from the environment or Streamlit secrets.
    Never hardcode the token.
    """
    token = os.environ.get("HF_TOKEN")

    if not token:
        try:
            import streamlit as st  # local import: only needed if running in Streamlit

            token = st.secrets.get("HF_TOKEN")  # type: ignore[union-attr]
        except Exception:
            token = None

    if not token:
        raise ImageGeneratorError(
            "HF_TOKEN is not set. Add it to your environment, a .env file, "
            "or your Streamlit secrets.toml."
        )

    return token


def generate_garden_image(
    prompt: str,
    model: str = DEFAULT_HF_IMAGE_MODEL,
    max_retries: int = MAX_RETRIES,
) -> Image.Image:
    """
    Generate a photorealistic garden image from `prompt` using Hugging Face
    Inference Providers (provider="auto").

    Retries transient failures (rate limits, model-loading/cold-start,
    timeouts) with exponential backoff. Raises ImageGeneratorError if every
    attempt fails, with a message describing the last error encountered.
    """
    if not prompt or not prompt.strip():
        raise ImageGeneratorError("Cannot generate an image from an empty prompt.")

    token = _get_hf_token()
    client = InferenceClient(provider="auto", api_key=token)

    last_error: Exception | None = None

    for attempt in range(1, max_retries + 1):
        try:
            image = client.text_to_image(prompt, model=model)
            if image is None:
                raise ImageGeneratorError("The image provider returned no image data.")
            return image

        except HfHubHTTPError as exc:
            last_error = exc
            status_code = getattr(exc.response, "status_code", None)

            # 503 usually means the model is loading / cold-starting on the
            # provider's infrastructure — worth retrying. 429 means we're
            # rate-limited — also worth retrying with backoff. Other 4xx
            # errors (401, 404, etc.) are not going to fix themselves, so
            # fail fast instead of burning retries.
            if status_code not in (429, 503) and attempt < max_retries:
                raise ImageGeneratorError(
                    f"Hugging Face request failed with a non-retryable error "
                    f"(status {status_code}): {exc}"
                ) from exc

        except Exception as exc:  # noqa: BLE001 - network errors, timeouts, etc.
            last_error = exc

        if attempt < max_retries:
            backoff = BASE_BACKOFF_SECONDS * (2 ** (attempt - 1))
            time.sleep(backoff)

    raise ImageGeneratorError(
        f"Image generation failed after {max_retries} attempts. "
        f"Last error: {last_error}"
    )
