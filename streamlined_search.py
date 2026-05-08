"""
Streamlined Search Interface - Simple and intuitive for first-time users
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from typing import List, Dict
from auth import (
    can_perform_search,
    update_search_count,
    get_user_api_key,
)
from new_search_engine import find_emails_new

def show_loaded_search_results():
    """Display previously loaded search results"""
    loaded_results = st.session_state.get('loaded_search_results', [])
    loaded_info = st.session_state.get('loaded_search_info', {})
    
    if not loaded_results:
        st.error("No loaded results found")
        st.session_state.show_loaded_results = False
        return
    
    # Display header with search info
    st.markdown("## Loaded Search Results")
    st.markdown(f"**Keywords:** {loaded_info.get('keywords', 'Unknown')}")
    st.markdown(f"**Locations:** {', '.join(loaded_info.get('locations', []))}")
    st.markdown(f"**Results:** {loaded_info.get('results_count', 0)} businesses found")
    st.markdown(f"**Date:** {loaded_info.get('created_at', 'Unknown').strftime('%B %d, %Y at %H:%M') if loaded_info.get('created_at') else 'Unknown'}")
    
    # Action buttons
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        if st.button("New Search", type="primary"):
            st.session_state.show_loaded_results = False
            st.rerun()
    
    with col2:
        # Generate CSV for download
        csv_data = generate_results_csv(loaded_results)
        st.download_button(
            label="Download CSV",
            data=csv_data,
            file_name=f"fetchster_results_{loaded_info.get('keywords', 'search').replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv"
        )
    
    # Display results
    st.markdown("---")
    
    # Show results in a table format
    if loaded_results:
        st.markdown(f"### {len(loaded_results)} Businesses Found")
        
        for i, result in enumerate(loaded_results, 1):
            # Try multiple possible business name fields
            business_name = (result.get('name') or 
                           result.get('business_name') or 
                           result.get('title') or 
                           'Unknown Business')
            with st.expander(f"{i}. {business_name}", expanded=False):
                col1, col2 = st.columns(2)
                
                with col1:
                    if result.get('phone'):
                        st.markdown(f"📞 **Phone:** {result['phone']}")
                    if result.get('address'):
                        st.markdown(f"📍 **Address:** {result['address']}")
                    if result.get('website'):
                        st.markdown(f"🌐 **Website:** {result['website']}")
                
                with col2:
                    # Show emails
                    scraped_emails = result.get('emails', [])
                    domain_emails = result.get('domain_emails', [])
                    
                    if scraped_emails:
                        st.markdown("📧 **Found Emails:**")
                        for email in scraped_emails:
                            st.markdown(f"• {email}")
                    
                    if domain_emails:
                        st.markdown("📧 **Suggested Emails:**")
                        for email in domain_emails:
                            st.markdown(f"• {email}")
                    
                    if not scraped_emails and not domain_emails:
                        st.markdown("📧 **No emails found**")
    else:
        st.info("No results to display")

def generate_results_csv(results: List[Dict]) -> str:
    """Generate CSV data from results"""
    if not results:
        return ""
    
    # Create comprehensive CSV with one email per line
    csv_rows = []
    headers = ['Business Name', 'Email', 'Email Type', 'Phone', 'Address', 'Website', 'Source']
    
    for business in results:
        business_name = business.get('name', 'Unknown Business')
        phone = business.get('phone', '')
        address = business.get('address', '')
        website = business.get('website', '')
        
        # Get all emails (scraped + domain-based)
        scraped_emails = business.get('emails', [])
        domain_emails = business.get('domain_emails', [])
        
        # Add scraped emails
        for email in scraped_emails:
            csv_rows.append([
                business_name, email, 'Scraped', phone, address, website, 'Website Content'
            ])
        
        # Add domain-based emails
        for email in domain_emails:
            csv_rows.append([
                business_name, email, 'Generated', phone, address, website, 'Domain Pattern'
            ])
        
        # If no emails found, still add the business info
        if not scraped_emails and not domain_emails:
            csv_rows.append([
                business_name, '', 'None Found', phone, address, website, 'Business Listing'
            ])
    
    # Convert to CSV format
    import io
    output = io.StringIO()
    import csv
    writer = csv.writer(output)
    writer.writerow(headers)
    writer.writerows(csv_rows)
    return output.getvalue()

class StreamlinedSearchEngine:
    """Simple search engine with clear controls"""
    
    def __init__(self):
        self.results = []
        self.search_completed = False
        
    def start_search(self, keywords: str, locations: List[str], options: Dict):
        """Start the search process"""
        if 'search_in_progress' not in st.session_state:
            st.session_state.search_in_progress = False
            
        if 'search_should_stop' not in st.session_state:
            st.session_state.search_should_stop = False
            
        st.session_state.search_in_progress = True
        st.session_state.search_should_stop = False
        
        return self.execute_search(keywords, locations, options)
    
    def stop_search(self):
        """Stop the search process"""
        st.session_state.search_should_stop = True
        st.session_state.search_in_progress = False
        
    def execute_search(self, keywords: str, locations: List[str], options: Dict):
        """Execute the actual search using new API engine"""
        # This method is no longer used - search is handled in the main interface
        return []

def show_streamlined_search_interface():
    """Display the streamlined search interface"""
    
    # Check if we have loaded results to display first
    if st.session_state.get('show_loaded_results', False):
        show_loaded_search_results()
        return
    
    # Get search parameters from session state
    keywords = st.session_state.get('search_keywords', '')
    locations = st.session_state.get('search_locations', [])
    search_options = st.session_state.get('search_options', {})
    
    if not keywords or not locations:
        st.info("💡 Enter keywords and select locations above to start searching")
        return
    
    # Display what will be searched
    st.markdown("## Ready to Search")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown(f"**Keywords:** {keywords}")
        location_display = ", ".join(locations[:3])
        if len(locations) > 3:
            location_display += f" and {len(locations)-3} more"
        st.markdown(f"**Locations:** {location_display}")
    
    with col2:
        total_searches = len(keywords.split(',')) * len(locations)
        st.metric("Estimated Searches", total_searches)
    
    # Check search permissions
    can_search, reason = can_perform_search()
    if not can_search:
        st.error(reason)
        if "trial searches" in reason or "subscription" in reason:
            from payments import show_pricing_cards
            show_pricing_cards()
        return
    
    # Validate search scope before allowing start
    from search_limits import SearchLimits
    search_valid = SearchLimits.show_search_validation(keywords, locations)
    
    # Search controls
    search_in_progress = st.session_state.get('search_in_progress', False)
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        if not search_in_progress:
            if search_valid:
                if st.button("🚀 START SEARCH", type="primary", use_container_width=True):
                    st.session_state.search_in_progress = True
                    st.session_state.search_should_stop = False
                    st.rerun()
            else:
                st.button("🚀 START SEARCH", disabled=True, use_container_width=True, 
                         help="Please reduce search scope to continue")
        else:
            st.button("🔄 Search in progress...", disabled=True, use_container_width=True)
    
    with col2:
        if search_in_progress:
            if st.button("⏹️ STOP", type="secondary", use_container_width=True):
                st.session_state.search_should_stop = True
                st.session_state.search_in_progress = False
                if 'search_state' in st.session_state:
                    del st.session_state.search_state
                st.warning("Search stopped")
                st.rerun()
        else:
            # Reset button for stuck searches
            if st.button("🔄 RESET", use_container_width=True, help="Reset if search appears stuck"):
                st.session_state.search_in_progress = False
                st.session_state.search_should_stop = False
                if 'search_state' in st.session_state:
                    del st.session_state.search_state
                st.success("Search state reset")
                st.rerun()
    
    with col3:
        if search_in_progress:
            if st.button("⏸️ PAUSE", use_container_width=True):
                st.session_state.search_should_stop = True
                st.info("Search paused - click START to resume")
                st.rerun()
    
    # Show search progress if search is running
    if search_in_progress:
        st.markdown("---")
        
        # Initialize search state if not exists
        if 'search_state' not in st.session_state:
            st.session_state.search_state = {
                'current_location_index': 0,
                'results': [],
                'started': False
            }
        
        search_state = st.session_state.search_state
        
        # Start search if just initiated
        if not search_state['started']:
            search_state['started'] = True
            search_state['current_location_index'] = 0
            search_state['results'] = []
        
        # Display progress
        progress_bar = st.progress(search_state['current_location_index'] / max(len(locations), 1))
        status_text = st.empty()
        
        current_index = search_state['current_location_index']
        
        # Check if search is complete
        if current_index >= len(locations):
            progress_bar.progress(1.0)
            status_text.text(f"Search completed! Found {len(search_state['results'])} total results")
            
            # Save results and complete search
            st.session_state.current_search_results = search_state['results']
            st.session_state.search_in_progress = False
            
            # Save to history
            if search_state['results']:
                from search_history import save_search_to_history
                save_search_to_history(keywords, locations, search_state['results'], len(search_state['results']))
                update_search_count()
            
            # Clean up search state
            del st.session_state.search_state
            st.rerun()
            
        # Continue search for current location
        elif not st.session_state.get('search_should_stop', False):
            current_location = locations[current_index]
            status_text.text(f"Searching {keywords} in {current_location}... ({current_index + 1}/{len(locations)})")
            
            # Get API key
            api_key = st.session_state.get('api_key', '') or get_user_api_key()
            
            if not api_key:
                st.error("Please configure your Serper.dev API key in Search Options")
                st.session_state.search_in_progress = False
                del st.session_state.search_state
                return
            
            try:
                # Execute search for current location with timeout handling
                location_results = find_emails_new(
                    keyword=keywords,
                    location=current_location,
                    api_key=api_key,
                    max_results=min(search_options.get('max_results', 50000), 20),  # Limit per location to prevent timeouts
                    use_maps=search_options.get('use_maps', True),
                    use_search=search_options.get('use_search', True),
                    stop_callback=lambda: st.session_state.get('search_should_stop', False)
                )
                
                if location_results:
                    search_state['results'].extend(location_results)
                    status_text.text(f"Found {len(location_results)} results in {current_location}")
                else:
                    status_text.text(f"No results found in {current_location}")
                    
            except Exception as location_error:
                error_msg = str(location_error)
                if "timeout" in error_msg.lower() or "connection" in error_msg.lower():
                    st.warning(f"Connection timeout in {current_location} - continuing with next location")
                    status_text.text(f"Timeout in {current_location} - continuing...")
                else:
                    st.error(f"Error searching {current_location}: {error_msg}")
            
            # Move to next location
            search_state['current_location_index'] += 1
            
            # Shorter pause for better responsiveness
            import time
            time.sleep(0.2)  # Reduced pause to prevent connection timeouts
            st.rerun()
        
        else:
            # Search was stopped
            status_text.text("Search stopped by user")
            st.session_state.search_in_progress = False
            if 'search_state' in st.session_state:
                del st.session_state.search_state

def show_search_results():
    """Display search results in a clean format"""
    
    # Check multiple possible result storage locations
    results = (st.session_state.get('current_search_results', []) or 
               st.session_state.get('search_results', []))
    
    if not results:
        return
    
    st.markdown("---")
    st.markdown("## Search Results")
    
    # Summary metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Results", len(results))
    with col2:
        total_emails = sum(len(r.get('emails', [])) for r in results)
        st.metric("Emails Found", total_emails)
    with col3:
        businesses_with_emails = sum(1 for r in results if r.get('emails'))
        if len(results) > 0:
            success_rate = (businesses_with_emails / len(results)) * 100
            st.metric("Success Rate", f"{success_rate:.1f}%")
    
    # Create clean CSV data for download
    if results:
        csv_data = []
        
        for result in results:
            # Try multiple possible business name fields
            business_name = (result.get('name') or 
                           result.get('business_name') or 
                           result.get('title') or 
                           'Unknown Business')
            website = result.get('website', result.get('url', 'N/A'))
            phone = result.get('phone', 'N/A')
            address = result.get('address', 'N/A')
            location = result.get('location', 'N/A')
            
            # Get emails - if no emails, still show business info
            emails = result.get('emails', [])
            if emails:
                for email in emails:
                    csv_data.append({
                        'Business Name': business_name,
                        'Email': email,
                        'Website': website,
                        'Phone': phone,
                        'Address': address,
                        'Location': location
                    })
            else:
                # Include business even without emails
                csv_data.append({
                    'Business Name': business_name,
                    'Email': '',
                    'Website': website,
                    'Phone': phone,
                    'Address': address,
                    'Location': location
                })
        
        # Create and display clean table
        df = pd.DataFrame(csv_data)
        st.dataframe(df, use_container_width=True)
        
        # Download options
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            csv_data = df.to_csv(index=False)
            st.download_button(
                label="📥 Download Results",
                data=csv_data,
                file_name=f"fetchster_results_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv",
                type="primary",
                use_container_width=True
            )
        
        with col2:
            # Create analytics CSV
            analytics_data = generate_analytics_csv(results)
            st.download_button(
                label="📊 Download Analytics",
                data=analytics_data,
                file_name=f"fetchster_analytics_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col3:
            if st.button("🗑️ Clear", use_container_width=True):
                del st.session_state.current_search_results
                st.rerun()

def generate_analytics_csv(results: List[Dict]) -> str:
    """Generate analytics CSV data"""
    analytics_data = []
    
    for result in results:
        # Get business name from multiple possible fields
        business_name = (result.get('name') or 
                        result.get('business_name') or 
                        result.get('title') or 
                        'Unknown Business')
        
        # Get all emails (scraped + domain guessed)
        scraped_emails = result.get('emails', [])
        domain_emails = result.get('domain_emails', result.get('suggested_emails', []))
        all_emails = scraped_emails + domain_emails
        
        # Create entry for each email found
        for email in all_emails:
            analytics_data.append({
                'Business Name': business_name,
                'Email': email,
                'Website': result.get('website', result.get('url', 'N/A')),
                'Phone': result.get('phone', 'N/A'),
                'Address': result.get('address', 'N/A'),
                'Search Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
        
        # If no emails found, still include the business
        if not all_emails:
            analytics_data.append({
                'Business Name': business_name,
                'Email': '',
                'Website': result.get('website', result.get('url', 'N/A')),
                'Phone': result.get('phone', 'N/A'),
                'Address': result.get('address', 'N/A'),
                'Search Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
    
    if analytics_data:
        df = pd.DataFrame(analytics_data)
        return df.to_csv(index=False)
    else:
        return "No data available"