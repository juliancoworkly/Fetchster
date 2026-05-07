"""
Clean Streamlit app for email searching - no duplicated functionality
"""
import streamlit as st
import pandas as pd
import json
import os
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from clean_searcher import find_emails
from dashboard_styles import get_dashboard_styles
from keywords_module import show_keywords_interface
from location_module import show_location_interface
from search_options_module import show_search_options_interface
from progress_module import show_progress_interface
from auth import (
    is_authenticated, 
    logout_user, 
    get_user_profile,
    can_perform_search,
    update_search_count,
    save_search_history,
    get_user_api_key,
    save_recent_keyword,
    get_user_search_history,
    activate_subscription
)
from payments import show_pricing_cards, handle_payment_callback
from footer import show_clean_footer

def show_user_dashboard():
    """Display user dashboard with subscription info"""
    st.markdown(get_dashboard_styles(), unsafe_allow_html=True)
    
    user_profile = get_user_profile()
    if not user_profile:
        st.error("Unable to load user profile")
        return
    
    # Header with user info and logout
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown(f"## Welcome, {user_profile.get('email', 'User')}")
    with col2:
        if st.button("Account", use_container_width=True):
            st.session_state.show_subscription = True
            st.rerun()
    with col3:
        if st.button("Sign Out", use_container_width=True):
            logout_user()
            st.rerun()
    
    # Tab navigation
    tab1, tab2, tab3, tab4 = st.tabs(["Analytics", "Search History", "Subscription", "Activation Key"])
    
    with tab1:
        show_analytics_dashboard()
    
    with tab2:
        from search_history import show_search_history_interface
        show_search_history_interface()
    
    with tab3:
        show_pricing_cards()
    
    with tab4:
        st.markdown("### Activation Key")
        activation_key = st.text_input("Enter activation key:", type="password")
        if st.button("Activate", type="primary") and activation_key:
            success, message = activate_subscription(activation_key)
            if success:
                st.success(message)
                st.rerun()
            else:
                st.error(message)

def show_search_history_dashboard():
    """Display comprehensive search history dashboard"""
    st.markdown("### Search History")
    
    from auth import get_user_search_history
    history = get_user_search_history(100)
    
    if not history:
        st.info("No search history found. Start your first search to see results here!")
        return
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Searches", len(history))
    
    with col2:
        total_results = sum(search.get('results_count', 0) for search in history)
        st.metric("Total Results", total_results)
    
    with col3:
        total_emails = sum(count_emails_in_history_record(search) for search in history)
        st.metric("Total Emails Found", total_emails)
    
    with col4:
        if total_results > 0:
            success_rate = (total_emails / total_results) * 100
            st.metric("Email Success Rate", f"{success_rate:.1f}%")
        else:
            st.metric("Email Success Rate", "0%")
    
    # Search history table
    st.markdown("### Search Records")
    
    # Search and filter options
    col1, col2 = st.columns(2)
    
    with col1:
        search_filter = st.text_input("Search keywords:", placeholder="Filter by keyword...")
    
    with col2:
        sort_option = st.selectbox("Sort by:", ["Most Recent", "Most Results", "Keyword A-Z"])
    
    # Filter and sort history
    filtered_history = history
    
    if search_filter:
        filtered_history = [
            h for h in filtered_history 
            if search_filter.lower() in h.get('keyword', '').lower() or 
               search_filter.lower() in h.get('location', '').lower()
        ]
    
    # Sort history
    if sort_option == "Most Results":
        filtered_history.sort(key=lambda x: x.get('results_count', 0), reverse=True)
    elif sort_option == "Keyword A-Z":
        filtered_history.sort(key=lambda x: x.get('keyword', '').lower())
    # Most Recent is default order
    
    # Display history records
    if filtered_history:
        for i, search in enumerate(filtered_history, 1):
            with st.container():
                col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 2, 1])
                
                with col1:
                    st.markdown(f"**{search.get('keyword', 'Unknown')}**")
                    st.caption(f"Location: {search.get('location', 'Unknown')}")
                
                with col2:
                    results_count = search.get('results_count', 0)
                    email_count = count_emails_in_history_record(search)
                    st.markdown(f"**{results_count}** results")
                    st.caption(f"{email_count} emails")
                
                with col3:
                    search_date = search.get('created_at', '')
                    if search_date:
                        try:
                            date_obj = datetime.fromisoformat(search_date.replace('Z', '+00:00'))
                            formatted_date = date_obj.strftime('%Y-%m-%d')
                            formatted_time = date_obj.strftime('%H:%M')
                            st.markdown(formatted_date)
                            st.caption(formatted_time)
                        except:
                            st.markdown(search_date)
                    else:
                        st.markdown("Unknown date")
                
                with col4:
                    # Quick stats
                    results_data = search.get('results_data', [])
                    if results_data:
                        businesses_with_emails = sum(1 for r in results_data if r.get('emails') or r.get('email'))
                        if results_count > 0:
                            success_rate = (businesses_with_emails / results_count) * 100
                            st.markdown(f"**{success_rate:.0f}%** success")
                        else:
                            st.markdown("0% success")
                    else:
                        st.markdown("No data")
                
                with col5:
                    # Create two rows of buttons
                    if st.button("📂 Load", key=f"load_history_{i}", help="Load this search into current session"):
                        load_search_from_history_record(search)
                        st.success("Search loaded!")
                        st.rerun()
                    
                    # Add download button for each search record
                    results_data = search.get('results_data', [])
                    if results_data:
                        # Generate CSV for this specific search
                        csv_data = generate_analytics_csv(results_data)
                        if csv_data:
                            search_date = search.get('created_at', 'unknown')
                            keyword = search.get('keyword', 'search')
                            filename = f"{keyword}_{search_date[:10] if search_date != 'unknown' else 'export'}.csv"
                            
                            st.download_button(
                                label="📥 Export",
                                data=csv_data,
                                file_name=filename,
                                mime="text/csv",
                                key=f"download_history_{i}",
                                help="Download this search as CSV"
                            )
                
                if i < len(filtered_history):
                    st.markdown("---")
    else:
        st.info("No search history matches your filter.")

def count_emails_in_history_record(search_record):
    """Count total emails in a search history record"""
    results_data = search_record.get('results_data', [])
    if not results_data:
        return 0
    
    total_emails = 0
    for result in results_data:
        emails = result.get('emails', [])
        if emails:
            total_emails += len(emails)
        elif result.get('email'):
            total_emails += 1
    
    return total_emails

def load_search_from_history_record(search_record):
    """Load a previous search into the current session"""
    results_data = search_record.get('results_data', [])
    if results_data:
        st.session_state.search_results = results_data
        
    # Also set the search parameters for potential re-search
    st.session_state.search_keywords = search_record.get('keyword', '')
    locations = search_record.get('location', '')
    if locations:
        location_list = [loc.strip() for loc in locations.split(',')]
        st.session_state.search_locations = location_list

def show_analytics_dashboard():
    """Display analytics dashboard"""
    st.markdown("### Search Analytics")
    
    from auth import get_user_search_history
    history = get_user_search_history(50)
    
    if not history:
        st.info("No search history available. Perform some searches to see analytics.")
        return
    
    # Convert to DataFrame for analysis
    df = pd.DataFrame(history)
    
    # Basic metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Searches", len(history))
    with col2:
        total_results = df['results_count'].sum() if 'results_count' in df.columns else 0
        st.metric("Total Results", total_results)
    with col3:
        avg_results = df['results_count'].mean() if 'results_count' in df.columns else 0
        st.metric("Avg Results", f"{avg_results:.1f}")
    with col4:
        unique_keywords = df['keyword'].nunique() if 'keyword' in df.columns else 0
        st.metric("Unique Keywords", unique_keywords)
    
    # Recent searches
    st.markdown("**Recent Searches:**")
    display_df = df[['keyword', 'location', 'results_count', 'created_at']].head(10)
    st.dataframe(display_df, use_container_width=True)

def show_tour_step(step_number, title, content):
    """Display a tour step with explanation"""
    st.info(f"**Step {step_number}: {title}**\n\n{content}")

def start_onboarding_tour():
    """Start the interactive onboarding tour"""
    st.session_state.show_tour = True
    st.session_state.tour_step = 1

def next_tour_step():
    """Move to the next tour step"""
    current_step = st.session_state.get('tour_step', 1)
    if current_step < 6:
        st.session_state.tour_step = current_step + 1
    else:
        complete_tour()

def complete_tour():
    """Complete the onboarding tour"""
    st.session_state.show_tour = False
    st.session_state.tour_step = 0
    st.session_state.onboarding_complete = True

def show_recent_searches_panel():
    """Display quick access panel for recent searches"""
    from search_history import get_user_search_history
    
    # Get last 3 searches
    recent_searches = get_user_search_history(3)
    
    if not recent_searches:
        st.info("No recent searches found. Complete a search to access it here later.")
        return
    
    st.markdown("Access your most recent searches instantly:")
    
    # Display recent searches in columns
    cols = st.columns(min(3, len(recent_searches)))
    
    for i, search in enumerate(recent_searches):
        with cols[i]:
            # Create a card-like display for each search
            with st.container():
                st.markdown(f"**Search {i+1}**")
                st.markdown(f"🔍 *{search['keywords']}*")
                st.markdown(f"📍 {len(search['locations'])} locations")
                st.markdown(f"📧 {search['results_count']} results")
                st.markdown(f"📅 {search['created_at'].strftime('%m/%d %H:%M')}")
                
                # Load search button
                if st.button(f"Load Search {i+1}", key=f"load_search_{i}", use_container_width=True):
                    load_previous_search(search)
                    st.success(f"Loaded search: {search['keywords']}")
                    st.rerun()

def load_previous_search(search_data):
    """Load a previous search into the current session"""
    # Set the search parameters
    st.session_state.search_keywords = search_data['keywords']
    st.session_state.search_locations = search_data['locations']
    
    # Store the results for immediate access
    st.session_state.loaded_search_results = search_data['search_data']
    st.session_state.loaded_search_info = {
        'keywords': search_data['keywords'],
        'locations': search_data['locations'],
        'results_count': search_data['results_count'],
        'created_at': search_data['created_at']
    }
    
    # Set flag to show loaded results
    st.session_state.show_loaded_results = True

def show_search_interface():
    """Display the main search interface using modular components"""
    st.markdown(get_dashboard_styles(), unsafe_allow_html=True)
    
    # Show tour if active
    if st.session_state.get('show_tour', False):
        step = st.session_state.get('tour_step', 1)
        
        if step == 1:
            show_tour_step(1, "Welcome to Fetchster", 
                          "This powerful tool helps you find business emails using Google Maps and Search. Let's take a quick tour!")
        elif step == 2:
            show_tour_step(2, "Search Settings", 
                          "Enter keywords like 'restaurant', 'dentist', or 'coworking space' to find businesses.")
        elif step == 3:
            show_tour_step(3, "Location Selection", 
                          "Choose specific countries, states/provinces, and cities for targeted searches.")
        elif step == 4:
            show_tour_step(4, "Search Sources", 
                          "We search Google Maps for business listings and Google Search for company websites.")
        elif step == 5:
            show_tour_step(5, "Results & Analytics", 
                          "View found emails, business names, and download results as CSV for your use.")
        elif step == 6:
            show_tour_step(6, "Account Features", 
                          "Access your search history, manage subscriptions, and save favorite keywords.")
        
        # Tour navigation
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if step > 1 and st.button("Previous", key="tour_prev"):
                st.session_state.tour_step -= 1
                st.rerun()
        with col2:
            if st.button("Skip Tour", key="tour_skip"):
                complete_tour()
                st.rerun()
        with col3:
            if st.button("Next", key="tour_next"):
                next_tour_step()
                st.rerun()
        
        st.markdown("---")
    
    # Header
    st.markdown("# Welcome to Fetchster")
    st.markdown("**Email harvesting and social discovery — internal tool**")

    # Tour starter for new users
    if not st.session_state.get('onboarding_complete', False) and not st.session_state.get('show_tour', False):
        col1, col2 = st.columns([3, 1])
        with col1:
            st.info("New to Fetchster? Take our quick tour to get started!")
        with col2:
            if st.button("Start Tour", key="main_tour_button"):
                start_onboarding_tour()
                st.rerun()

    tab_google, tab_instagram = st.tabs(["Google (email harvesting)", "Instagram"])

    with tab_google:
        # Main interface using modular components
        col1, col2 = st.columns([1, 1])

        with col1:
            keyword = show_keywords_interface()
            location = show_location_interface()

        with col2:
            search_options = show_search_options_interface()
            show_progress_interface()

        # Store search parameters in session state for the search interface
        st.session_state.search_keywords = keyword
        st.session_state.search_locations = location
        st.session_state.search_options = search_options

        # Streamlined search implementation
        st.markdown("---")
        from streamlined_search import show_streamlined_search_interface, show_search_results

        show_streamlined_search_interface()
        show_search_results()

        # Access to recent searches - moved to bottom
        st.markdown("---")
        st.markdown("### Access to Recent Searches")
        show_recent_searches_panel()

    with tab_instagram:
        from instagram_module import show_instagram_interface
        show_instagram_interface()

# OLD SEARCH FUNCTIONS REMOVED - NOW USING FRESH IMPLEMENTATION

def generate_analytics_csv(results):
    """Generate comprehensive CSV with one email per line and detailed metadata"""
    if not results:
        return None
    
    csv_data = []
    
    # Header row matching your requirements
    csv_data.append([
        'Business', 'Email', 'Source', 'URL', 'Facebook', 'LinkedIn', 
        'Instagram', 'Twitter', 'Location', 'Keyword'
    ])
    
    # Process each result
    for result in results:
        business_name = result.get('business_name', result.get('name', 'Unknown Business'))
        scraped_emails = result.get('emails', [])
        domain_emails = result.get('domain_emails', result.get('suggested_emails', []))
        
        # Get metadata
        source = result.get('source', 'Unknown')
        url = result.get('website', result.get('url', ''))
        social_links = result.get('social_links', {})
        facebook = social_links.get('facebook', '')
        linkedin = social_links.get('linkedin', '')
        instagram = social_links.get('instagram', '')
        twitter = social_links.get('twitter', '')
        location = result.get('location', '')
        keyword = result.get('keyword', '')
        
        # Combine scraped and domain emails for comprehensive lead generation
        all_emails_to_export = []
        seen_emails = set()
        
        # Add scraped emails first (real emails from websites)
        for email in scraped_emails:
            if email and email.lower() not in seen_emails:
                seen_emails.add(email.lower())
                all_emails_to_export.append(email)
        
        # Add domain-based guessed emails (only if not already found)
        for email in domain_emails:
            if email and email.lower() not in seen_emails:
                seen_emails.add(email.lower())
                all_emails_to_export.append(email)
        
        # Create one row per email (real + suggested for comprehensive coverage)
        if all_emails_to_export:
            for email in all_emails_to_export:
                csv_data.append([
                    business_name, email, source, url, facebook, linkedin,
                    instagram, twitter, location, keyword
                ])
        else:
            # Include business without any emails
            csv_data.append([
                business_name, '', source, url, facebook, linkedin,
                instagram, twitter, location, keyword
            ])
    
    # Convert to CSV
    import csv
    import io
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerows(csv_data)
    
    return output.getvalue()

def show_terms_of_service():
    """Display Terms of Service"""
    st.markdown("# Terms of Service")
    try:
        with open('terms_and_conditions.md', 'r') as f:
            terms_content = f.read()
        st.markdown(terms_content)
    except FileNotFoundError:
        st.error("Terms of Service document not found.")
    
    if st.button("Back to Dashboard"):
        st.session_state.show_terms = False
        st.rerun()

def show_privacy_policy():
    """Display Privacy Policy"""
    st.markdown("# Privacy Policy")
    try:
        with open('privacy_policy.md', 'r') as f:
            privacy_content = f.read()
        st.markdown(privacy_content)
    except FileNotFoundError:
        st.error("Privacy Policy document not found.")
    
    if st.button("Back to Dashboard"):
        st.session_state.show_privacy = False
        st.rerun()

def _site_password_gate() -> bool:
    """Render a single-password gate. Returns True once unlocked."""
    if st.session_state.get("site_unlocked"):
        return True

    expected = os.environ.get("FETCHSTER_PASSWORD", "")
    if not expected:
        # No password configured → gate is open. Useful for local dev.
        st.session_state.site_unlocked = True
        return True

    st.markdown("# Fetchster")
    st.markdown("Internal access. Enter the shared password to continue.")
    pw = st.text_input("Password", type="password", key="site_pw_input")
    col_a, _ = st.columns([1, 5])
    with col_a:
        submitted = st.button("Enter", type="primary")
    if submitted:
        if pw == expected:
            st.session_state.site_unlocked = True
            st.rerun()
        else:
            st.error("Incorrect password.")
    return False


def main():
    """Main application entry point"""
    st.set_page_config(
        page_title="Fetchster - Email Harvesting Tool",
        page_icon="🎯",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Initialize session state
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False

    # Site-level password gate. The shared password is read from
    # FETCHSTER_PASSWORD; if unset, falls back to a default for local dev.
    if not _site_password_gate():
        return

    # After the gate, populate session state with a synthetic admin user so the
    # downstream code (search history, can_perform_search, etc.) keeps working.
    if not st.session_state.authenticated:
        st.session_state.authenticated = True
        st.session_state.user_email = "internal@fetchster.local"
        st.session_state.user_name = "Internal User"
        st.session_state.subscription_type = "lifetime"
        st.session_state.subscription_status = "active"
        st.session_state.searches_remaining = 10**9
        st.session_state.total_searches = 0
        st.session_state.is_admin = True

    # Handle page navigation
    if st.session_state.get('show_terms', False):
        show_terms_of_service()
        return

    if st.session_state.get('show_privacy', False):
        show_privacy_policy()
        return

    if st.session_state.get('show_pricing', False):
        from pricing_page import show_pricing_page
        show_pricing_page()
        return

    handle_payment_callback()
    
    # Main application flow
    if st.session_state.get('show_subscription', False):
        show_user_dashboard()
    else:
        show_search_interface()
    
    # Footer
    show_clean_footer()

if __name__ == "__main__":
    main()
