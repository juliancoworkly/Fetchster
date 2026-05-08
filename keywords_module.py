"""
Keywords management module - separated for clean code organization
"""
import streamlit as st
from auth import save_user_keywords, get_user_keywords
from search_styles import get_search_styles

def show_keywords_interface():
    """Display simplified keywords interface"""
    
    # Apply search-specific styles
    st.markdown(get_search_styles(), unsafe_allow_html=True)
    
    st.markdown("### Keywords")
    st.markdown("What type of businesses are you looking for?")
    
    # Get saved keywords
    saved_keywords = get_user_keywords()
    
    # Initialize session state for keywords
    if 'search_keywords_list' not in st.session_state:
        st.session_state.search_keywords_list = []
    
    # Simple keyword input with form to handle Enter key
    with st.form("keyword_form", clear_on_submit=True):
        col1, col2 = st.columns([3, 1])
        
        with col1:
            new_keyword = st.text_input(
                "Enter keyword",
                placeholder="e.g., restaurant, dentist, plumber",
                help="Enter the type of business you want to find",
                label_visibility="collapsed"
            )
        
        with col2:
            add_clicked = st.form_submit_button("Add", type="primary", use_container_width=True)
        
        # Handle form submission (works with both button click and Enter key)
        if add_clicked and new_keyword and new_keyword not in st.session_state.search_keywords_list:
            st.session_state.search_keywords_list.append(new_keyword)
            # Auto-save to user's collection
            current_saved = get_user_keywords()
            if new_keyword not in current_saved:
                save_user_keywords(current_saved + [new_keyword])
            st.rerun()
    
    # Display current search keywords with simple removal
    if st.session_state.search_keywords_list:
        st.markdown("**Selected keywords:**")
        for i, keyword in enumerate(st.session_state.search_keywords_list):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"• {keyword}")
            with col2:
                if st.button("✕", key=f"remove_keyword_{i}", help=f"Remove {keyword}"):
                    st.session_state.search_keywords_list.remove(keyword)
                    st.rerun()
        
        # Clear all button
        if len(st.session_state.search_keywords_list) > 1:
            if st.button("Clear All", type="secondary"):
                st.session_state.search_keywords_list = []
                st.rerun()
    
    # Quick access to saved keywords
    if saved_keywords:
        st.markdown("**Previous keywords** (click to add):")
        
        # Show popular keywords in a simple grid
        cols = st.columns(3)
        for i, keyword in enumerate(saved_keywords[:9]):  # Show max 9 keywords
            with cols[i % 3]:
                if st.button(keyword, key=f"saved_{keyword}", use_container_width=True):
                    if keyword not in st.session_state.search_keywords_list:
                        st.session_state.search_keywords_list.append(keyword)
                        st.rerun()
        
        # Show more options in expander
        if len(saved_keywords) > 9:
            with st.expander(f"Show all {len(saved_keywords)} saved keywords"):
                for keyword in saved_keywords[9:]:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        if st.button(keyword, key=f"saved_all_{keyword}", use_container_width=True):
                            if keyword not in st.session_state.search_keywords_list:
                                st.session_state.search_keywords_list.append(keyword)
                                st.rerun()
                    with col2:
                        if st.button("✕", key=f"delete_{keyword}", help=f"Delete {keyword}"):
                            updated_keywords = [k for k in saved_keywords if k != keyword]
                            save_user_keywords(updated_keywords)
                            st.rerun()
    
    # Return the search keywords list as a comma-separated string
    return ", ".join(st.session_state.search_keywords_list) if st.session_state.search_keywords_list else ""