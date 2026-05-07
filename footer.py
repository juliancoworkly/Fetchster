import streamlit as st
from auth import is_authenticated

def show_clean_footer():
    """Display clean footer with functional legal links and copyright"""
    st.markdown("---")
    
    # Create perfectly centered links closer together with equal spacing from center
    col1, col2, col3, col4, col5 = st.columns([5, 1, 0.2, 1, 5])
    
    with col2:
        if st.button("Terms", key="footer_terms_clean"):
            st.session_state.show_terms = True
            st.rerun()
    
    with col4:
        if st.button("Privacy", key="footer_privacy_clean"):
            st.session_state.show_privacy = True
            st.rerun()
    
    st.markdown(
        "<div style='text-align: center; color: #666; margin-top: 10px; font-size: 0.8em;'>"
        "© 2025 Fetchster. All rights reserved."
        "</div>", 
        unsafe_allow_html=True
    )