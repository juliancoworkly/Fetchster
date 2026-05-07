"""
Login page CSS styles - separated for clean code organization
"""

def get_login_styles():
    """Return all CSS styles specific to the login page"""
    return """
    <style>
    /* LOGIN PAGE STYLES */
    
    /* Main container and background */
    .stApp {
        background-color: #000000;
        color: #ffffff;
    }
    
    /* Tab styling for Sign In / Create Account */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0px;
        background-color: transparent;
        border-bottom: none;
        justify-content: center;
        margin-bottom: 2rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        color: #ffffff;
        border: 1px solid rgba(255, 255, 255, 0.25);
        border-radius: 20px;
        padding: 12px 24px;
        margin: 0 5px;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #dc2626;
        color: #ffffff;
        border-color: rgba(255, 255, 255, 0.5);
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: rgba(255, 255, 255, 0.1);
        border-color: rgba(255, 255, 255, 0.5);
    }
    
    /* Remove tab underlines */
    .stTabs [data-baseweb="tab-border"] {
        display: none;
    }
    
    .stTabs [data-baseweb="tab-highlight"] {
        display: none;
    }
    
    /* Input field styling - transparent containers */
    .stTextInput > div {
        background: transparent !important;
        border: none !important;
    }
    
    .stTextInput > div > div {
        background: transparent !important;
        border: 1px solid rgba(255, 255, 255, 0.25) !important;
        border-radius: 20px !important;
        padding: 0.5rem 1rem !important;
        color: #ffffff !important;
        transition: all 0.3s ease !important;
        position: relative !important;
    }
    
    .stTextInput > div > div > input {
        background: transparent !important;
        background-color: transparent !important;
        border: none !important;
        color: #ffffff !important;
        width: 100% !important;
        box-sizing: border-box !important;
    }
    
    /* Focus states */
    .stTextInput > div > div:focus-within {
        border-color: rgba(255, 255, 255, 0.5) !important;
        background-color: transparent !important;
    }
    
    /* Remove all outer container borders */
    .stForm {
        background: transparent !important;
        border: none !important;
    }
    
    .element-container {
        background: transparent !important;
        border: none !important;
    }
    
    /* Password visibility button styling - centered in input */
    button[kind="secondary"] {
        background: transparent !important;
        border: none !important;
        color: rgba(255, 255, 255, 0.7) !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        visibility: visible !important;
        opacity: 1 !important;
        width: auto !important;
        height: auto !important;
        padding: 4px !important;
        margin: 0 4px !important;
        position: absolute !important;
        right: 8px !important;
        top: 50% !important;
        transform: translateY(-50%) !important;
        z-index: 1000 !important;
    }
    
    button[kind="secondary"]:hover {
        color: rgba(255, 255, 255, 1) !important;
    }
    
    /* Text input button visibility fixes */
    .stTextInput button,
    div[data-testid*="textInput"] button,
    div[data-testid*="password"] button {
        background: transparent !important;
        border: none !important;
        color: rgba(255, 255, 255, 0.7) !important;
        display: inline-block !important;
        visibility: visible !important;
        opacity: 1 !important;
        width: auto !important;
        height: auto !important;
        min-width: 24px !important;
        min-height: 24px !important;
        overflow: visible !important;
    }
    
    /* Container visibility */
    .stTextInput > div,
    .stTextInput > div > div {
        overflow: visible !important;
        position: relative !important;
    }
    
    /* Submit button - identical to Sign In/Create Account with red background */
    button[kind="primary"],
    .stButton > button[kind="primary"],
    button[data-testid="baseButton-primary"],
    form button[kind="primary"],
    .stForm button[kind="primary"],
    div[data-testid="stForm"] button[kind="primary"],
    div[data-testid="stForm"] .stButton button[kind="primary"],
    form[data-testid="form"] button[kind="primary"] {
        background-color: #dc2626 !important;
        background: #dc2626 !important;
        border: 1px solid rgba(255, 255, 255, 0.25) !important;
        border-radius: 20px !important;
        color: #ffffff !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
        padding: 0.5rem 1rem !important;
        height: 3rem !important;
        min-height: 3rem !important;
        font-size: 1rem !important;
        width: auto !important;
    }
    
    /* Submit button hover - slight darkening */
    button[kind="primary"]:hover,
    .stButton > button[kind="primary"]:hover,
    button[data-testid="baseButton-primary"]:hover,
    form button[kind="primary"]:hover,
    .stForm button[kind="primary"]:hover,
    div[data-testid="stForm"] button[kind="primary"]:hover,
    div[data-testid="stForm"] .stButton button[kind="primary"]:hover,
    form[data-testid="form"] button[kind="primary"]:hover {
        background-color: #b91c1c !important;
        background: #b91c1c !important;
        border-color: rgba(255, 255, 255, 0.25) !important;
    }
    
    /* Center Submit button */
    div[data-testid="stForm"] .stButton {
        display: flex !important;
        justify-content: center !important;
        width: 100% !important;
    }
    
    /* Text link buttons (non-primary) */
    .stButton > button:not([kind="primary"]) {
        background-color: transparent !important;
        border: none !important;
        border-radius: 0px !important;
        color: #ffffff !important;
        transition: all 0.3s ease;
        padding: 8px 16px !important;
        text-decoration: none !important;
    }
    
    .stButton > button:not([kind="primary"]):hover {
        background-color: transparent !important;
        border: none !important;
        color: #dc2626 !important;
        text-decoration: none !important;
    }
    
    /* Forgot password button styling */
    button[kind="secondary"] {
        background: transparent !important;
        border: none !important;
        color: #ffffff !important;
        font-size: 1em !important;
        transition: color 0.3s ease !important;
        padding: 8px 0 !important;
        text-align: center !important;
        width: 100% !important;
        box-shadow: none !important;
        outline: none !important;
    }
    
    button[kind="secondary"]:hover {
        color: #dc2626 !important;
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }
    
    button[kind="secondary"]:focus {
        border: none !important;
        box-shadow: none !important;
        outline: none !important;
    }
    
    /* General element styling */
    .element-container, .stMarkdown, .stDataFrame {
        border-radius: 20px;
    }
    
    .stAlert {
        border-radius: 20px;
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