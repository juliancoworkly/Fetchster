"""
Enhanced search engine with proper progress tracking and stop controls
"""

import streamlit as st
import time
from typing import List, Dict, Callable, Optional
from clean_searcher import find_emails

class SearchEngine:
    """Enhanced search engine with visual progress tracking and stop controls"""
    
    def __init__(self):
        self.reset_state()
    
    def reset_state(self):
        """Reset search state"""
        if 'search_engine_state' not in st.session_state:
            st.session_state.search_engine_state = {
                'is_running': False,
                'current_keyword': '',
                'current_location': '',
                'current_step': 0,
                'total_steps': 0,
                'results': [],
                'errors': [],
                'start_time': None,
                'stop_requested': False
            }
    
    def start_search(self, keywords: List[str], locations: List[str], 
                    api_key: str, max_results: int = 10, 
                    use_maps: bool = True, use_search: bool = True):
        """Start enhanced search with progress tracking"""
        
        # Reset and initialize state
        self.reset_state()
        search_state = st.session_state.search_engine_state
        
        search_state['is_running'] = True
        search_state['start_time'] = time.time()
        search_state['stop_requested'] = False
        search_state['total_steps'] = len(keywords) * len(locations)
        search_state['current_step'] = 0
        search_state['results'] = []
        search_state['errors'] = []
        
        # Create progress containers
        progress_container = st.container()
        
        with progress_container:
            st.markdown("### Search Progress")
            
            # Main progress bar
            progress_bar = st.progress(0)
            
            # Status display
            status_col1, status_col2, status_col3 = st.columns(3)
            
            with status_col1:
                current_status = st.empty()
            with status_col2:
                time_status = st.empty()
            with status_col3:
                results_count = st.empty()
            
            # Detailed progress
            detailed_progress = st.empty()
            
            # Stop button with persistent state
            stop_col1, stop_col2, stop_col3 = st.columns([1, 2, 1])
            with stop_col2:
                if st.button("🛑 STOP SEARCH", type="secondary", use_container_width=True, key="persistent_stop_search_btn"):
                    search_state['stop_requested'] = True
                    st.session_state.search_in_progress = False
                    st.rerun()
        
        # Execute search if not stopped
        if not search_state['stop_requested']:
            self._execute_search_loop(
                keywords, locations, api_key, max_results, 
                use_maps, use_search, progress_bar, 
                current_status, time_status, results_count, detailed_progress
            )
        
        # Mark search as completed
        search_state['is_running'] = False
    
    def _execute_search_loop(self, keywords: List[str], locations: List[str], 
                           api_key: str, max_results: int, use_maps: bool, 
                           use_search: bool, progress_bar, current_status, 
                           time_status, results_count, detailed_progress):
        """Execute the main search loop with progress updates"""
        
        search_state = st.session_state.search_engine_state
        results_per_query = max(1, max_results // search_state['total_steps'])
        
        try:
            for keyword_idx, keyword in enumerate(keywords):
                if search_state['stop_requested']:
                    break
                    
                for location_idx, location in enumerate(locations):
                    if search_state['stop_requested']:
                        break
                    
                    # Update current search info
                    search_state['current_keyword'] = keyword
                    search_state['current_location'] = location
                    search_state['current_step'] += 1
                    
                    # Calculate progress
                    progress = search_state['current_step'] / search_state['total_steps']
                    progress_bar.progress(progress)
                    
                    # Update status displays
                    current_status.text(f"Step {search_state['current_step']}/{search_state['total_steps']}")
                    
                    elapsed_time = time.time() - search_state['start_time']
                    time_status.text(f"Time: {elapsed_time:.1f}s")
                    
                    results_count.text(f"Found: {len(search_state['results'])}")
                    
                    # Detailed progress
                    with detailed_progress.container():
                        st.info(f"Searching: **{keyword}** in **{location}**")
                        
                        # Show mini progress for this specific search
                        mini_progress = st.progress(0)
                        mini_status = st.empty()
                    
                    # Execute individual search with callback
                    def update_mini_progress(status: str, progress_val: Optional[float] = None):
                        mini_status.text(status)
                        if progress_val is not None:
                            mini_progress.progress(progress_val)
                    
                    try:
                        # Call the search function
                        mini_status.text("Starting search...")
                        mini_progress.progress(0.1)
                        
                        search_results = find_emails(
                            keyword=keyword.strip(),
                            location=location.strip(),
                            api_key=api_key,
                            max_results=results_per_query,
                            use_maps=use_maps,
                            use_search=use_search,
                            stop_callback=lambda: search_state['stop_requested']
                        )
                        
                        mini_progress.progress(1.0)
                        mini_status.text(f"Completed - Found {len(search_results)} results")
                        
                        # Add results
                        search_state['results'].extend(search_results)
                        
                        # Small delay to show progress
                        time.sleep(0.5)
                        
                    except Exception as e:
                        error_msg = f"Error searching {keyword} in {location}: {str(e)}"
                        search_state['errors'].append(error_msg)
                        mini_status.text(f"Error: {str(e)}")
                        st.error(error_msg)
                        
                    # Check for stop request after each search
                    if search_state['stop_requested']:
                        break
        
        except Exception as e:
            st.error(f"Search execution error: {str(e)}")
            search_state['errors'].append(f"Execution error: {str(e)}")
        
        finally:
            # Finalize search
            search_state['is_running'] = False
            progress_bar.progress(1.0)
            
            total_time = time.time() - search_state['start_time']
            
            if search_state['stop_requested']:
                st.warning(f"Search stopped by user after {total_time:.1f} seconds")
                current_status.text("STOPPED")
            else:
                st.success(f"Search completed in {total_time:.1f} seconds")
                current_status.text("COMPLETED")
            
            time_status.text(f"Total: {total_time:.1f}s")
            results_count.text(f"Final: {len(search_state['results'])}")
            
            # Store results in main session state for UI access
            st.session_state.search_results = search_state['results']
    
    def is_running(self) -> bool:
        """Check if search is currently running"""
        return st.session_state.get('search_engine_state', {}).get('is_running', False)
    
    def stop_search(self):
        """Stop the current search"""
        if 'search_engine_state' in st.session_state:
            st.session_state.search_engine_state['stop_requested'] = True
    
    def get_results(self) -> List[Dict]:
        """Get current search results"""
        return st.session_state.get('search_engine_state', {}).get('results', [])
    
    def get_errors(self) -> List[str]:
        """Get search errors"""
        return st.session_state.get('search_engine_state', {}).get('errors', [])