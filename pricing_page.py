"""
Pricing page functionality - separated for clean code organization
"""
import streamlit as st
from login_styles import get_login_styles

def show_pricing_page():
    """Display pricing page with $20 pricing information"""
    
    # Apply login-specific styles for consistency
    st.markdown(get_login_styles(), unsafe_allow_html=True)
    
    # Center the pricing interface
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<h1 style='text-align: center; margin-bottom: 2rem;'>Fetchster Pricing</h1>", unsafe_allow_html=True)
        
        # Main pricing card
        st.markdown("""
        <div style='text-align: center; padding: 2rem; background: rgba(255,255,255,0.1); border-radius: 12px; border: 2px solid #ff4444; margin-bottom: 2rem;'>
            <h2 style='color: #ff4444; margin-bottom: 1rem;'>Professional Plan</h2>
            <div style='margin-bottom: 1.5rem;'>
                <span style='font-size: 3em; font-weight: bold; color: white;'>$20</span>
                <span style='color: rgba(255,255,255,0.8); font-size: 1.2em;'> annual</span>
            </div>
            <p style='color: rgba(255,255,255,0.9); margin-bottom: 1.5rem; font-size: 1.1em;'>
                <strong>Annual subscription with all features included</strong>
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Features included
        st.markdown("### ✅ What's Included:")
        
        features = [
            "Professional email harvesting tools",
            "Google Maps business lookup",
            "Google Search website scraping", 
            "CSV export functionality",
            "Search history access",
            "Analytics dashboard",
            "Priority customer support",
            "All features included"
        ]
        
        for feature in features:
            st.markdown(f"• {feature}")
        
        st.markdown("---")
        
        # How it works section
        st.markdown("### 🚀 How Fetchster Works:")
        
        steps = [
            "**Enter Keywords**: Search for business types like 'restaurant', 'dentist', 'lawyer'",
            "**Select Locations**: Choose specific cities, states, or countries to target",
            "**Run Search**: Our system finds businesses via Google Maps and extracts emails from websites",
            "**Download Results**: Get organized CSV files with business names, emails, and contact details"
        ]
        
        for i, step in enumerate(steps, 1):
            st.markdown(f"{i}. {step}")
        
        st.markdown("---")
        
        # Requirements section
        st.markdown("### 🔑 Requirements")
        st.markdown("""
        **Serper.dev API Account Required**
        - Sign up for a free account at [serper.dev](https://serper.dev)
        - Get your API key from the dashboard
        - Add your API key to Fetchster after registration
        - Serper.dev provides the Google search functionality
        """)
        
        st.markdown("---")
        
        # Payment section
        st.markdown("### 💳 Annual Subscription")
        st.markdown("Simple annual billing with all features included.")
        st.markdown("Professional email harvesting at an affordable price.")
        
        # CTA buttons
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🚀 Get Started Now", type="primary", use_container_width=True):
                st.session_state.show_pricing = False
                st.rerun()
        
        with col2:
            if st.button("← Back to Login", use_container_width=True):
                st.session_state.show_pricing = False
                st.rerun()
        
        st.markdown("---")
        
        # FAQ section
        st.markdown("### ❓ Frequently Asked Questions")
        
        with st.expander("What data sources does Fetchster use?"):
            st.markdown("""
            Fetchster searches Google Maps for business listings and then visits the associated 
            websites to extract publicly available email addresses. All data comes from legitimate, 
            publicly accessible sources.
            """)
        
        with st.expander("What are the search limits?"):
            st.markdown("""
            Your search capabilities depend on your annual subscription and your Serper.dev API 
            account limits. Fetchster provides all the tools, but search volume is managed 
            through your Serper.dev account.
            """)
        
        with st.expander("What formats can I export data in?"):
            st.markdown("""
            You can export your results as CSV files, which can be opened in Excel, Google Sheets, 
            or any spreadsheet application. We also provide analytics CSV exports with detailed metadata.
            """)
        
        with st.expander("Do I need my own API key?"):
            st.markdown("""
            Yes, you need a Serper.dev API account. Sign up at serper.dev for free and get your 
            API key. This is required because Fetchster uses Serper.dev to access Google search 
            and maps data. Your API usage and costs are managed through your Serper.dev account.
            """)
        
        with st.expander("Do you offer refunds?"):
            st.markdown("""
            Yes, we offer a 30-day money-back guarantee. If you're not satisfied with Fetchster, 
            contact hello@fetchster.io within 30 days for a full refund.
            """)
        
        with st.expander("Is my data secure?"):
            st.markdown("""
            Yes, all search history and exported data is stored securely and is only accessible 
            by your account. We follow industry-standard security practices to protect your information.
            """)
        
        # Contact footer
        st.markdown("---")
        st.markdown("""
        <div style='text-align: center; padding: 1rem; color: rgba(255,255,255,0.7);'>
            <p style='margin: 0;'>Questions? Contact us at <strong>hello@fetchster.io</strong></p>
        </div>
        """, unsafe_allow_html=True)