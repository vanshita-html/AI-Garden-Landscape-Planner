# 🌿 AI Garden & Landscape Planner

Pick a plot size, garden style, dominant plant type, season, and color theme —
an LLM (Groq's `llama-3.3-70b-versatile`) turns your choices into a detailed
landscape design brief, and a Hugging Face Inference Providers text-to-image
model renders it as a photorealistic preview.

## Project structure

```
garden-planner/
├── app.py                  # Streamlit UI
├── prompt_builder.py        # Groq call -> rich image-generation prompt
├── image_generator.py       # HF Inference Providers -> image, with retries
├── config.py                 # Dropdown options & model constants
├── requirements.txt
├── .env.example
├── .streamlit/
│   └── config.toml          # Forces a light theme (avoids mobile dark-mode issues)
└── README.md
```

## Setup

1. **Clone / copy the project, then create a virtual environment:**

   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Set your API keys.** Copy `.env.example` to `.env` and fill in your keys:

   ```bash
   cp .env.example .env
   ```

   ```
   GROQ_API_KEY=your_groq_api_key_here
   HF_TOKEN=your_huggingface_token_here
   ```

   - Get a Groq key at https://console.groq.com/keys
   - Get a Hugging Face token at https://huggingface.co/settings/tokens
     (a "read" token is enough — Inference Providers billing/routing happens
     through your HF account)

   **Alternative: Streamlit secrets.** If you're deploying to Streamlit
   Community Cloud (or just prefer secrets over `.env`), create
   `.streamlit/secrets.toml`:

   ```toml
   GROQ_API_KEY = "your_groq_api_key_here"
   HF_TOKEN = "your_huggingface_token_here"
   ```

   The app checks environment variables first and falls back to
   `st.secrets` automatically — no code changes needed either way.

4. **Run the app:**

   ```bash
   streamlit run app.py
   ```

## How it works

1. **Form** — `app.py` renders a form with dropdowns sourced from `config.py`
   (plot size, garden style, plant type, season, color theme, plus an
   "advanced" image-model picker).
2. **Prompt building** — On submit, `prompt_builder.py` sends your selections
   to Groq's `llama-3.3-70b-versatile` model, which writes a single detailed,
   photorealistic image-generation prompt describing the garden's layout,
   plants, color palette, lighting, and mood.
3. **Image generation** — `image_generator.py` passes that prompt to
   `huggingface_hub.InferenceClient(provider="auto")`, which routes the
   request to whichever Inference Provider currently serves the selected
   model (default: `black-forest-labs/FLUX.1-dev`). Transient failures
   (rate limits, cold starts) are retried automatically with exponential
   backoff.
4. **Result panel** — The generated image is displayed along with the AI
   design prompt (in a collapsible section) and a download button.

## Notes on security

- API keys are **never** hardcoded. They're read from environment variables
  (via `python-dotenv` locally) or `st.secrets` in deployed environments.
- `.env` is meant to stay local — don't commit it. Only `.env.example` (with
  placeholder values) is checked in.

## Customizing

- **Add/remove dropdown options** — edit the lists/dicts in `config.py`; the
  UI picks them up automatically.
- **Swap the image model** — add more entries to `HF_IMAGE_MODEL_OPTIONS` in
  `config.py`, as long as the model is available via an Inference Provider
  and supports text-to-image.
- **Tune the design-writing style** — edit the system prompt in
  `prompt_builder.py`.
