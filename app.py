"""
app.py
------
Streamlit front-end for the Garden & Landscape Planner.

Flow:
  1. User picks plot size, garden style, plant type, season, color theme,
     and (optionally) which image model to render with.
  2. On submit, Groq (llama-3.3-70b-versatile) turns those choices into a
     rich photorealistic image-generation prompt.
  3. Hugging Face Inference Providers renders that prompt into an image.
  4. The image (and the prompt used) are shown in a result panel, with a
     download button for the image.

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
    layout="centered",
)

# ---------------------------------------------------------------------------
# Theme
# ---------------------------------------------------------------------------
# A clean, modern SaaS-style theme: neutral cool-gray surface, a single
# confident green accent, Sora for headings paired with Inter for UI/body
# text. Every multi-line HTML string below is passed through
# textwrap.dedent().strip() before rendering — Markdown treats 4-space
# indented text as a preformatted code block, which is what caused the
# raw tags to show up literally in the previous version.
CSS = textwrap.dedent(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Sora:wght@500;600;700;800&family=Inter:wght@400;500;600&display=swap');

    :root {
      --bg: #F5F6F8;
      --surface: #FFFFFF;
      --border: #E4E7EC;
      --ink: #111827;
      --ink-soft: #667085;
      --green: #16A34A;
      --teal: #0D9488;
      --gold: #F59E0B;
      --accent-soft: #E7F4EC;
      --focus: #F59E0B;
      --hero-deep: #0B1F14;
      --hero-mid: #123324;
      --hero-glow-1: #F59E0B;
      --hero-glow-2: #2DD4BF;
    }

    html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
      background: var(--bg) !important;
    }
    * { font-family: 'Inter', -apple-system, sans-serif; }

    [data-testid="stHeader"] { background: transparent; }
    .block-container { padding-top: 2.25rem; padding-bottom: 3rem; max-width: 720px; }

    /* ---------- Hero header: dark, gradient, glowing ---------- */
    #gp-header {
      position: relative;
      overflow: hidden;
      background: radial-gradient(120% 150% at 12% -10%, var(--hero-mid) 0%, var(--hero-deep) 60%);
      border-radius: 26px;
      padding: 2.75rem 2.5rem;
      margin-bottom: 2rem;
      box-shadow: 0 24px 48px -22px rgba(11,31,20,0.55);
    }
    #gp-header::before,
    #gp-header::after {
      content: '';
      position: absolute;
      border-radius: 50%;
      filter: blur(18px);
      z-index: 0;
    }
    #gp-header::before {
      width: 260px; height: 260px;
      background: radial-gradient(circle, rgba(245,158,11,0.35), transparent 70%);
      top: -100px; right: -70px;
    }
    #gp-header::after {
      width: 240px; height: 240px;
      background: radial-gradient(circle, rgba(45,212,191,0.30), transparent 70%);
      bottom: -110px; left: 8%;
    }
    #gp-header .gp-eyebrow {
      position: relative; z-index: 1;
      display: inline-flex;
      align-items: center;
      gap: 0.4rem;
      background: linear-gradient(135deg, var(--hero-glow-1), #FDE68A);
      color: var(--hero-deep) !important;
      font-size: 0.72rem !important;
      font-weight: 700 !important;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      padding: 0.35rem 0.75rem;
      border-radius: 999px;
      margin: 0 0 1.25rem;
    }
    #gp-header .gp-title {
      position: relative; z-index: 1;
      font-family: 'Sora', sans-serif !important;
      font-weight: 700 !important;
      font-size: 3rem !important;
      color: #F5F7F2 !important;
      letter-spacing: -0.03em !important;
      line-height: 1.08 !important;
      margin: 0 0 0.9rem !important;
    }
    #gp-header .gp-title-accent {
      background: linear-gradient(135deg, #4ADE80, #FDE68A) !important;
      -webkit-background-clip: text !important;
      background-clip: text !important;
      color: transparent !important;
    }
    #gp-header .gp-tagline {
      position: relative; z-index: 1;
      font-family: 'Inter', sans-serif !important;
      color: rgba(245,247,242,0.75) !important;
      font-size: 1.1rem !important;
      line-height: 1.6 !important;
      max-width: 52ch;
      margin: 0 !important;
    }
    @media (max-width: 480px) {
      #gp-header .gp-title { font-size: 2.15rem !important; }
    }

    /* ---------- Form card ---------- */
    [data-testid="stForm"] {
      position: relative;
      overflow: hidden;
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 20px;
      padding: 2.25rem 2.1rem 1.6rem;
      box-shadow: 0 1px 2px rgba(16,24,40,0.04), 0 8px 24px -12px rgba(16,24,40,0.10);
    }
    [data-testid="stForm"]::before {
      content: '';
      position: absolute; top: 0; left: 0; right: 0; height: 5px;
      background: linear-gradient(90deg, var(--green), var(--teal), var(--gold));
    }
    [data-testid="stForm"] label p {
      font-family: 'Inter', sans-serif;
      font-size: 0.72rem;
      font-weight: 600;
      letter-spacing: 0.07em;
      text-transform: uppercase;
      color: var(--ink-soft);
    }
    [data-testid="stForm"] [data-baseweb="select"] > div {
      background: var(--bg);
      border-radius: 10px;
      border: 1px solid var(--border);
      transition: border-color 0.15s ease, box-shadow 0.15s ease;
    }
    [data-testid="stForm"] [data-baseweb="select"] > div:hover {
      border-color: var(--teal);
    }
    /* Two-tone focus color: left column glows green, right column glows teal */
    [data-testid="stForm"] [data-testid="stColumn"]:nth-of-type(1) [data-baseweb="select"] > div:focus-within,
    [data-testid="stForm"] [data-testid="column"]:nth-of-type(1) [data-baseweb="select"] > div:focus-within {
      border-color: var(--green);
      box-shadow: 0 0 0 3px rgba(22,163,74,0.18);
    }
    [data-testid="stForm"] [data-testid="stColumn"]:nth-of-type(2) [data-baseweb="select"] > div:focus-within,
    [data-testid="stForm"] [data-testid="column"]:nth-of-type(2) [data-baseweb="select"] > div:focus-within {
      border-color: var(--teal);
      box-shadow: 0 0 0 3px rgba(13,148,136,0.18);
    }

    [data-testid="stExpander"] {
      border: 1px solid var(--border);
      border-left: 4px solid var(--gold);
      border-radius: 16px;
      background: var(--surface);
      overflow: hidden;
      box-shadow: 0 1px 2px rgba(16,24,40,0.04);
    }
    [data-testid="stExpander"] summary {
      font-family: 'Inter', sans-serif;
      font-weight: 600;
      color: var(--ink);
    }
    [data-testid="stExpander"] p { color: var(--ink-soft); line-height: 1.6; }

    .stFormSubmitButton > button {
      background: linear-gradient(135deg, var(--green), var(--teal));
      color: #FFFFFF !important;
      border: none;
      border-radius: 12px;
      padding: 0.75rem 1.4rem;
      font-family: 'Sora', sans-serif;
      font-weight: 600;
      letter-spacing: 0.01em;
      transition: transform 0.15s ease, box-shadow 0.15s ease, filter 0.15s ease;
      box-shadow: 0 10px 24px -10px rgba(13,148,136,0.55);
    }
    .stFormSubmitButton > button:hover {
      filter: brightness(1.08);
      transform: translateY(-1px);
      box-shadow: 0 14px 28px -10px rgba(13,148,136,0.6);
      color: #FFFFFF !important;
    }

    .stDownloadButton > button {
      background: var(--surface);
      color: var(--teal) !important;
      border: 1.5px solid var(--teal);
      border-radius: 12px;
      padding: 0.7rem 1.4rem;
      font-family: 'Sora', sans-serif;
      font-weight: 600;
      transition: background 0.15s ease, transform 0.15s ease;
    }
    .stDownloadButton > button:hover {
      background: var(--accent-soft);
      transform: translateY(-1px);
    }

    .stFormSubmitButton > button:focus-visible,
    .stDownloadButton > button:focus-visible {
      outline: 3px solid var(--focus);
      outline-offset: 2px;
    }

    [data-testid="stVerticalBlockBorderWrapper"] {
      position: relative;
      overflow: hidden;
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 20px;
      box-shadow: 0 1px 2px rgba(16,24,40,0.04), 0 8px 24px -12px rgba(16,24,40,0.10);
    }
    [data-testid="stVerticalBlockBorderWrapper"]::before {
      content: '';
      position: absolute; top: 0; left: 0; right: 0; height: 5px;
      background: linear-gradient(90deg, var(--gold), var(--green), var(--teal));
    }
    .gp-result-title {
      font-family: 'Sora', sans-serif;
      font-weight: 600;
      font-size: 1.35rem;
      color: var(--ink);
      margin: 0.1rem 0 0.9rem;
    }
    [data-testid="stImage"] img { border-radius: 12px; }

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
    <span class="gp-eyebrow">🌱 AI Design Studio</span>
    <h1 class="gp-title">Garden &amp; <span class="gp-title-accent">Landscape</span> Planner</h1>
    <p class="gp-tagline">
    Choose a few details about your space, and an AI landscape designer
    writes the concept while an AI artist renders it.
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

st.markdown(CSS, unsafe_allow_html=True)
st.markdown(HEADER_HTML, unsafe_allow_html=True)

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

# ---------------------------------------------------------------------------
# Generation flow
# ---------------------------------------------------------------------------
if submitted:
    st.session_state.result_image = None
    st.session_state.result_prompt = None

    plot_size_desc = PLOT_SIZES[plot_size_label]

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
# Result panel
# ---------------------------------------------------------------------------
if st.session_state.result_prompt:
    st.write("")
    with st.expander("Design concept (AI-generated prompt)", expanded=False):
        st.write(st.session_state.result_prompt)

if st.session_state.result_image:
    st.write("")
    with st.container(border=True):
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

st.markdown(FOOTER_HTML, unsafe_allow_html=True)
