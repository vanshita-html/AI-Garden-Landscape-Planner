"""
config.py
---------
Central place for all dropdown options and shared constants used across the
AI Garden / Landscape Planner app. Keeping these here means the UI
(app.py) and the prompt builder (prompt_builder.py) always stay in sync.
"""

# ---------------------------------------------------------------------------
# Plot size options
# Key   -> label shown in the Streamlit dropdown
# Value -> descriptive phrase fed into the LLM prompt
# ---------------------------------------------------------------------------
PLOT_SIZES = {
    "Small (Balcony / Patio, under 100 sq ft)": (
        "a compact balcony or patio garden space, under 100 square feet"
    ),
    "Medium (Backyard, 100-500 sq ft)": (
        "a medium-sized backyard garden, roughly 100 to 500 square feet"
    ),
    "Large (Yard, 500-2000 sq ft)": (
        "a large residential yard, roughly 500 to 2000 square feet"
    ),
    "Estate (2000+ sq ft)": (
        "an expansive estate-sized landscape, over 2000 square feet"
    ),
}

# ---------------------------------------------------------------------------
# Garden / landscape style options
# ---------------------------------------------------------------------------
GARDEN_STYLES = [
    "Japanese Zen",
    "English Cottage",
    "Modern Minimalist",
    "Tropical Paradise",
    "Mediterranean",
    "Desert Xeriscape",
    "French Formal",
    "Woodland Naturalistic",
    "Cottage Farmhouse",
    "Coastal",
]

# ---------------------------------------------------------------------------
# Dominant plant type options
# ---------------------------------------------------------------------------
PLANT_TYPES = [
    "Flowering Perennials",
    "Ornamental Grasses",
    "Succulents & Cacti",
    "Shrubs & Hedges",
    "Fruit Trees",
    "Vegetable & Herb Beds",
    "Ferns & Shade Plants",
    "Roses",
    "Bamboo",
    "Mixed Native Plants",
]

# ---------------------------------------------------------------------------
# Season options
# ---------------------------------------------------------------------------
SEASONS = [
    "Spring",
    "Summer",
    "Autumn / Fall",
    "Winter",
]

# ---------------------------------------------------------------------------
# Color theme options
# ---------------------------------------------------------------------------
COLOR_THEMES = [
    "Pastel & Soft Hues",
    "Vibrant & Bold",
    "Monochrome Green",
    "Warm Sunset Tones",
    "Cool Blues & Purples",
    "White & Silver Moonlight Garden",
    "Earthy Neutrals",
    "Rainbow Multicolor",
]

# ---------------------------------------------------------------------------
# Model configuration
# ---------------------------------------------------------------------------
# Groq chat model used to turn form selections into a rich image-generation prompt.
GROQ_MODEL = "llama-3.3-70b-versatile"

# Hugging Face Inference Providers model used for the actual image generation.
# Users can swap this for any text-to-image model available on the Hub as
# long as it's supported by an Inference Provider.
DEFAULT_HF_IMAGE_MODEL = "black-forest-labs/FLUX.1-dev"

# A short list of alternative image models the user can pick from in the UI.
HF_IMAGE_MODEL_OPTIONS = [
    "black-forest-labs/FLUX.1-dev",
    "black-forest-labs/FLUX.1-schnell",
    "stabilityai/stable-diffusion-xl-base-1.0",
]
