"""
app.py
------
Streamlit front-end for the AI Garden / Landscape Planner.

Flow:
  1. User picks plot size, garden style, plant type, season, color theme
     (and optionally which HF image model to use).
  2. On submit, Groq (llama-3.3-70b-versatile) turns those choices into a
     rich photorealistic image-generation prompt.
  3. Hugging Face Inference Providers renders that prompt into an image.
  4. The image (and the prompt used) are shown in a result panel, with a
     download button for the image.
"""

from __future__ import annotations

import io

import streamlit as st

# python-dotenv is only needed for local development (loading a .env file).
# On Streamlit Cloud, secrets come from st.secrets instead, so we don't want
# a missing/stale dotenv install to crash the whole app.
try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv(*args, **kwargs):  # type: ignore[no-redef]
        return False

from config import (
    COLOR_THEMES,
    GARDEN_STYLES,
    HF_IMAGE_MODEL_OPTIONS,
    PLANT_TYPES,
    PLOT_SIZES,
    SEASONS,
)
from image_generator import ImageGeneratorError, generate_garden_image
from prompt_builder import PromptBuilderError, build_garden_prompt

load_dotenv()  # no-op in production/Streamlit Cloud, convenient for local dev

st.set_page_config(
    page_title="AI Garden & Landscape Planner",
    page_icon="🌿",
    layout="centered",
)

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.title("🌿 AI Garden & Landscape Planner")
st.caption(
    "Describe your dream garden with a few dropdowns — an AI landscape "
    "designer writes the concept, and an AI artist renders it."
)

if "result_image" not in st.session_state:
    st.session_state.result_image = None
if "result_prompt" not in st.session_state:
    st.session_state.result_prompt = None

# ---------------------------------------------------------------------------
# Form
# ---------------------------------------------------------------------------
with st.form("garden_form"):
    col1, col2 = st.columns(2)

    with col1:
        plot_size_label = st.selectbox("Plot size", options=list(PLOT_SIZES.keys()))
        garden_style = st.selectbox("Garden style", options=GARDEN_STYLES)
        plant_type = st.selectbox("Dominant plant type", options=PLANT_TYPES)

    with col2:
        season = st.selectbox("Season", options=SEASONS)
        color_theme = st.selectbox("Color theme", options=COLOR_THEMES)
        image_model = st.selectbox(
            "Image model (advanced)", options=HF_IMAGE_MODEL_OPTIONS
        )

    submitted = st.form_submit_button("🌱 Generate My Garden Design", use_container_width=True)

# ---------------------------------------------------------------------------
# Generation flow
# ---------------------------------------------------------------------------
if submitted:
    st.session_state.result_image = None
    st.session_state.result_prompt = None

    plot_size_desc = PLOT_SIZES[plot_size_label]

    with st.spinner("👩‍🎨 Our AI landscape designer is sketching the concept..."):
        try:
            prompt = build_garden_prompt(
                plot_size_desc=plot_size_desc,
                garden_style=garden_style,
                plant_type=plant_type,
                season=season,
                color_theme=color_theme,
            )
        except PromptBuilderError as exc:
            st.error(f"Couldn't build the design prompt: {exc}")
            prompt = None

    if prompt:
        st.session_state.result_prompt = prompt
        with st.spinner("🎨 Rendering a photorealistic preview of your garden..."):
            try:
                image = generate_garden_image(prompt, model=image_model)
                st.session_state.result_image = image
            except ImageGeneratorError as exc:
                st.error(f"Couldn't generate the image: {exc}")

# ---------------------------------------------------------------------------
# Result panel
# ---------------------------------------------------------------------------
if st.session_state.result_prompt:
    with st.expander("📝 Design concept (AI-generated prompt)", expanded=False):
        st.write(st.session_state.result_prompt)

if st.session_state.result_image:
    st.subheader("Your Garden Design")
    st.image(st.session_state.result_image, use_container_width=True)

    buffer = io.BytesIO()
    st.session_state.result_image.save(buffer, format="PNG")

    st.download_button(
        label="⬇️ Download image",
        data=buffer.getvalue(),
        file_name="garden_design.png",
        mime="image/png",
        use_container_width=True,
    )

st.divider()
st.caption(
    "Powered by Groq (llama-3.3-70b-versatile) for design concepts and "
    "Hugging Face Inference Providers for image generation."
)
