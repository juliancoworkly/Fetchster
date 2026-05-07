"""
Fresh Search Implementation - Clean and Simple
Built from scratch to avoid all previous issues
"""

import streamlit as st
import time
from typing import List, Dict, Optional
from clean_searcher import find_emails
from auth import get_user_api_key, can_perform_search, update_search_count, save_search_history, save_recent_keyword


class FreshSearchEngine:
    """Brand new search engine with zero legacy code"""
    
    def __init__(self):
        self.results = []
        self.is_running = False
        self.total_found = 0
        self.current_progress = 0
        self.total_searches = 0
    
    def execute_search(self, keywords: str, locations, options: Dict) -> List[Dict]:
        """Execute search with clean state management"""
        
        # Reset state
        self.results = []
        self.is_running = True
        self.total_found = 0
        self.current_progress = 0
        
        try:
            # Get API key
            api_key = get_user_api_key()
            if not api_key:
                st.error("API key required. Please add your Serper.dev API key in Keywords section.")
                return []
            
            # Parse parameters
            keyword_list = [k.strip() for k in keywords.split(',') if k.strip()]
            keyword_list = list(set(keyword_list))  # Remove duplicates
            
            # Handle different location formats safely
            location_list = []
            if locations:
                if isinstance(locations, list):
                    for loc in locations:
                        if isinstance(loc, str) and loc.strip():
                            location_list.append(loc.strip())
                elif isinstance(locations, str):
                    location_list = [locations.strip()]
            
            if not location_list:
                st.error("No valid locations provided")
                return []
            
            location_list = list(set(location_list))  # Remove duplicates
            
            # Calculate total searches
            self.total_searches = len(keyword_list) * len(location_list)
            
            # Get search options
            max_results = options.get('max_results', 10)
            use_maps = options.get('use_maps', True)
            use_search = options.get('use_search', True)
            
            # Create status display
            status_container = st.container()
            with status_container:
                progress_text = st.empty()
                results_text = st.empty()
            
            # Execute searches
            progress_text.text(f"Starting {self.total_searches} searches...")
            
            for keyword in keyword_list:
                for location in location_list:
                    self.current_progress += 1
                    
                    # Update display
                    progress_text.text(f"Searching: {keyword} in {location} ({self.current_progress}/{self.total_searches})")
                    results_text.text(f"Found {self.total_found} results so far")
                    
                    # Execute individual search
                    try:
                        search_results = find_emails(
                            keyword=keyword,
                            location=location,
                            api_key=api_key,
                            max_results=max_results,
                            use_maps=use_maps,
                            use_search=use_search
                        )
                        
                        if search_results:
                            self.results.extend(search_results)
                            self.total_found = len(self.results)
                            
                    except Exception as e:
                        st.warning(f"Error searching {keyword} in {location}: {str(e)}")
                        continue
            
            # Final status
            progress_text.text(f"Search completed: {self.current_progress}/{self.total_searches}")
            results_text.text(f"Total results found: {self.total_found}")
            
            return self.results
            
        except Exception as e:
            st.error(f"Search execution failed: {str(e)}")
            return []
        
        finally:
            self.is_running = False


def show_fresh_search_interface():
    """Display completely fresh search interface"""
    
    st.markdown("## Search for Business Emails")
    
    # Get parameters from session state
    keywords = st.session_state.get('search_keywords', '')
    locations = st.session_state.get('search_locations', [])
    search_options = st.session_state.get('search_options', {
        'max_results': 10,
        'use_maps': True,
        'use_search': True
    })
    
    if not keywords:
        st.info("Enter keywords in the Keywords section above")
        return
        
    if not locations:
        st.info("Select locations in the Locations section above")
        return
    
    # Check permissions
    can_search, reason = can_perform_search()
    if not can_search:
        st.error(reason)
        if "trial" in reason.lower():
            st.markdown("### Upgrade Required")
            from payments import show_pricing_cards
            show_pricing_cards()
        return
    
    # Show search preview
    st.markdown("**Ready to search:**")
    st.info(f"Keywords: {keywords}")
    
    location_display = ", ".join(locations[:3])
    if len(locations) > 3:
        location_display += f" and {len(locations)-3} more locations"
    st.info(f"Locations: {location_display}")
    
    # Calculate search count
    keyword_count = len([k for k in keywords.split(',') if k.strip()])
    total_searches = keyword_count * len(locations)
    st.caption(f"This will perform {total_searches} searches")
    
    # Search button
    if st.button("🚀 Start Search", type="primary", use_container_width=True):
        
        # Update search count before starting
        try:
            update_search_count()
        except Exception as e:
            st.warning(f"Could not update search count: {str(e)}")
        
        # Execute search
        search_engine = FreshSearchEngine()
        
        with st.spinner("Executing search..."):
            results = search_engine.execute_search(keywords, locations, search_options)
        
        # Store results
        st.session_state.search_results = results
        
        # Save to history
        if results:
            try:
                save_recent_keyword(keywords)
                location_str = ", ".join(locations)
                save_search_history(keywords, location_str, len(results), results)
            except Exception as e:
                st.warning(f"Could not save to history: {str(e)}")
        
        # Show completion message
        if results:
            st.success(f"Search completed! Found {len(results)} results")
        else:
            st.warning("Search completed but no results found")
        
        # Trigger rerun to show results
        st.rerun()


def show_fresh_search_results():
    """Display fresh search results"""
    
    if 'search_results' not in st.session_state or not st.session_state.search_results:
        return
    
    results = st.session_state.search_results
    
    st.markdown("---")
    st.markdown("## Search Results")
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Results", len(results))
    
    with col2:
        total_emails = sum(len(r.get('emails', [])) for r in results)
        st.metric("Emails Found", total_emails)
    
    with col3:
        businesses_with_emails = sum(1 for r in results if r.get('emails'))
        st.metric("Businesses with Emails", businesses_with_emails)
    
    with col4:
        if len(results) > 0:
            success_rate = (businesses_with_emails / len(results)) * 100
            st.metric("Success Rate", f"{success_rate:.1f}%")
    
    # Results display options
    display_mode = st.radio("Display Mode", ["Compact", "Detailed"], horizontal=True)
    
    # Show results
    for i, result in enumerate(results):
        if display_mode == "Compact":
            show_compact_result(i, result)
        else:
            show_detailed_result(i, result)
    
    # Download options
    st.markdown("### Download Results")
    col1, col2 = st.columns(2)
    
    with col1:
        csv_data = generate_results_csv(results)
        st.download_button(
            "Download CSV",
            data=csv_data,
            file_name=f"search_results_{int(time.time())}.csv",
            mime="text/csv",
            type="primary"
        )
    
    with col2:
        if st.button("Clear Results"):
            if 'search_results' in st.session_state:
                del st.session_state.search_results
            st.rerun()


def show_compact_result(index: int, result: dict):
    """Show compact result display"""
    
    business_name = result.get('business_name', 'Unknown Business')
    emails = result.get('emails', [])
    website = result.get('website', 'N/A')
    
    email_display = emails[0] if emails else "No email found"
    
    with st.expander(f"{index + 1}. {business_name} - {email_display}"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Website:** {website}")
            st.write(f"**Source:** {result.get('source', 'N/A')}")
        
        with col2:
            if len(emails) > 1:
                st.write("**All Emails:**")
                for email in emails:
                    st.write(f"• {email}")


def show_detailed_result(index: int, result: dict):
    """Show detailed result display"""
    
    with st.container():
        st.markdown(f"### {index + 1}. {result.get('business_name', 'Unknown Business')}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Website:** {result.get('website', 'N/A')}")
            st.write(f"**Phone:** {result.get('phone', 'N/A')}")
            st.write(f"**Address:** {result.get('address', 'N/A')}")
        
        with col2:
            emails = result.get('emails', [])
            if emails:
                st.write("**Emails Found:**")
                for email in emails:
                    st.write(f"✉️ {email}")
            else:
                st.write("**No emails found**")
        
        st.divider()


def generate_results_csv(results: List[Dict]) -> str:
    """Generate CSV data from results"""
    
    import pandas as pd
    
    csv_data = []
    
    for result in results:
        emails_str = '; '.join(result.get('emails', []))
        
        csv_data.append({
            'Business Name': result.get('business_name', ''),
            'Emails': emails_str,
            'Website': result.get('website', ''),
            'Phone': result.get('phone', ''),
            'Address': result.get('address', ''),
            'Source': result.get('source', ''),
            'Location': result.get('location', ''),
            'Keyword': result.get('keyword', '')
        })
    
    df = pd.DataFrame(csv_data)
    return df.to_csv(index=False)