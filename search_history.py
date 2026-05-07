"""
Search History Management - Store and retrieve previous searches
"""

import streamlit as st
import pandas as pd
import json
from datetime import datetime
from typing import List, Dict, Any
import psycopg2
import os

def save_search_to_history(keywords: str, locations: List[str], results: List[Dict], results_count: int):
    """Save a search to the user's history"""
    try:
        from auth import get_current_user
        user = get_current_user()
        if not user:
            return False
            
        conn = psycopg2.connect(os.environ.get("DATABASE_URL"))
        cur = conn.cursor()
        
        # Get user ID
        cur.execute("SELECT id FROM user_profiles WHERE email = %s", (user.get('email'),))
        user_result = cur.fetchone()
        if not user_result:
            return False
            
        user_id = user_result[0]
        
        # Save search history
        cur.execute("""
            INSERT INTO search_history (user_id, keyword, location, results_count, results_data)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            user_id,
            keywords,
            json.dumps(locations),
            results_count,
            json.dumps(results)
        ))
        
        conn.commit()
        cur.close()
        conn.close()
        return True
        
    except Exception as e:
        st.error(f"Failed to save search history: {e}")
        return False

def get_user_search_history(limit: int = 10) -> List[Dict]:
    """Get user's search history"""
    try:
        from auth import get_current_user
        user = get_current_user()
        if not user:
            return []
            
        conn = psycopg2.connect(os.environ.get("DATABASE_URL"))
        cur = conn.cursor()
        
        # Get user ID
        cur.execute("SELECT id FROM user_profiles WHERE email = %s", (user.get('email'),))
        user_result = cur.fetchone()
        if not user_result:
            return []
            
        user_id = user_result[0]
        
        # Get search history
        cur.execute("""
            SELECT keyword, location, results_count, results_data, created_at
            FROM search_history
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT %s
        """, (user_id, limit))
        
        history = []
        for row in cur.fetchall():
            # Handle locations - could be string or already a list
            locations_data = row[1]
            if isinstance(locations_data, str):
                locations = json.loads(locations_data) if locations_data else []
            elif isinstance(locations_data, list):
                locations = locations_data
            else:
                locations = []
            
            # Handle search data - could be string or already a list/dict
            search_data = row[3]
            if isinstance(search_data, str):
                search_results = json.loads(search_data) if search_data else []
            elif isinstance(search_data, (list, dict)):
                search_results = search_data
            else:
                search_results = []
            
            history.append({
                'keywords': row[0],
                'locations': locations,
                'results_count': row[2],
                'search_data': search_results,
                'created_at': row[4]
            })
        
        cur.close()
        conn.close()
        return history
        
    except Exception as e:
        st.error(f"Failed to load search history: {e}")
        return []

def show_search_history_interface():
    """Display search history interface"""
    st.markdown("### Search History")
    
    history = get_user_search_history(20)
    
    if not history:
        st.info("No search history yet. Complete a search to see it here.")
        return
    
    # Summary stats
    total_searches = len(history)
    total_results = sum(h['results_count'] for h in history)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Searches", total_searches)
    with col2:
        st.metric("Total Results Found", total_results)
    
    # History list
    for i, search in enumerate(history):
        with st.expander(f"Search {i+1}: {search['keywords']} ({search['results_count']} results) - {search['created_at'].strftime('%Y-%m-%d %H:%M')}"):
            
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                st.write(f"**Keywords:** {search['keywords']}")
                locations_display = ", ".join(search['locations'][:3])
                if len(search['locations']) > 3:
                    locations_display += f" and {len(search['locations'])-3} more"
                st.write(f"**Locations:** {locations_display}")
                st.write(f"**Results:** {search['results_count']}")
            
            with col2:
                if st.button("Repeat Search", key=f"repeat_{i}"):
                    # Load this search into current session
                    st.session_state.search_keywords_list = search['keywords'].split(', ')
                    st.session_state.selected_locations_persistent = search['locations']
                    st.success("Search loaded! Go to the search tab to run it.")
                    st.rerun()
            
            with col3:
                if search['search_data'] and len(search['search_data']) > 0:
                    # Create downloadable CSV
                    df_data = []
                    for result in search['search_data']:
                        emails_str = '; '.join(result.get('emails', []))
                        df_data.append({
                            'Business Name': result.get('business_name', 'N/A'),
                            'Emails': emails_str,
                            'Website': result.get('website', 'N/A'),
                            'Phone': result.get('phone', 'N/A'),
                            'Address': result.get('address', 'N/A')
                        })
                    
                    if df_data:
                        df = pd.DataFrame(df_data)
                        csv_data = df.to_csv(index=False)
                        st.download_button(
                            label="Download",
                            data=csv_data,
                            file_name=f"search_{i+1}_{search['created_at'].strftime('%Y%m%d')}.csv",
                            mime="text/csv",
                            key=f"download_{i}"
                        )

def delete_search_history():
    """Delete all search history for current user"""
    try:
        from auth import get_current_user
        user = get_current_user()
        if not user:
            return False
            
        conn = psycopg2.connect(os.environ.get("DATABASE_URL"))
        cur = conn.cursor()
        
        # Get user ID
        cur.execute("SELECT id FROM user_profiles WHERE email = %s", (user.get('email'),))
        user_result = cur.fetchone()
        if not user_result:
            return False
            
        user_id = user_result[0]
        
        # Delete search history
        cur.execute("DELETE FROM search_history WHERE user_id = %s", (user_id,))
        
        conn.commit()
        cur.close()
        conn.close()
        return True
        
    except Exception as e:
        st.error(f"Failed to delete search history: {e}")
        return False