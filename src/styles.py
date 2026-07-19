"""Design-token CSS for the FII/DII dashboard — light + dark mode."""

APP_CSS = """
<style>
    :root {
        --bg-primary: #ffffff;
        --bg-card: #f8fafc;
        --border-card: #e2e8f0;
        --text-primary: #0f172a;
        --text-muted: #64748b;
        --text-caption: #94a3b8;
        --accent-green: #22C55E;
        --accent-red: #EF4444;
        --bg-info: #f0f4ff;
        --border-info: #dbeafe;
    }
    @media (prefers-color-scheme: dark) {
        .stApp { background: #0f172a; }
        :root {
            --bg-primary: #0f172a;
            --bg-card: #1e293b;
            --border-card: #334155;
            --text-muted: #94a3b8;
            --text-caption: #64748b;
            --bg-info: #1e3a5f;
            --border-info: #2563eb;
        }
        div[data-testid="column"] { background: #1e293b; border-color: #334155; }
        div[data-testid="metric-container"] > label { color: #94a3b8 !important; }
        .st-b7, .st-b6, .st-b5, .st-b4 { color: #e2e8f0 !important; }
    }
    .stApp { max-width: 1200px; margin: 0 auto; }
    div[data-testid="column"] {
        background: var(--bg-card);
        border: 1px solid var(--border-card);
        border-radius: 12px;
        padding: 16px 14px;
    }
    div[data-testid="metric-container"] {
        background: transparent !important;
        padding: 0 !important;
    }
    div[data-testid="metric-container"] > label {
        font-size: 0.75rem !important;
        color: var(--text-muted) !important;
        font-weight: 500 !important;
    }
    div[data-testid="metric-container"] > div {
        font-size: 1.35rem !important;
        font-weight: 600 !important;
    }
    div[data-testid="stInfo"] {
        background: var(--bg-info) !important;
        border: 1px solid var(--border-info) !important;
        border-radius: 10px !important;
    }
    .ml { display: flex; align-items: center; gap: 6px; margin-bottom: 4px; font-size: 0.78rem; font-weight: 500; }
    .mc { font-size: 0.7rem; color: var(--text-caption); margin-top: 2px; }
    .hdr { display: flex; align-items: center; gap: 8px; font-weight: 600; font-size: 1.05rem; margin: 24px 0 4px; }
    .empty { text-align: center; padding: 32px 20px; border: 1px dashed var(--border-card); border-radius: 12px; color: var(--text-caption); font-size: 0.85rem; }
    hr { margin: 4px 0 16px; }
    .stButton button, .stDownloadButton button { border-radius: 8px; font-size: 0.8rem; width: 100%; }
    .stButton button:hover { opacity: 0.85; transition: opacity 0.15s; }
    section[data-testid="stSidebar"] .stMarkdown { font-size: 0.85rem; }
    .error-placeholder {
        text-align: center; padding: 24px 20px;
        border: 1px solid #fecaca; border-radius: 12px;
        background: #fef2f2; color: #dc2626; font-size: 0.85rem;
    }
    @media (prefers-color-scheme: dark) {
        .error-placeholder {
            background: #451a1a; border-color: #7f1d1d; color: #fca5a5;
        }
    }
    @media (prefers-reduced-motion: reduce) {
        .stButton button:hover { transition: none; }
    }
    .footer {
        margin-top: 32px; padding: 12px 0;
        border-top: 1px solid var(--border-card);
        font-size: 0.7rem; color: var(--text-caption);
        display: flex; justify-content: space-between; flex-wrap: wrap; gap: 8px;
    }
    .footer a { color: var(--text-caption); }
    .footer a:hover { color: var(--text-primary); }
</style>
"""


def render_css():
    """Render the full CSS block. Call once at app startup."""
    import streamlit as st
    st.markdown(APP_CSS, unsafe_allow_html=True)
