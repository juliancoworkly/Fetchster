"""
Clean search interface module - handles all search UI components
"""

import streamlit as st
from typing import List, Dict, Any
from datetime import datetime
from search_engine import SearchEngine
from auth import save_search_history

def show_search_interface():
    """Display the clean search interface with enhanced controls"""
    
    st.markdown("## Start Your Search")
    
    # Get search parameters from session state
    keyword = st.session_state.get('search_keywords', '')
    location = st.session_state.get('search_locations', [])
    search_options = st.session_state.get('search_options', {})
    
    # Show what will be searched
    if keyword and location:
        st.markdown("**Ready to search:**")
        st.info(f"Keywords: {keyword}")
        
        # Format location display properly
        if isinstance(location, list):
            location_display = ", ".join(location) if len(location) <= 5 else f"{', '.join(location[:5])} and {len(location)-5} more"
        else:
            location_display = location
        st.info(f"Locations: {location_display}")
        
        # Check search permissions
        from auth import can_perform_search
        can_search, reason = can_perform_search()
        
        if not can_search:
            st.error(reason)
            if "trial searches" in reason:
                st.markdown("### Upgrade Your Account")
                from payments import show_pricing_cards
                show_pricing_cards()
            return
        
        # Initialize search engine
        search_engine = SearchEngine()
        search_in_progress = st.session_state.get('search_in_progress', False)
        
        # Search controls - always show button with different states
        col1, col2 = st.columns([3, 1])
        
        with col1:
            if not search_in_progress:
                if st.button("🚀 START SEARCH", type="primary", use_container_width=True, key="enhanced_search_start_btn"):
                    st.session_state.search_in_progress = True
                    st.rerun()
            else:
                st.info("🔄 Search in progress... Please wait")
        
        with col2:
            # Show search estimate
            total_searches = len(keyword.split(',')) * (len(location) if isinstance(location, list) else 1)
            st.caption(f"~{total_searches} searches")
        
        # Execute search if in progress
        if search_in_progress:
            execute_search(search_engine, keyword, location, search_options)
    
    else:
        st.info("💡 Select keywords and locations above to start searching")

def execute_search(search_engine: SearchEngine, keyword: str, location, search_options: Dict[str, Any]):
    """Execute the search with enhanced progress tracking"""
    
    # Get search parameters
    from auth import get_user_api_key, update_search_count
    
    api_key = getattr(st.session_state, 'api_key', get_user_api_key())
    if not api_key:
        st.error("API key not found. Please add your Serper.dev API key in the Keywords section.")
        st.session_state.search_in_progress = False
        return
    
    max_results = search_options.get('max_results', 10)
    use_maps = search_options.get('use_maps', True)
    use_search = search_options.get('use_search', True)
    
    # Update search count
    update_search_count()
    
    # Prepare search parameters
    keywords_list = [k.strip() for k in keyword.split(',') if k.strip()]
    keywords_list = list(set(keywords_list))  # Remove duplicates
    
    # Handle location parameter
    if isinstance(location, list):
        locations_list = [l.strip() for l in location if l.strip()]
    else:
        locations_list = [l.strip() for l in str(location).split(',') if l.strip()]
    
    locations_list = list(set(locations_list))  # Remove duplicates
    
    # Execute enhanced search
    try:
        search_engine.start_search(
            keywords=keywords_list,
            locations=locations_list,
            api_key=api_key,
            max_results=max_results,
            use_maps=use_maps,
            use_search=use_search
        )
        
        # Reset search state and save results
        st.session_state.search_in_progress = False
        
        # Save to history if results found
        results = search_engine.get_results()
        if results:
            location_str = ", ".join(locations_list)
            from auth import save_search_history
            save_search_history(keyword, location_str, len(results), results)
            
        # Show any errors
        errors = search_engine.get_errors()
        if errors:
            with st.expander(f"⚠️ {len(errors)} Errors Occurred", expanded=False):
                for error in errors:
                    st.error(error)
    
    except Exception as e:
        st.error(f"Search execution error: {str(e)}")
        st.session_state.search_in_progress = False

def show_search_results():
    """Display search results with enhanced formatting"""
    
    if 'search_results' not in st.session_state or not st.session_state.search_results:
        return
    
    results = st.session_state.search_results
    
    st.markdown("---")
    st.markdown("## 📊 Search Results")
    
    # Enhanced summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Results", len(results))
    
    with col2:
        # Handle both email formats: single email string or emails list
        all_emails = []
        for r in results:
            if r.get('email'):
                all_emails.append(r.get('email'))
            elif r.get('emails'):
                all_emails.extend(r.get('emails', []))
        unique_emails = len(set(all_emails))
        st.metric("Unique Emails", unique_emails)
    
    with col3:
        unique_companies = len(set(r.get('business_name', '') for r in results if r.get('business_name')))
        st.metric("Companies Found", unique_companies)
    
    with col4:
        social_links = sum(1 for r in results if r.get('social_links'))
        st.metric("Social Profiles", social_links)
    
    # Results display options
    st.markdown("### Display Options")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        show_details = st.checkbox("Show detailed view", value=True)
    
    with col2:
        filter_emails = st.checkbox("Only show results with emails", value=False)
    
    with col3:
        sort_by = st.selectbox("Sort by", ["Business Name", "Email", "Location", "Keyword"])
    
    # Filter and sort results
    display_results = results.copy()
    
    if filter_emails:
        display_results = [r for r in display_results if r.get('email') or r.get('emails')]
    
    # Sort results
    if sort_by == "Business Name":
        display_results.sort(key=lambda x: x.get('business_name', '').lower())
    elif sort_by == "Email":
        display_results.sort(key=lambda x: x.get('email', '').lower())
    elif sort_by == "Location":
        display_results.sort(key=lambda x: x.get('location', '').lower())
    elif sort_by == "Keyword":
        display_results.sort(key=lambda x: x.get('keyword', '').lower())
    
    # Display results
    st.markdown(f"### Results ({len(display_results)} shown)")
    
    for i, result in enumerate(display_results, 1):
        with st.container():
            if show_details:
                show_detailed_result(i, result)
            else:
                show_compact_result(i, result)
            
            if i < len(display_results):
                st.markdown("---")
    
    # Download options
    if display_results:
        st.markdown("### 📥 Download Results")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📊 Download as CSV", use_container_width=True, key="download_csv_btn"):
                csv_data = generate_csv_download(display_results)
                st.download_button(
                    label="💾 Save CSV File",
                    data=csv_data,
                    file_name=f"search_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True,
                    key="save_csv_file_btn"
                )
        
        with col2:
            if st.button("📋 Copy Email List", use_container_width=True, key="copy_email_list_btn"):
                all_emails = []
                for r in display_results:
                    if r.get('email'):
                        all_emails.append(r.get('email'))
                    elif r.get('emails'):
                        all_emails.extend(r.get('emails', []))
                email_list = '\n'.join(set(all_emails))  # Remove duplicates
                st.code(email_list, language=None)

def show_detailed_result(index: int, result: Dict[str, Any]):
    """Show detailed result card"""
    
    st.markdown(f"#### {index}. {result.get('business_name', 'Unknown Business')}")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Handle both email formats
        emails_to_show = []
        if result.get('email'):
            emails_to_show.append(result['email'])
        elif result.get('emails'):
            emails_to_show.extend(result.get('emails', []))
        
        if emails_to_show:
            if len(emails_to_show) == 1:
                st.markdown(f"**📧 Email:** {emails_to_show[0]}")
            else:
                st.markdown(f"**📧 Emails:** {', '.join(emails_to_show[:3])}")
                if len(emails_to_show) > 3:
                    st.caption(f"+ {len(emails_to_show) - 3} more emails")
        
        if result.get('website'):
            st.markdown(f"**🌐 Website:** {result['website']}")
        
        if result.get('location'):
            st.markdown(f"**📍 Location:** {result['location']}")
        
        if result.get('keyword'):
            st.markdown(f"**🔍 Found with:** {result['keyword']}")
    
    with col2:
        # Social media links
        social_links = result.get('social_links', {})
        if social_links:
            st.markdown("**🔗 Social Media:**")
            for platform, link in social_links.items():
                if link:
                    st.markdown(f"• [{platform.title()}]({link})")

def show_compact_result(index: int, result: Dict[str, Any]):
    """Show compact result line"""
    
    # Handle both email formats
    email_display = 'No email'
    if result.get('email'):
        email_display = result['email']
    elif result.get('emails'):
        emails = result.get('emails', [])
        if emails:
            email_display = emails[0]
            if len(emails) > 1:
                email_display += f" (+{len(emails) - 1} more)"
    
    business = result.get('business_name', 'Unknown')
    location = result.get('location', 'Unknown location')
    
    st.markdown(f"**{index}.** {business} • {email_display} • {location}")

def generate_csv_download(results: List[Dict[str, Any]]) -> str:
    """Generate CSV data for download"""
    
    import pandas as pd
    import io
    
    # Prepare data for CSV
    csv_data = []
    
    for result in results:
        social_links = result.get('social_links', {})
        
        row = {
            'Business Name': result.get('business_name', ''),
            'Email': result.get('email', ''),
            'Website': result.get('website', ''),
            'Location': result.get('location', ''),
            'Keyword': result.get('keyword', ''),
            'Facebook': social_links.get('facebook', ''),
            'Twitter': social_links.get('twitter', ''),
            'LinkedIn': social_links.get('linkedin', ''),
            'Instagram': social_links.get('instagram', ''),
            'TikTok': social_links.get('tiktok', '')
        }
        csv_data.append(row)
    
    # Create DataFrame and convert to CSV
    df = pd.DataFrame(csv_data)
    
    # Use StringIO to create CSV string
    output = io.StringIO()
    df.to_csv(output, index=False)
    return output.getvalue()