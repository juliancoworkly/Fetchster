"""
Progress management module - separated for clean code organization
"""
import streamlit as st
import json
import os
from datetime import datetime
from search_styles import get_search_styles

def show_progress_interface():
    """Display progress management interface"""
    
    # Apply search-specific styles
    st.markdown(get_search_styles(), unsafe_allow_html=True)
    
    st.markdown("### Search Progress")
    st.markdown("Track and manage your search progress")
    
    # Progress saving and loading
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Save Progress", type="primary", use_container_width=True):
            save_search_progress()
            st.success("Progress saved")
    
    with col2:
        if st.button("Load Progress", use_container_width=True):
            load_search_progress()
            st.success("Progress loaded")
    
    with col3:
        if st.button("Clear Progress", use_container_width=True):
            clear_saved_progress()
            st.success("Progress cleared")
    
    # Current search status
    if hasattr(st.session_state, 'search_results'):
        results = st.session_state.search_results
        if results:
            st.markdown("**Current Search Results:**")
            st.metric("Total Results", len(results))
            
            emails_found = sum(1 for result in results if result.get('emails'))
            st.metric("Businesses with Emails", emails_found)
    
    # Search history
    if hasattr(st.session_state, 'search_history'):
        history = st.session_state.search_history
        if history:
            st.markdown("**Recent Searches:**")
            for i, search in enumerate(history[-5:]):  # Show last 5 searches
                with st.expander(f"Search {i+1}: {search.get('keyword', 'Unknown')}"):
                    st.write(f"Location: {search.get('location', 'N/A')}")
                    st.write(f"Results: {search.get('results_count', 0)}")
                    st.write(f"Date: {search.get('timestamp', 'N/A')}")

def save_search_progress():
    """Save current search progress to file"""
    progress_data = {
        'keyword': getattr(st.session_state, 'selected_keyword', ''),
        'locations': getattr(st.session_state, 'selected_locations', []),
        'search_options': getattr(st.session_state, 'search_options', {}),
        'results': getattr(st.session_state, 'search_results', []),
        'timestamp': datetime.now().isoformat()
    }
    
    try:
        with open('search_progress.json', 'w') as f:
            json.dump(progress_data, f, indent=2)
        return True
    except Exception as e:
        st.error(f"Failed to save progress: {str(e)}")
        return False

def load_search_progress():
    """Load previous search progress from file"""
    try:
        if os.path.exists('search_progress.json'):
            with open('search_progress.json', 'r') as f:
                progress_data = json.load(f)
            
            st.session_state.selected_keyword = progress_data.get('keyword', '')
            st.session_state.selected_locations = progress_data.get('locations', [])
            st.session_state.search_options = progress_data.get('search_options', {})
            st.session_state.search_results = progress_data.get('results', [])
            
            return True
    except Exception as e:
        st.error(f"Failed to load progress: {str(e)}")
        return False

def clear_saved_progress():
    """Clear saved progress file"""
    try:
        if os.path.exists('search_progress.json'):
            os.remove('search_progress.json')
        
        # Clear session state
        for key in ['selected_keyword', 'selected_locations', 'search_options', 'search_results']:
            if key in st.session_state:
                del st.session_state[key]
        
        return True
    except Exception as e:
        st.error(f"Failed to clear progress: {str(e)}")
        return False