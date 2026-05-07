"""
Search options module - separated for clean code organization
"""
import streamlit as st
from search_styles import get_search_styles

def show_search_options_interface():
    """Display search options interface"""
    
    # Apply search-specific styles
    st.markdown(get_search_styles(), unsafe_allow_html=True)
    
    st.markdown("### Search Options")
    st.markdown("Configure your search parameters")
    
    # API Key management
    from auth import get_user_api_key, save_user_api_key
    
    with st.expander("API Configuration", expanded=False):
        st.markdown("**Serper.dev API Key**")
        
        # Get current saved API key
        current_api_key = get_user_api_key()
        
        if current_api_key:
            # Show masked version of saved key
            masked_key = current_api_key[:8] + "*" * (len(current_api_key) - 12) + current_api_key[-4:] if len(current_api_key) > 12 else "*" * len(current_api_key)
            st.success(f"Using saved API key: {masked_key}")
            st.session_state.api_key = current_api_key
            
            # Option to update API key
            if st.button("Update API Key"):
                st.session_state.show_api_input = True
                st.rerun()
        
        # Show API key input if no key saved or user wants to update
        if not current_api_key or st.session_state.get('show_api_input', False):
            api_key = st.text_input(
                "Enter your Serper.dev API key:",
                type="password",
                placeholder="Your API key",
                label_visibility="collapsed"
            )
            
            if api_key:
                if save_user_api_key(api_key):
                    st.session_state.api_key = api_key
                    st.session_state.show_api_input = False
                    st.success("API key saved securely!")
                    st.rerun()
                else:
                    st.error("Failed to save API key")
            
            if not current_api_key:
                st.warning("Please enter your Serper.dev API key to perform searches")
    
    # Search parameters
    st.markdown("**Search Volume:**")
    max_results = st.slider(
        "Maximum results per search:",
        min_value=10,
        max_value=100000,
        value=50000,
        step=100,
        label_visibility="collapsed"
    )
    
    # Advanced options (remove redundant multiselect)
    with st.expander("Advanced Options", expanded=False):
        use_maps = st.checkbox("Use Google Maps search", value=True)
        use_search = st.checkbox("Use Google Search", value=True)
        
        # Email validation options
        st.markdown("**Email Validation**")
        validate_emails = st.checkbox("Validate email formats", value=True)
        remove_duplicates = st.checkbox("Remove duplicate emails", value=True)
        
        # Website analysis
        st.markdown("**Website Analysis**")
        analyze_websites = st.checkbox("Analyze business websites", value=True)
        extract_hidden_emails = st.checkbox("Extract hidden emails from HTML", value=True)
        
        # Last Search Results Section
        st.markdown("---")
        st.markdown("**Last Search Results**")
        
        # Check for current search results
        current_results = st.session_state.get('current_search_results', [])
        
        if current_results:
            st.success(f"Found {len(current_results)} results from your last search")
            
            # Show summary
            total_emails = sum(len(r.get('emails', [])) + len(r.get('domain_emails', [])) for r in current_results)
            st.metric("Total Emails Available", total_emails)
            
            # Quick download and clear options
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("📥 Download Last Results", use_container_width=True):
                    import pandas as pd
                    from datetime import datetime
                    
                    # Generate CSV data for last results
                    csv_data = []
                    for result in current_results:
                        business_name = (result.get('name') or 
                                       result.get('business_name') or 
                                       result.get('title') or 
                                       'Unknown Business')
                        
                        # Get all emails
                        scraped_emails = result.get('emails', [])
                        domain_emails = result.get('domain_emails', result.get('suggested_emails', []))
                        all_emails = scraped_emails + domain_emails
                        
                        if all_emails:
                            for email in all_emails:
                                csv_data.append({
                                    'Business Name': business_name,
                                    'Email': email,
                                    'Website': result.get('website', result.get('url', 'N/A')),
                                    'Phone': result.get('phone', 'N/A'),
                                    'Address': result.get('address', 'N/A'),
                                    'Location': result.get('location', 'N/A')
                                })
                        else:
                            csv_data.append({
                                'Business Name': business_name,
                                'Email': '',
                                'Website': result.get('website', result.get('url', 'N/A')),
                                'Phone': result.get('phone', 'N/A'),
                                'Address': result.get('address', 'N/A'),
                                'Location': result.get('location', 'N/A')
                            })
                    
                    if csv_data:
                        df = pd.DataFrame(csv_data)
                        csv_string = df.to_csv(index=False)
                        
                        st.download_button(
                            label="Download CSV",
                            data=csv_string,
                            file_name=f"fetchster_last_results_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                            mime="text/csv",
                            use_container_width=True,
                            key="download_last_results"
                        )
            
            with col2:
                if st.button("🗑️ Clear Results", use_container_width=True):
                    del st.session_state.current_search_results
                    st.success("Last results cleared")
                    st.rerun()
                    
            # Show preview of results
            st.markdown("**Preview (First 5 Results):**")
            for i, result in enumerate(current_results[:5], 1):
                business_name = (result.get('name') or 
                               result.get('business_name') or 
                               result.get('title') or 
                               'Unknown Business')
                emails = result.get('emails', []) + result.get('domain_emails', [])
                st.write(f"{i}. **{business_name}** - {len(emails)} emails")
                
        else:
            st.info("No recent search results found. Complete a search to see results here.")
    
    # Store options in session state
    st.session_state.search_options = {
        'max_results': max_results,
        'use_maps': use_maps,
        'use_search': use_search,
        'validate_emails': validate_emails,
        'remove_duplicates': remove_duplicates,
        'analyze_websites': analyze_websites,
        'extract_hidden_emails': extract_hidden_emails
    }
    
    return st.session_state.search_options