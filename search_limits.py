"""
Search Limits and Validation Module
Prevents overloading and connection timeouts by enforcing smart limits
"""

import streamlit as st


class SearchLimits:
    """Manages search limits and validation"""
    
    # Maximum total searches to prevent timeouts
    MAX_TOTAL_SEARCHES = 20
    MAX_LOCATIONS_PER_KEYWORD = 15
    MAX_KEYWORDS = 3
    
    # Recommended limits for best performance
    RECOMMENDED_TOTAL_SEARCHES = 10
    RECOMMENDED_LOCATIONS = 8
    
    @classmethod
    def validate_search_scope(cls, keywords: str, locations: list) -> dict:
        """Validate search scope and return validation results"""
        
        # Parse keywords
        keyword_list = [k.strip() for k in keywords.split(',') if k.strip()]
        num_keywords = len(keyword_list)
        num_locations = len(locations)
        total_searches = num_keywords * num_locations
        
        result = {
            'valid': True,
            'warnings': [],
            'errors': [],
            'recommendations': [],
            'stats': {
                'keywords': num_keywords,
                'locations': num_locations,
                'total_searches': total_searches,
                'estimated_time': cls._estimate_time(total_searches)
            }
        }
        
        # Check hard limits
        if total_searches > cls.MAX_TOTAL_SEARCHES:
            result['valid'] = False
            result['errors'].append(
                f"Total searches ({total_searches}) exceeds maximum limit of {cls.MAX_TOTAL_SEARCHES}. "
                f"This prevents connection timeouts and ensures reliable results."
            )
        
        if num_keywords > cls.MAX_KEYWORDS:
            result['valid'] = False
            result['errors'].append(
                f"Maximum {cls.MAX_KEYWORDS} keywords allowed. You have {num_keywords} keywords."
            )
        
        if num_locations > cls.MAX_LOCATIONS_PER_KEYWORD and num_keywords > 1:
            result['valid'] = False
            result['errors'].append(
                f"With multiple keywords, maximum {cls.MAX_LOCATIONS_PER_KEYWORD} locations allowed. "
                f"You have {num_locations} locations."
            )
        
        # Performance warnings
        if total_searches > cls.RECOMMENDED_TOTAL_SEARCHES:
            result['warnings'].append(
                f"Large search ({total_searches} total searches) may take longer and use more API credits."
            )
        
        if num_locations > cls.RECOMMENDED_LOCATIONS:
            result['warnings'].append(
                f"Searching {num_locations} locations may take significant time. "
                f"Consider reducing to {cls.RECOMMENDED_LOCATIONS} or fewer for faster results."
            )
        
        # Generate recommendations
        if not result['valid']:
            result['recommendations'] = cls._generate_recommendations(num_keywords, num_locations)
        
        return result
    
    @classmethod
    def _estimate_time(cls, total_searches: int) -> str:
        """Estimate search completion time"""
        # Rough estimate: 3-5 seconds per search
        estimated_seconds = total_searches * 4
        
        if estimated_seconds < 60:
            return f"{estimated_seconds} seconds"
        elif estimated_seconds < 3600:
            minutes = estimated_seconds // 60
            return f"{minutes} minutes"
        else:
            hours = estimated_seconds // 3600
            minutes = (estimated_seconds % 3600) // 60
            return f"{hours}h {minutes}m"
    
    @classmethod
    def _generate_recommendations(cls, num_keywords: int, num_locations: int) -> list:
        """Generate recommendations to fix search scope issues"""
        recommendations = []
        
        total_searches = num_keywords * num_locations
        
        if total_searches > cls.MAX_TOTAL_SEARCHES:
            # Calculate better distribution
            if num_keywords > cls.MAX_KEYWORDS:
                recommendations.append(f"Reduce keywords to {cls.MAX_KEYWORDS} or fewer")
            
            max_locations_for_keywords = cls.MAX_TOTAL_SEARCHES // max(num_keywords, 1)
            if num_locations > max_locations_for_keywords:
                recommendations.append(
                    f"With {num_keywords} keywords, use maximum {max_locations_for_keywords} locations"
                )
            
            # Suggest optimal split
            if num_keywords == 1:
                recommendations.append(f"Use maximum {cls.MAX_TOTAL_SEARCHES} locations with 1 keyword")
            elif num_keywords == 2:
                recommendations.append(f"Use maximum {cls.MAX_TOTAL_SEARCHES // 2} locations with 2 keywords")
            else:
                recommendations.append(f"Use maximum {cls.MAX_TOTAL_SEARCHES // 3} locations with 3 keywords")
        
        return recommendations
    
    @classmethod
    def show_search_validation(cls, keywords: str, locations: list):
        """Display search validation with clear messaging"""
        
        if not keywords.strip() or not locations:
            return True  # Don't validate empty searches
        
        validation = cls.validate_search_scope(keywords, locations)
        stats = validation['stats']
        
        # Show search statistics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Keywords", stats['keywords'])
        with col2:
            st.metric("Locations", stats['locations'])
        with col3:
            st.metric("Total Searches", stats['total_searches'])
        with col4:
            st.metric("Est. Time", stats['estimated_time'])
        
        # Show errors (blocking)
        if validation['errors']:
            st.error("**Search Too Large - Please Reduce Scope**")
            for error in validation['errors']:
                st.error(f"❌ {error}")
            
            if validation['recommendations']:
                st.info("**Recommendations:**")
                for rec in validation['recommendations']:
                    st.info(f"💡 {rec}")
            
            # Show limits explanation
            with st.expander("ℹ️ Why These Limits Exist"):
                st.markdown(f"""
                **Connection Stability:**
                - Large searches can cause connection timeouts
                - API servers may reject too many simultaneous requests
                - Your browser connection may be interrupted
                
                **Performance:**
                - Each search uses API credits from your Serper.dev account
                - More searches = longer wait times
                - Maximum {cls.MAX_TOTAL_SEARCHES} searches ensures reliable completion
                
                **Best Practice:**
                - Start with {cls.RECOMMENDED_TOTAL_SEARCHES} or fewer searches
                - Test with smaller scope first
                - Use multiple smaller searches instead of one large search
                """)
        
        # Show warnings (non-blocking)
        elif validation['warnings']:
            st.warning("**Large Search Warning**")
            for warning in validation['warnings']:
                st.warning(f"⚠️ {warning}")
            
            st.info("💡 Consider breaking this into smaller searches for better reliability")
        
        # Show success for reasonable searches
        elif stats['total_searches'] <= cls.RECOMMENDED_TOTAL_SEARCHES:
            st.success(f"✅ Search scope looks good - {stats['total_searches']} total searches")
        
        return validation['valid']