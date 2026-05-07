"""
Location UI components - Modular interface components
"""

import streamlit as st
from typing import List, Dict
from location_data import COUNTRIES, LOCATION_DATA
from location_utils import LocationOptimizer

class LocationKeyManager:
    """Manages unique keys for Streamlit components"""
    
    def __init__(self):
        self.reset_keys()
    
    def reset_keys(self):
        """Reset key registry on each render"""
        if hasattr(st.session_state, 'multiselect_keys_used'):
            st.session_state.multiselect_keys_used = set()
        else:
            st.session_state.multiselect_keys_used = set()
    
    def get_unique_key(self, base_key: str) -> str:
        """Generate unique key with counter if needed"""
        counter = 0
        unique_key = base_key
        while unique_key in st.session_state.multiselect_keys_used:
            counter += 1
            unique_key = f"{base_key}_{counter}"
        st.session_state.multiselect_keys_used.add(unique_key)
        return unique_key

class LocationSearchPreview:
    """Handles search preview and cost estimation"""
    
    def __init__(self, optimizer: LocationOptimizer):
        self.optimizer = optimizer
    
    def show_search_preview(self, locations: List[str]) -> None:
        """Display search preview with cost estimation"""
        if not locations:
            return
        
        cost_estimate = self.optimizer.estimate_search_cost(locations)
        optimized_locations, optimization_report = self.optimizer.optimize_locations(locations)
        
        # Create preview container
        with st.container():
            st.markdown("#### 🔍 Search Preview")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Original Queries",
                    cost_estimate['original_cost'],
                    help="Number of search queries before optimization"
                )
            
            with col2:
                st.metric(
                    "Optimized Queries", 
                    cost_estimate['optimized_cost'],
                    delta=f"-{cost_estimate['savings']}" if cost_estimate['savings'] > 0 else None,
                    help="Number of search queries after smart optimization"
                )
            
            with col3:
                efficiency_color = "green" if cost_estimate['efficiency_score'] > 80 else "orange" if cost_estimate['efficiency_score'] > 50 else "red"
                st.metric(
                    "Efficiency Score",
                    f"{cost_estimate['efficiency_score']:.0f}%",
                    help="How optimized your location selection is"
                )
            
            # Show optimization details if any
            if optimization_report['conflicts']:
                st.warning(f"⚠️ Found {len(optimization_report['conflicts'])} overlapping locations that will be automatically optimized")
                
                with st.expander("View Optimization Details"):
                    for conflict in optimization_report['conflicts']:
                        st.info(f"Removing '{conflict['broad']}' because '{conflict['specific']}' is more specific")
            
            # Show final search terms
            if optimized_locations:
                st.success(f"✅ Final search will use {len(optimized_locations)} optimized location(s)")

class DirectCitySearch:
    """Handles direct city search functionality"""
    
    def __init__(self, key_manager: LocationKeyManager):
        self.key_manager = key_manager
        self._city_options = None
    
    def get_city_options(self) -> List[Dict]:
        """Get all available cities with context"""
        if self._city_options is None:
            self._city_options = []
            
            # Process the complete location database
            for country, cities in LOCATION_DATA.items():
                if isinstance(cities, list):
                    for city in cities:
                        self._city_options.append({
                            'city': city,
                            'country': country,
                            'display': f"{city}, {country}"
                        })
            
            # Sort alphabetically by city name
            self._city_options.sort(key=lambda x: x['city'])
        
        return self._city_options
    
    def show_direct_search(self) -> List[str]:
        """Display direct city search interface with single country selection"""
        st.markdown("**Search cities by country - select one country at a time:**")
        
        # Organize cities by country
        cities_by_country = {}
        city_data = self.get_city_options()
        
        for city_info in city_data:
            country = city_info['country']
            if country not in cities_by_country:
                cities_by_country[country] = []
            cities_by_country[country].append(city_info)
        
        # Sort countries alphabetically
        sorted_countries = sorted(cities_by_country.keys())
        
        selected_locations = []
        
        # Single country selection dropdown
        selected_country = st.selectbox(
            "Select a country to view its cities:",
            [""] + sorted_countries,
            key=self.key_manager.get_unique_key("country_selectbox"),
            format_func=lambda x: "Choose a country..." if x == "" else f"{self._get_country_flag(x)} {x}"
        )
        
        if selected_country:
            country_cities = cities_by_country[selected_country]
            
            st.markdown(f"**{self._get_country_flag(selected_country)} {selected_country}** - {len(country_cities)} cities available")
            
            # Select all cities button
            col1, col2 = st.columns([3, 1])
            
            with col1:
                select_all_country = st.button(
                    f"Select all {len(country_cities)} cities in {selected_country}",
                    key=self.key_manager.get_unique_key(f"select_all_btn_{selected_country}"),
                    help=f"This will add all cities from {selected_country} to your search"
                )
            
            with col2:
                if len(country_cities) > 20:
                    st.caption(f"⚠️ {len(country_cities)} searches")
                else:
                    st.caption(f"✅ {len(country_cities)} searches")
            
            if select_all_country:
                # Add all cities from this country
                for city_info in country_cities:
                    selected_locations.append(f"{city_info['city']}, {city_info['country']}")
                st.success(f"Added all {len(country_cities)} cities from {selected_country}")
            
            # Individual city selection dropdown
            city_options = ["Select cities..."] + [city['city'] for city in country_cities]
            
            selected_cities = st.multiselect(
                f"Or select specific cities in {selected_country}:",
                city_options[1:],  # Skip the placeholder
                key=self.key_manager.get_unique_key(f"cities_multiselect_{selected_country}"),
                placeholder=f"Choose specific cities in {selected_country}..."
            )
            
            # Convert selected cities to location format
            for selected_city in selected_cities:
                for city_info in country_cities:
                    if city_info['city'] == selected_city:
                        selected_locations.append(f"{city_info['city']}, {city_info['country']}")
                        break
        
        return selected_locations
    
    def _get_country_flag(self, country: str) -> str:
        """Get flag emoji for country"""
        flag_map = {
            "United States": "🇺🇸", "United Kingdom": "🇬🇧", "Canada": "🇨🇦", "Australia": "🇦🇺",
            "Germany": "🇩🇪", "France": "🇫🇷", "Italy": "🇮🇹", "Spain": "🇪🇸", "Japan": "🇯🇵",
            "China": "🇨🇳", "India": "🇮🇳", "Brazil": "🇧🇷", "Russia": "🇷🇺", "Mexico": "🇲🇽",
            "South Korea": "🇰🇷", "Netherlands": "🇳🇱", "Switzerland": "🇨🇭", "Sweden": "🇸🇪",
            "Norway": "🇳🇴", "Denmark": "🇩🇰", "Finland": "🇫🇮", "Belgium": "🇧🇪", "Austria": "🇦🇹",
            "Poland": "🇵🇱", "Portugal": "🇵🇹", "Greece": "🇬🇷", "Turkey": "🇹🇷", "Israel": "🇮🇱",
            "Egypt": "🇪🇬", "South Africa": "🇿🇦", "Nigeria": "🇳🇬", "Kenya": "🇰🇪", "Morocco": "🇲🇦",
            "Argentina": "🇦🇷", "Chile": "🇨🇱", "Colombia": "🇨🇴", "Peru": "🇵🇪", "Venezuela": "🇻🇪",
            "Thailand": "🇹🇭", "Vietnam": "🇻🇳", "Singapore": "🇸🇬", "Malaysia": "🇲🇾", "Indonesia": "🇮🇩",
            "Philippines": "🇵🇭", "Pakistan": "🇵🇰", "Bangladesh": "🇧🇩", "Sri Lanka": "🇱🇰",
            "Iran": "🇮🇷", "Iraq": "🇮🇶", "Saudi Arabia": "🇸🇦", "UAE": "🇦🇪", "Jordan": "🇯🇴"
        }
        return flag_map.get(country, "🌍")

class HierarchicalLocationBrowser:
    """Handles hierarchical country/region/city browsing"""
    
    def __init__(self, key_manager: LocationKeyManager):
        self.key_manager = key_manager
    
    def show_hierarchical_browser(self) -> List[str]:
        """Display hierarchical location browser"""
        st.markdown("**Browse by country and region (optional filters):**")
        
        all_locations = []
        
        # Country selection
        selected_countries = st.multiselect(
            "Select countries:",
            COUNTRIES,
            key=self.key_manager.get_unique_key("country_selection"),
            placeholder="Choose countries..."
        )
        
        # Process each selected country
        for selected_country in selected_countries:
            if selected_country in LOCATION_DATA:
                st.markdown(f"**{selected_country} Locations:**")
                country_data = LOCATION_DATA[selected_country]
                
                # For the simplified database, just add all cities from this country
                if isinstance(country_data, list):
                    for city in country_data:
                        all_locations.append(f"{city}, {selected_country}")
                        
                    st.info(f"Added {len(country_data)} cities from {selected_country}")
        
        return all_locations
    
    def _process_country_data(self, country: str, country_data: Dict) -> List[str]:
        """Process specific country data structure"""
        locations = []
        
        if country == "United States":
            locations = self._process_us_data(country, country_data)
        elif country == "United Kingdom":
            locations = self._process_uk_data(country, country_data)
        elif country == "Canada":
            locations = self._process_canada_data(country, country_data)
        elif country == "Australia":
            locations = self._process_australia_data(country, country_data)
        else:
            locations = self._process_generic_country_data(country, country_data)
        
        return locations
    
    def _process_us_data(self, country: str, country_data: Dict) -> List[str]:
        """Process United States data structure"""
        locations = []
        
        selected_states = st.multiselect(
            f"Select {country} states:",
            list(country_data["states"].keys()),
            key=self.key_manager.get_unique_key(f"states_{country}"),
            placeholder="Choose states..."
        )
        
        for state in selected_states:
            locations.append(f"{state}, {country}")
        
        # Cities for selected states
        if selected_states:
            all_state_cities = []
            for state in selected_states:
                all_state_cities.extend(country_data["states"][state])
            
            selected_cities = st.multiselect(
                f"Select cities in {', '.join(selected_states)}:",
                sorted(set(all_state_cities)),
                key=self.key_manager.get_unique_key(f"cities_states_{country}"),
                placeholder="Choose cities..."
            )
            
            for city in selected_cities:
                # Find which state this city belongs to
                for state in selected_states:
                    if city in country_data["states"][state]:
                        locations.append(f"{city}, {state}, {country}")
                        break
        
        return locations
    
    def _process_uk_data(self, country: str, country_data: Dict) -> List[str]:
        """Process United Kingdom data structure"""
        locations = []
        
        selected_uk_countries = st.multiselect(
            f"Select {country} countries/regions:",
            list(country_data["uk_countries"].keys()),
            key=self.key_manager.get_unique_key(f"uk_countries_{country}"),
            placeholder="Choose countries/regions..."
        )
        
        for uk_country in selected_uk_countries:
            locations.append(f"{uk_country}, {country}")
            
            uk_data = country_data["uk_countries"][uk_country]
            
            # Regions
            if "regions" in uk_data:
                selected_regions = st.multiselect(
                    f"Select {uk_country} regions:",
                    uk_data["regions"],
                    key=self.key_manager.get_unique_key(f"regions_uk_{uk_country}"),
                    placeholder="Choose regions..."
                )
                for region in selected_regions:
                    locations.append(f"{region}, {uk_country}, {country}")
            
            # Cities
            if "cities" in uk_data:
                selected_cities = st.multiselect(
                    f"Select {uk_country} cities:",
                    uk_data["cities"],
                    key=self.key_manager.get_unique_key(f"cities_uk_{uk_country}"),
                    placeholder="Choose cities..."
                )
                for city in selected_cities:
                    locations.append(f"{city}, {uk_country}, {country}")
        
        return locations
    
    def _process_canada_data(self, country: str, country_data: Dict) -> List[str]:
        """Process Canada data structure"""
        locations = []
        
        selected_provinces = st.multiselect(
            f"Select {country} provinces/territories:",
            list(country_data["provinces"].keys()),
            key=self.key_manager.get_unique_key(f"provinces_{country}"),
            placeholder="Choose provinces/territories..."
        )
        
        for province in selected_provinces:
            locations.append(f"{province}, {country}")
        
        # Cities for selected provinces
        if selected_provinces:
            all_province_cities = []
            for province in selected_provinces:
                all_province_cities.extend(country_data["provinces"][province])
            
            selected_cities = st.multiselect(
                f"Select cities in {', '.join(selected_provinces)}:",
                sorted(set(all_province_cities)),
                key=self.key_manager.get_unique_key(f"cities_provinces_{country}"),
                placeholder="Choose cities..."
            )
            
            for city in selected_cities:
                # Find which province this city belongs to
                for province in selected_provinces:
                    if city in country_data["provinces"][province]:
                        locations.append(f"{city}, {province}, {country}")
                        break
        
        return locations
    
    def _process_australia_data(self, country: str, country_data: Dict) -> List[str]:
        """Process Australia data structure"""
        locations = []
        
        selected_states = st.multiselect(
            f"Select {country} states/territories:",
            list(country_data["states"].keys()),
            key=self.key_manager.get_unique_key(f"states_{country}"),
            placeholder="Choose states/territories..."
        )
        
        for state in selected_states:
            locations.append(f"{state}, {country}")
        
        # Cities for selected states
        if selected_states:
            all_state_cities = []
            for state in selected_states:
                all_state_cities.extend(country_data["states"][state])
            
            selected_cities = st.multiselect(
                f"Select cities in {', '.join(selected_states)}:",
                sorted(set(all_state_cities)),
                key=self.key_manager.get_unique_key(f"cities_states_{country}"),
                placeholder="Choose cities..."
            )
            
            for city in selected_cities:
                # Find which state this city belongs to
                for state in selected_states:
                    if city in country_data["states"][state]:
                        locations.append(f"{city}, {state}, {country}")
                        break
        
        return locations
    
    def _process_generic_country_data(self, country: str, country_data: Dict) -> List[str]:
        """Process generic country data structure"""
        locations = []
        
        # Handle countries with regions structure (like France)
        if "regions" in country_data:
            selected_regions = st.multiselect(
                f"Select {country} regions:",
                list(country_data["regions"].keys()),
                key=self.key_manager.get_unique_key(f"regions_{country}"),
                placeholder="Choose regions..."
            )
            
            for region in selected_regions:
                locations.append(f"{region}, {country}")
            
            # Cities for selected regions
            if selected_regions:
                all_region_cities = []
                for region in selected_regions:
                    all_region_cities.extend(country_data["regions"][region])
                
                selected_cities = st.multiselect(
                    f"Select cities in {', '.join(selected_regions)}:",
                    sorted(set(all_region_cities)),
                    key=self.key_manager.get_unique_key(f"cities_regions_{country}"),
                    placeholder="Choose cities..."
                )
                
                for city in selected_cities:
                    # Find which region this city belongs to
                    for region in selected_regions:
                        if city in country_data["regions"][region]:
                            locations.append(f"{city}, {region}, {country}")
                            break
        
        # Handle countries with states structure (like Germany)
        elif "states" in country_data:
            selected_states = st.multiselect(
                f"Select {country} states:",
                list(country_data["states"].keys()),
                key=self.key_manager.get_unique_key(f"states_{country}"),
                placeholder="Choose states..."
            )
            
            for state in selected_states:
                locations.append(f"{state}, {country}")
            
            # Cities for selected states
            if selected_states:
                all_state_cities = []
                for state in selected_states:
                    all_state_cities.extend(country_data["states"][state])
                
                selected_cities = st.multiselect(
                    f"Select cities in {', '.join(selected_states)}:",
                    sorted(set(all_state_cities)),
                    key=self.key_manager.get_unique_key(f"cities_states_{country}"),
                    placeholder="Choose cities..."
                )
                
                for city in selected_cities:
                    # Find which state this city belongs to
                    for state in selected_states:
                        if city in country_data["states"][state]:
                            locations.append(f"{city}, {state}, {country}")
                            break
        
        return locations

class BulkLocationInput:
    """Handles bulk location input functionality"""
    
    def __init__(self, key_manager: LocationKeyManager):
        self.key_manager = key_manager
    
    def show_bulk_input(self) -> List[str]:
        """Display bulk location input interface"""
        st.markdown("**Paste or type multiple locations:**")
        
        bulk_text = st.text_area(
            "Enter locations (one per line or comma-separated):",
            height=100,
            placeholder="New York, NY\nLos Angeles, CA\nChicago, IL\n\nOr: New York NY, Los Angeles CA, Chicago IL",
            help="Enter multiple locations separated by commas or new lines"
        )
        
        locations = []
        if bulk_text.strip():
            # Try splitting by newlines first, then by commas
            if '\n' in bulk_text:
                locations = [loc.strip() for loc in bulk_text.split('\n') if loc.strip()]
            else:
                locations = [loc.strip() for loc in bulk_text.split(',') if loc.strip()]
        
        if locations:
            st.success(f"Parsed {len(locations)} location(s) from input")
            
            with st.expander("View Parsed Locations"):
                for i, location in enumerate(locations, 1):
                    st.write(f"{i}. {location}")
        
        return locations