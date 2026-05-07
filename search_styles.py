"""
Search interface CSS styles - separated for clean code organization
"""

def get_search_styles():
    """Return all CSS styles specific to the search interface"""
    return """
    <style>
    /* SEARCH INTERFACE STYLES */

    /* Main container */
    .stApp {
        background-color: #000000;
        color: #ffffff;
    }

    /* Remove container backgrounds - make transparent */
    .stContainer {
        background: transparent !important;
        border: none !important;
    }

    .element-container {
        background: transparent !important;
        border: none !important;
    }

    /* Input fields styling */
    [data-testid="stWidgetLabel"] p {
        color: rgba(255, 255, 255, 0.78) !important;
    }

    .stTextInput > div {
        background: transparent !important;
        border: none !important;
    }

    .stTextInput > div > div {
        background: transparent !important;
        border: 1px solid rgba(255, 255, 255, 0.25) !important;
        border-radius: 8px !important;
        padding: 0.5rem 1rem !important;
        color: #ffffff !important;
        transition: all 0.3s ease !important;
    }

    .stTextInput > div > div > input {
        background: transparent !important;
        color: #ffffff !important;
        border: none !important;
    }

    /* Focus states */
    .stTextInput > div > div:focus-within {
        border-color: rgba(255, 255, 255, 0.5) !important;
    }

    /* Select boxes */
    .stSelectbox > div > div {
        background: transparent !important;
        border: 1px solid rgba(255, 255, 255, 0.25) !important;
        border-radius: 8px !important;
        color: #ffffff !important;
    }

    .stSelectbox div,
    .stMultiSelect div {
        color: #ffffff !important;
    }

    /* Multiselect */
    .stMultiSelect > div > div {
        background: transparent !important;
        border: 1px solid rgba(255, 255, 255, 0.25) !important;
        border-radius: 8px !important;
    }

    .stMultiSelect div[data-baseweb="tag"] {
        background-color: #dc2626;
        border-radius: 6px;
        color: #ffffff;
    }

    /* Buttons */
    .stButton > button {
        background-color: transparent !important;
        border: 1px solid rgba(255, 255, 255, 0.25) !important;
        border-radius: 8px !important;
        color: #ffffff !important;
        transition: all 0.3s ease !important;
        padding: 0.5rem 1rem !important;
    }

    .stButton > button:hover {
        background-color: rgba(255, 255, 255, 0.1) !important;
        border-color: rgba(255, 255, 255, 0.5) !important;
    }

    /* Primary action buttons */
    .stButton > button[kind="primary"] {
        background-color: #dc2626 !important;
        border: 1px solid rgba(255, 255, 255, 0.25) !important;
        border-radius: 8px !important;
        color: #ffffff !important;
        font-weight: 500 !important;
    }

    .stButton > button[kind="primary"]:hover {
        background-color: #b91c1c !important;
        border-color: #dc2626 !important;
    }

    /* Expanders */
    .stExpander {
        background-color: transparent !important;
        border: 1px solid rgba(255, 255, 255, 0.25) !important;
        border-radius: 8px !important;
    }

    .stExpander > div {
        background-color: transparent !important;
        border: none !important;
    }

    .stExpander summary {
        background-color: transparent !important;
        border: none !important;
        color: #ffffff !important;
        padding: 1rem !important;
        font-weight: 500 !important;
        border-radius: 8px !important;
    }

    .stExpander summary:hover {
        background-color: rgba(255, 255, 255, 0.05) !important;
    }

    /* Progress bars */
    .stProgress > div > div {
        background-color: #dc2626;
        border-radius: 10px;
    }

    /* Metrics */
    div[data-testid="metric-container"] {
        background-color: transparent !important;
        border: 1px solid rgba(255, 255, 255, 0.25) !important;
        border-radius: 8px !important;
        padding: 1rem !important;
    }

    /* Alerts */
    .stAlert {
        border-radius: 8px !important;
        border: 1px solid rgba(255, 255, 255, 0.25) !important;
    }

    /* Data frames */
    .stDataFrame {
        border: 1px solid rgba(255, 255, 255, 0.25) !important;
        border-radius: 8px !important;
    }

    /* Hide Streamlit branding */
    .stDeployButton {
        display: none;
    }

    footer {
        visibility: hidden;
    }

    .stApp > header {
        display: none;
    }

    [data-testid="stHeader"] {
        display: none;
    }
    </style>
    """
