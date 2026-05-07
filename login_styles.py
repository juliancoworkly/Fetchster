"""
Login page CSS styles - separated for clean code organization
"""


def get_login_styles():
    """Return all CSS styles specific to the login page."""
    return """
    <style>
    .stApp {
        background: #050505;
        color: #ffffff;
    }

    .block-container {
        max-width: 1180px;
        padding-top: 2.25rem;
        padding-bottom: 2rem;
    }

    [data-testid="stHeader"],
    .stDeployButton,
    footer {
        display: none;
        visibility: hidden;
    }

    .auth-hero {
        padding-top: 1.25rem;
    }

    .auth-kicker {
        color: #ff4d4d;
        font-weight: 700;
        letter-spacing: 0;
        margin: 0 0 0.75rem 0;
        text-transform: uppercase;
    }

    .auth-hero h1 {
        font-size: 3rem;
        line-height: 1.05;
        letter-spacing: 0;
        margin: 0 0 1rem 0;
        max-width: 560px;
    }

    .auth-lede {
        color: rgba(255, 255, 255, 0.72);
        font-size: 1.05rem;
        line-height: 1.6;
        margin: 0 0 1.5rem 0;
        max-width: 560px;
    }

    .auth-facts {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 0.75rem;
        margin: 0 0 1.25rem 0;
        max-width: 560px;
    }

    .auth-facts div {
        border: 1px solid rgba(255, 255, 255, 0.14);
        border-radius: 8px;
        background: #151515;
        padding: 0.9rem;
    }

    .auth-facts strong,
    .auth-facts span {
        display: block;
    }

    .auth-facts strong {
        color: #ffffff;
        margin-bottom: 0.25rem;
    }

    .auth-facts span,
    .auth-benefits {
        color: rgba(255, 255, 255, 0.68);
    }

    .auth-benefits {
        line-height: 1.8;
        margin: 0;
        padding-left: 1.1rem;
    }

    .auth-panel-title {
        color: rgba(255, 255, 255, 0.74);
        font-weight: 700;
        margin: 0.25rem 0 0.9rem 0;
        text-transform: uppercase;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        margin-bottom: 1.25rem;
    }

    .stTabs [data-baseweb="tab"] {
        background: #141414;
        border: 1px solid rgba(255, 255, 255, 0.14);
        border-radius: 8px;
        color: #ffffff;
        font-weight: 600;
        padding: 0.75rem 1rem;
    }

    .stTabs [aria-selected="true"] {
        background: #dc2626;
        border-color: #ef4444;
    }

    .stTabs [data-baseweb="tab-border"],
    .stTabs [data-baseweb="tab-highlight"] {
        display: none;
    }

    .stForm {
        border: 1px solid rgba(255, 255, 255, 0.14) !important;
        border-radius: 8px !important;
        background: #101010 !important;
        padding: 1rem !important;
    }

    .stTextInput > div > div {
        background: #090909 !important;
        border: 1px solid rgba(255, 255, 255, 0.18) !important;
        border-radius: 8px !important;
        color: #ffffff !important;
        min-height: 2.75rem;
    }

    div[data-testid="stTextInput"] div[data-testid="stTextInputRootElement"],
    div[data-testid="stTextInput"] [data-baseweb="input"],
    div[data-testid="stTextInput"] [data-baseweb="input"] > div,
    div[data-testid="stTextInput"] [data-baseweb="input"] > div:last-child {
        background: #090909 !important;
        background-color: #090909 !important;
    }

    .stTextInput > div > div:focus-within {
        border-color: #ef4444 !important;
        box-shadow: 0 0 0 1px rgba(239, 68, 68, 0.28) !important;
    }

    .stTextInput input {
        color: #ffffff !important;
    }

    .stTextInput button,
    .stTextInput button[aria-label="Show password text"] {
        background: transparent !important;
        background-color: transparent !important;
        border: none !important;
        color: rgba(255, 255, 255, 0.7) !important;
        min-height: 1.75rem !important;
        padding: 0.25rem !important;
    }

    .stTextInput button:hover,
    .stTextInput button[aria-label="Show password text"]:hover {
        background: transparent !important;
        background-color: transparent !important;
        color: #ffffff !important;
    }

    [data-testid="stWidgetLabel"] p {
        color: rgba(255, 255, 255, 0.76) !important;
    }

    .stCheckbox label {
        color: rgba(255, 255, 255, 0.78) !important;
    }

    .stButton > button,
    div[data-testid="stFormSubmitButton"] button {
        border-radius: 8px !important;
        min-height: 2.75rem !important;
        font-weight: 600 !important;
    }

    div[data-testid="stFormSubmitButton"] button {
        background: #dc2626 !important;
        border: 1px solid #ef4444 !important;
        color: #ffffff !important;
    }

    div[data-testid="stFormSubmitButton"] button:hover {
        background: #b91c1c !important;
        border-color: #f87171 !important;
    }

    .stButton > button {
        background: transparent !important;
        border: 1px solid rgba(255, 255, 255, 0.16) !important;
        color: #ffffff !important;
    }

    .stButton > button:hover {
        border-color: rgba(255, 255, 255, 0.34) !important;
        color: #ff6666 !important;
    }

    .stAlert {
        border-radius: 8px !important;
    }

    .auth-footer {
        border-top: 1px solid rgba(255, 255, 255, 0.12);
        margin-top: 2rem;
        padding-top: 1rem;
    }

    @media (max-width: 820px) {
        .block-container {
            padding-top: 1.25rem;
        }

        .auth-hero h1 {
            font-size: 2.25rem;
        }

        .auth-facts {
            grid-template-columns: 1fr;
        }
    }
    </style>
    """
