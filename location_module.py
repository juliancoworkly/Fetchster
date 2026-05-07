"""
Location management module - separated for clean code organization
"""

import streamlit as st
from location_ui_components import (
    LocationKeyManager, 
    LocationSearchPreview, 
    DirectCitySearch, 
    HierarchicalLocationBrowser,
    BulkLocationInput
)
from location_utils import LocationOptimizer

def show_location_interface():
    """Display location selection interface with smart optimization"""
    
    # Initialize components
    key_manager = LocationKeyManager()
    key_manager.reset_keys()
    
    optimizer = LocationOptimizer()
    search_preview = LocationSearchPreview(optimizer)
    direct_search = DirectCitySearch(key_manager)
    hierarchical_browser = HierarchicalLocationBrowser(key_manager)
    bulk_input = BulkLocationInput(key_manager)
    
    # Initialize session state for location selections with persistence
    if 'selected_locations_persistent' not in st.session_state:
        st.session_state.selected_locations_persistent = []
    
    # Start with previously selected locations
    all_locations = st.session_state.selected_locations_persistent.copy()
    
    # Track new selections from each tab separately to avoid duplication
    new_locations = []
    
    # Create tabs for different search methods
    tab1, tab2, tab3 = st.tabs(["🏙️ Direct City Search", "🗺️ Browse by Country/Region", "📋 Bulk Input"])
    
    with tab1:
        locations_from_direct = direct_search.show_direct_search()
        new_locations.extend(locations_from_direct)
    
    with tab2:
        locations_from_hierarchical = hierarchical_browser.show_hierarchical_browser()
        new_locations.extend(locations_from_hierarchical)
    
    with tab3:
        locations_from_bulk = bulk_input.show_bulk_input()
        new_locations.extend(locations_from_bulk)
    
    # Only add new locations that aren't already in the persistent list
    for location in new_locations:
        if location not in all_locations:
            all_locations.append(location)
    
    # Manual location input with Enter key support and auto-clearing
    with st.form(key="manual_location_form", clear_on_submit=True):
        manual_location = st.text_input(
            "Add custom location:",
            placeholder="Enter location and press Enter...",
            help="Type any location not found in the lists above"
        )
        
        # Hidden submit button - Enter key will trigger this
        submitted = st.form_submit_button("Add Location", type="primary")
        
        if submitted and manual_location.strip():
            # Only add manual location if not already in the list
            clean_location = manual_location.strip()
            if clean_location not in all_locations:
                all_locations.append(clean_location)
                # Add to session state for persistence
                if 'manual_locations_added' not in st.session_state:
                    st.session_state.manual_locations_added = []
                st.session_state.manual_locations_added.append(clean_location)
                st.success(f"Added location: {clean_location}")
                st.rerun()  # This will clear the form and refresh
    
    # Add previously entered manual locations to the list
    if 'manual_locations_added' in st.session_state:
        for loc in st.session_state.manual_locations_added:
            if loc not in all_locations:
                all_locations.append(loc)
    
    # Show search preview and optimization
    if all_locations:
        search_preview.show_search_preview(all_locations)
        
        # Show optimization suggestions
        suggestions = optimizer.suggest_location_improvements(all_locations)
        if suggestions:
            st.info("💡 Optimization Suggestions:")
            for suggestion in suggestions:
                st.markdown(f"• {suggestion['message']} (Save {suggestion['savings']} credits)")
        
        # Display selected locations with removal option
        st.markdown("#### Selected Locations:")
        optimized_locations, _ = optimizer.optimize_locations(all_locations)
        
        # Create columns for location display and removal
        for i, location in enumerate(optimized_locations):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"{i+1}. {location}")
            with col2:
                if st.button("Remove", key=f"remove_loc_{i}", help=f"Remove {location}"):
                    # Remove from all session state location lists
                    if location in st.session_state.selected_locations_persistent:
                        st.session_state.selected_locations_persistent.remove(location)
                    if 'manual_locations_added' in st.session_state and location in st.session_state.manual_locations_added:
                        st.session_state.manual_locations_added.remove(location)
                    
                    # Also remove from any other location storage that might exist
                    for key in st.session_state.keys():
                        if isinstance(key, str) and key.startswith('selected_') and isinstance(st.session_state[key], list):
                            if location in st.session_state[key]:
                                st.session_state[key].remove(location)
                    
                    st.rerun()
        
        # Add clear all locations button
        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("Clear All", type="secondary", help="Remove all selected locations"):
                st.session_state.selected_locations_persistent = []
                if 'manual_locations_added' in st.session_state:
                    st.session_state.manual_locations_added = []
                st.rerun()
        
        # Store optimized locations in persistent session state
        st.session_state.selected_locations_persistent = optimized_locations
        return optimized_locations
    
    else:
        st.session_state.selected_locations_persistent = []
        return []