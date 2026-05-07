"""
Dashboard page CSS styles - separated for clean code organization
"""

def get_dashboard_styles():
    """Return all CSS styles specific to the dashboard and main functionality"""
    return """
    <style>
    /* DASHBOARD AND MAIN APP STYLES */

    /* Main container */
    .stApp {
        background-color: #000000;
        color: #ffffff;
    }

    /* Metric containers */
    div[data-testid="metric-container"] {
        background-color: #000000;
        border: 1px solid rgba(255, 255, 255, 0.25);
        border-radius: 8px;
        padding: 1rem;
    }

    /* Expander styling */
    .stExpander {
        background-color: transparent !important;
        border: 1px solid rgba(255, 255, 255, 0.25) !important;
        border-radius: 8px !important;
    }

    .stExpander > div {
        background-color: transparent !important;
        border: none !important;
    }

    .stExpander > div > div {
        background-color: transparent !important;
        border: none !important;
    }

    .stExpander details {
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

    /* Sidebar styling */
    .css-1d391kg {
        background-color: #000000;
        border-right: 1px solid rgba(255, 255, 255, 0.25);
    }

    /* Input fields in dashboard */
    [data-testid="stWidgetLabel"] p {
        color: rgba(255, 255, 255, 0.78) !important;
    }

    .stTextInput > div > div {
        background: transparent;
        border: 1px solid rgba(255, 255, 255, 0.25);
        border-radius: 8px;
        padding: 0.5rem 1rem;
        color: #ffffff;
        transition: all 0.3s ease;
    }

    .stTextInput > div > div > input {
        background: transparent !important;
        color: #ffffff !important;
        border: none !important;
    }

    /* Select boxes */
    .stSelectbox > div > div {
        background: transparent;
        border: 1px solid rgba(255, 255, 255, 0.25);
        border-radius: 8px;
        color: #ffffff;
    }

    .stSelectbox div,
    .stMultiSelect div {
        color: #ffffff;
    }

    /* Multiselect */
    .stMultiSelect > div > div {
        background: transparent;
        border: 1px solid rgba(255, 255, 255, 0.25);
        border-radius: 8px;
        color: #ffffff;
    }

    /* Data frames */
    .stDataFrame {
        border: 1px solid rgba(255, 255, 255, 0.25);
        border-radius: 8px;
    }

    /* Progress bars */
    .stProgress > div > div {
        background-color: #dc2626;
        border-radius: 10px;
    }

    /* File uploader */
    .stFileUploader > div {
        border: 1px solid rgba(255, 255, 255, 0.25);
        border-radius: 8px;
        background: transparent;
    }

    /* Columns and containers */
    .element-container {
        border-radius: 8px;
    }

    /* Success/Error/Warning messages */
    .stAlert {
        border-radius: 8px;
        border: 1px solid rgba(255, 255, 255, 0.25);
    }

    /* Dashboard buttons */
    .stButton > button:not([kind="primary"]) {
        background-color: transparent !important;
        border: 1px solid rgba(255, 255, 255, 0.25) !important;
        border-radius: 8px !important;
        color: #ffffff !important;
        transition: all 0.3s ease;
        padding: 0.5rem 1rem !important;
    }

    .stButton > button:not([kind="primary"]):hover {
        background-color: rgba(255, 255, 255, 0.1) !important;
        border-color: rgba(255, 255, 255, 0.5) !important;
    }

    /* Primary action buttons in dashboard */
    .stButton > button[kind="primary"] {
        background-color: #dc2626 !important;
        border: 1px solid rgba(255, 255, 255, 0.25) !important;
        border-radius: 8px !important;
        color: #ffffff !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
        padding: 0.5rem 1rem !important;
    }

    .stButton > button[kind="primary"]:hover {
        background-color: #b91c1c !important;
        border-color: #dc2626 !important;
    }

    /* Hide Streamlit elements */
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
