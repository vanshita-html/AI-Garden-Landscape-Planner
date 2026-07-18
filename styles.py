"""
styles.py
---------
Custom visual design for the Garden & Landscape Planner: a botanical,
editorial palette (pale eucalyptus paper, deep moss ink, sage, warm ochre
clay) built specifically for this app rather than a generic AI-app default.

Everything here is plain CSS/SVG injected via st.markdown(unsafe_allow_html=
True) — no external assets required, so it works the same locally and on
Streamlit Cloud.
"""

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,500;0,9..144,600;1,9..144,500&family=Inter:wght@400;500;600&display=swap');

:root {
  --gp-bg: #F1F4EC;
  --gp-surface: #FFFFFF;
  --gp-ink: #1F2E1B;
  --gp-ink-soft: #58694F;
  --gp-moss: #3F5B3E;
  --gp-moss-dark: #2A4029;
  --gp-sage: #7E9A72;
  --gp-clay: #BD8A46;
  --gp-line: #DDE4D2;
}

html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
  background: var(--gp-bg) !important;
}

* { font-family: 'Inter', sans-serif; }

[data-testid="stHeader"] { background: transparent; }
.block-container { padding-top: 2.6rem; padding-bottom: 3rem; max-width: 760px; }

/* ---------- Header ---------- */
.gp-header { display: flex; align-items: center; gap: 0.9rem; }
.gp-title {
  font-family: 'Fraunces', serif;
  font-weight: 600;
  font-size: 2.3rem;
  color: var(--gp-moss-dark);
  letter-spacing: -0.01em;
  line-height: 1.05;
  margin: 0;
}
.gp-tagline {
  color: var(--gp-ink-soft);
  font-size: 1.02rem;
  line-height: 1.5;
  max-width: 48ch;
  margin: 0.9rem 0 0;
}

.gp-divider {
  border: none;
  height: 1px;
  background: var(--gp-line);
  margin: 1.9rem 0 2rem;
  position: relative;
}
.gp-divider::after {
  content: '\\2766';
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  background: var(--gp-bg);
  padding: 0 0.65rem;
  color: var(--gp-sage);
  font-size: 1rem;
}

/* ---------- Form card ---------- */
[data-testid="stForm"] {
  background: var(--gp-surface);
  border: 1px solid var(--gp-line);
  border-radius: 20px;
  padding: 2.1rem 2.1rem 1.6rem;
  box-shadow: 0 10px 34px -16px rgba(42, 64, 41, 0.22);
}

[data-testid="stForm"] label p {
  font-family: 'Inter', sans-serif;
  font-size: 0.72rem;
  font-weight: 600;
  letter-spacing: 0.09em;
  text-transform: uppercase;
  color: var(--gp-sage);
}

[data-testid="stForm"] [data-baseweb="select"] > div {
  background: var(--gp-bg);
  border-radius: 10px;
  border: 1px solid var(--gp-line);
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
}
[data-testid="stForm"] [data-baseweb="select"] > div:hover {
  border-color: var(--gp-sage);
}
[data-testid="stForm"] [data-baseweb="select"] > div:focus-within {
  border-color: var(--gp-moss);
  box-shadow: 0 0 0 3px rgba(63, 91, 62, 0.16);
}

/* ---------- Expander (design concept) ---------- */
[data-testid="stExpander"] {
  border: 1px solid var(--gp-line);
  border-radius: 16px;
  background: var(--gp-surface);
  overflow: hidden;
  box-shadow: 0 6px 20px -14px rgba(42, 64, 41, 0.18);
}
[data-testid="stExpander"] summary {
  font-family: 'Inter', sans-serif;
  font-weight: 600;
  color: var(--gp-moss-dark);
}
[data-testid="stExpander"] p {
  color: var(--gp-ink-soft);
  line-height: 1.6;
}

/* ---------- Buttons ---------- */
.stButton > button,
.stFormSubmitButton > button,
.stDownloadButton > button {
  background: var(--gp-moss-dark);
  color: #F6F8F1 !important;
  border: none;
  border-radius: 12px;
  padding: 0.75rem 1.4rem;
  font-weight: 600;
  letter-spacing: 0.01em;
  transition: transform 0.15s ease, box-shadow 0.15s ease, background 0.15s ease;
  box-shadow: 0 8px 18px -9px rgba(42, 64, 41, 0.55);
}
.stButton > button:hover,
.stFormSubmitButton > button:hover,
.stDownloadButton > button:hover {
  background: var(--gp-moss);
  transform: translateY(-1px);
  box-shadow: 0 12px 24px -9px rgba(42, 64, 41, 0.6);
  color: #F6F8F1 !important;
}
.stButton > button:focus-visible,
.stFormSubmitButton > button:focus-visible,
.stDownloadButton > button:focus-visible {
  outline: 3px solid var(--gp-clay);
  outline-offset: 2px;
}

/* ---------- Result panel ---------- */
[data-testid="stVerticalBlockBorderWrapper"] {
  background: var(--gp-surface);
  border: 1px solid var(--gp-line);
  border-radius: 20px;
  box-shadow: 0 10px 34px -16px rgba(42, 64, 41, 0.2);
}
.gp-result-title {
  font-family: 'Fraunces', serif;
  font-weight: 500;
  font-size: 1.5rem;
  color: var(--gp-moss-dark);
  margin: 0.1rem 0 0.9rem;
}
[data-testid="stImage"] img {
  border-radius: 12px;
}

@media (prefers-reduced-motion: no-preference) {
  .gp-fade-in { animation: gpFadeIn 0.55s ease both; }
}
@keyframes gpFadeIn {
  from { opacity: 0; transform: translateY(6px); }
  to { opacity: 1; transform: none; }
}

/* ---------- Footer ---------- */
.gp-footer {
  text-align: center;
  color: var(--gp-ink-soft);
  font-size: 0.85rem;
  margin-top: 2.4rem;
}
</style>
"""

# A small hand-drawn-style line-art sprig: one stem, two curling leaves.
# Used as the app's signature visual element instead of a stock emoji.
SPRIG_SVG = """
<svg width="46" height="46" viewBox="0 0 44 44" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
  <path d="M22 40V12" stroke="#2A4029" stroke-width="2" stroke-linecap="round"/>
  <path d="M22 27C22 27 13 25 11 15C21 15 22 27 22 27Z" stroke="#7E9A72" stroke-width="2" stroke-linejoin="round"/>
  <path d="M22 19C22 19 31 17 33 8C23 8 22 19 22 19Z" stroke="#7E9A72" stroke-width="2" stroke-linejoin="round"/>
  <circle cx="22" cy="10" r="2.4" fill="#BD8A46"/>
</svg>
"""
