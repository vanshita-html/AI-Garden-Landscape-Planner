"""
app.py
------
Streamlit front-end for the Garden & Landscape Planner.

Layout: a two-column "studio" view — the form lives in the left column,
the generated image (or a placeholder) lives in the right column, similar
to typical AI image-generation tools.

Flow:
  1. User picks plot size, garden style, plant type, season, color theme,
     and (optionally) which image model to render with.
  2. On submit, Groq (llama-3.3-70b-versatile) turns those choices into a
     rich photorealistic image-generation prompt.
  3. Hugging Face Inference Providers renders that prompt into an image.
  4. The image (and the prompt used) are shown in the right-hand panel,
     with a download button.

All styling lives in this file (a single injected <style> block) so the
app is self-contained.
"""

from __future__ import annotations

import io
import textwrap

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
    page_title="Garden & Landscape Planner",
    page_icon="🌿",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Theme: white background, near-black text, a single green accent used in a
# light tint (badges, hover fills) and a rich/dark shade (buttons, borders).
# Every multi-line HTML string below is passed through textwrap.dedent()
# .strip() before rendering — Markdown treats 4-space indented text as a
# preformatted code block, which is what caused raw tags to show up
# literally in an earlier version of this file.
# ---------------------------------------------------------------------------
CSS = textwrap.dedent(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Sora:wght@600;700;800&family=Inter:wght@400;500;600&display=swap');

    :root {
      --bg: #FFFFFF;
      --surface: #FFFFFF;
      --field-bg: #FFFFFF;
      --border: #E5E7EB;
      --ink: #111111;
      --ink-soft: #6B7280;
      --green: #16A34A;
      --green-dark: #0F7B3D;
      --green-deep: #0B5C2D;
      --green-light: #DCFCE7;
      --green-mid: #22C55E;
      --focus: #16A34A;
    }

    html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
      background: var(--bg) !important;
    }
    * { font-family: 'Inter', -apple-system, sans-serif; }

    [data-testid="stHeader"] { background: transparent; }
    .block-container { padding-top: 2.5rem; padding-bottom: 3rem; max-width: 1180px; }

    /* ---------- Header (full width, above the two columns) ---------- */
    #gp-header { margin-bottom: 2.25rem; }
    #gp-header .gp-titlebar {
      display: flex;
      align-items: center;
      gap: 0.7rem;
      margin-bottom: 0.6rem;
    }
    #gp-header .gp-logo {
      width: 40px; height: 40px;
      border-radius: 12px;
      background: linear-gradient(135deg, var(--green-mid), var(--green-deep));
      display: flex; align-items: center; justify-content: center;
      font-size: 1.2rem;
      flex-shrink: 0;
    }
    #gp-header .gp-title {
      font-family: 'Sora', sans-serif !important;
      font-weight: 700 !important;
      font-size: 2.1rem !important;
      color: var(--green) !important;
      letter-spacing: -0.02em !important;
      margin: 0 !important;
      line-height: 1.1 !important;
    }
    #gp-header .gp-tagline {
      font-family: 'Inter', sans-serif !important;
      color: var(--ink-soft) !important;
      font-size: 1rem !important;
      margin: 0 !important;
    }
    #gp-header .gp-tagline strong { color: var(--ink) !important; font-weight: 600 !important; }
    #gp-header .gp-tagline .gp-dot { color: var(--green); margin: 0 0.5rem; }

    /* ---------- Left column: form ---------- */
    .gp-badge {
      display: inline-flex;
      align-items: center;
      gap: 0.4rem;
      background: var(--green-light);
      color: var(--green-deep);
      font-size: 0.78rem;
      font-weight: 600;
      padding: 0.35rem 0.75rem;
      border-radius: 999px;
      margin-bottom: 0.9rem;
    }
    [data-testid="stForm"] {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 16px;
      padding: 1.75rem 1.6rem;
      box-shadow: 0 1px 2px rgba(17,17,17,0.03), 0 6px 18px -12px rgba(17,17,17,0.10);
    }
    [data-testid="stForm"] label p {
      font-family: 'Inter', sans-serif;
      font-size: 0.72rem;
      font-weight: 600;
      letter-spacing: 0.06em;
      text-transform: uppercase;
      color: var(--ink-soft);
    }
    [data-testid="stForm"] [data-baseweb="select"] > div {
      background: var(--field-bg);
      border-radius: 10px;
      border: 1px solid var(--border);
      transition: border-color 0.15s ease, box-shadow 0.15s ease;
    }
    [data-testid="stForm"] [data-baseweb="select"] span { color: var(--ink) !important; }
    [data-testid="stForm"] [data-baseweb="select"] > div:hover { border-color: var(--green); }
    [data-testid="stForm"] [data-baseweb="select"] > div:focus-within {
      border-color: var(--green);
      box-shadow: 0 0 0 3px rgba(22,163,74,0.16);
    }

    [data-testid="stExpander"] {
      border: 1px solid var(--border);
      border-radius: 14px;
      background: var(--surface);
      overflow: hidden;
      margin-top: 1rem;
    }
    [data-testid="stExpander"] summary { font-weight: 600; color: var(--ink); }
    [data-testid="stExpander"] p { color: var(--ink-soft); line-height: 1.6; }

    .stFormSubmitButton > button {
      background: var(--green);
      color: #FFFFFF !important;
      border: none;
      border-radius: 12px;
      padding: 0.85rem 1.4rem;
      font-family: 'Sora', sans-serif;
      font-weight: 700;
      font-size: 1.02rem;
      letter-spacing: 0.01em;
      transition: transform 0.15s ease, box-shadow 0.15s ease, background 0.15s ease;
      box-shadow: 0 10px 22px -10px rgba(22,163,74,0.55);
    }
    .stFormSubmitButton > button:hover {
      background: var(--green-dark);
      transform: translateY(-1px);
      box-shadow: 0 14px 26px -10px rgba(22,163,74,0.6);
      color: #FFFFFF !important;
    }
    .stFormSubmitButton > button:focus-visible {
      outline: 3px solid var(--green-mid);
      outline-offset: 2px;
    }

    /* ---------- Right column: result panel ---------- */
    .gp-result-panel {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 16px;
      min-height: 480px;
      display: flex;
      flex-direction: column;
      overflow: hidden;
    }
    .gp-placeholder {
      flex: 1;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 0.75rem;
      background: var(--green-light);
      color: var(--green-deep);
      text-align: center;
      padding: 2rem;
      border-radius: 16px;
      min-height: 480px;
    }
    .gp-placeholder .gp-placeholder-icon { font-size: 2.4rem; }
    .gp-placeholder p {
      color: var(--green-deep) !important;
      font-size: 0.98rem;
      max-width: 32ch;
      margin: 0 !important;
    }
    .gp-result-title {
      font-family: 'Sora', sans-serif;
      font-weight: 700;
      font-size: 1.15rem;
      color: var(--ink);
      margin: 0 0 0.75rem !important;
    }
    [data-testid="stImage"] img { border-radius: 12px; }

    .stDownloadButton > button {
      background: #FFFFFF;
      color: var(--green) !important;
      border: 1.5px solid var(--green);
      border-radius: 12px;
      padding: 0.65rem 1.4rem;
      font-family: 'Sora', sans-serif;
      font-weight: 600;
      transition: background 0.15s ease, transform 0.15s ease;
    }
    .stDownloadButton > button:hover { background: var(--green-light); transform: translateY(-1px); }
    .stDownloadButton > button:focus-visible {
      outline: 3px solid var(--green-mid);
      outline-offset: 2px;
    }

    @media (prefers-reduced-motion: no-preference) {
      .gp-fade-in { animation: gpFadeIn 0.5s ease both; }
    }
    @keyframes gpFadeIn {
      from { opacity: 0; transform: translateY(6px); }
      to { opacity: 1; transform: none; }
    }

    .gp-footer {
      text-align: center;
      color: var(--ink-soft);
      font-size: 0.85rem;
      margin-top: 2.4rem;
    }
    </style>
    """
).strip()

HEADER_HTML = textwrap.dedent(
    """
    <div id="gp-header">
    <div class="gp-titlebar">
    <div class="gp-logo">🌿</div>
    <h1 class="gp-title">Garden &amp; Landscape Planner</h1>
    </div>
    <p class="gp-tagline">
    <strong>AI-powered garden design</strong><span class="gp-dot">•</span>Photorealistic renders from a few dropdowns
    </p>
    </div>
    """
).strip()

FOOTER_HTML = textwrap.dedent(
    """
    <p class="gp-footer">
    Powered by Groq (llama-3.3-70b-versatile) for design concepts and
    Hugging Face Inference Providers for image generation.
    </p>
    """
).strip()

PLACEHOLDER_HTML = textwrap.dedent(
    """
    <div class="gp-placeholder">
    <div class="gp-placeholder-icon">🖼️</div>
    <p>Your photorealistic garden design will appear here once you generate it.</p>
    </div>
    """
).strip()

st.markdown(CSS, unsafe_allow_html=True)
st.markdown(HEADER_HTML, unsafe_allow_html=True)

if "result_image" not in st.session_state:
    st.session_state.result_image = None
if "result_prompt" not in st.session_state:
    st.session_state.result_prompt = None

left_col, right_col = st.columns([1, 1.15], gap="large")

# ---------------------------------------------------------------------------
# Left column: form
# ---------------------------------------------------------------------------
with left_col:
    st.markdown('<span class="gp-badge">🌱 Design options</span>', unsafe_allow_html=True)

    with st.form("garden_form"):
        col1, col2 = st.columns(2)

        with col1:
            plot_size_label = st.selectbox("📐 Plot size", options=list(PLOT_SIZES.keys()))
            garden_style = st.selectbox("🎌 Garden style", options=GARDEN_STYLES)
            plant_type = st.selectbox("🌸 Dominant plant type", options=PLANT_TYPES)

        with col2:
            season = st.selectbox("☀️ Season", options=SEASONS)
            color_theme = st.selectbox("🎨 Color theme", options=COLOR_THEMES)
            image_model = st.selectbox(
                "🖼️ Image model",
                options=HF_IMAGE_MODEL_OPTIONS,
                help="Advanced: choose which model renders the final image.",
            )

        submitted = st.form_submit_button("Generate garden design", use_container_width=True)

    if st.session_state.result_prompt:
        with st.expander("Design concept (AI-generated prompt)", expanded=False):
            st.write(st.session_state.result_prompt)

# ---------------------------------------------------------------------------
# Generation flow
# ---------------------------------------------------------------------------
if submitted:
    st.session_state.result_image = None
    st.session_state.result_prompt = None

    plot_size_desc = PLOT_SIZES[plot_size_label]

    with right_col:
        with st.spinner("Sketching the design concept..."):
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
            with st.spinner("Rendering a photorealistic preview..."):
                try:
                    image = generate_garden_image(prompt, model=image_model)
                    st.session_state.result_image = image
                except ImageGeneratorError as exc:
                    st.error(f"Couldn't generate the image: {exc}")

# ---------------------------------------------------------------------------
# Right column: result panel
# ---------------------------------------------------------------------------
with right_col:
    if st.session_state.result_image:
        st.markdown('<div class="gp-fade-in">', unsafe_allow_html=True)
        st.markdown('<p class="gp-result-title">Your garden design</p>', unsafe_allow_html=True)
        st.image(st.session_state.result_image, use_container_width=True)

        buffer = io.BytesIO()
        st.session_state.result_image.save(buffer, format="PNG")

        st.download_button(
            label="Download image",
            data=buffer.getvalue(),
            file_name="garden_design.png",
            mime="image/png",
            use_container_width=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)
    elif not submitted:
        st.markdown(PLACEHOLDER_HTML, unsafe_allow_html=True)

st.markdown(FOOTER_HTML, unsafe_allow_html=True)
