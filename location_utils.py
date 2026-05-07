"""
Location utility functions - Smart deduplication and optimization
"""

from typing import List, Dict, Tuple, Set, Any, Union
from location_data import LOCATION_DATA

class LocationOptimizer:
    """Handles smart location deduplication and search optimization"""
    
    def __init__(self):
        self.hierarchy_weights = {
            'city': 3,
            'region': 2, 
            'state': 2,
            'province': 2,
            'country': 1
        }
    
    def parse_location(self, location: str) -> Dict[str, Any]:
        """Parse a location string into components"""
        parts = [part.strip() for part in location.split(',')]
        
        if len(parts) == 1:
            return {'type': 'unknown', 'location': parts[0], 'specificity': 1}
        elif len(parts) == 2:
            return {'type': 'country_or_region', 'location': parts[0], 'parent': parts[1], 'specificity': 2}
        elif len(parts) == 3:
            return {'type': 'city', 'location': parts[0], 'region': parts[1], 'country': parts[2], 'specificity': 3}
        else:
            return {'type': 'unknown', 'location': location, 'specificity': 1}
    
    def detect_hierarchy_conflicts(self, locations: List[str]) -> List[Dict]:
        """Detect when broader and specific locations overlap"""
        conflicts = []
        parsed_locations = [self.parse_location(loc) for loc in locations]
        
        for i, loc1 in enumerate(parsed_locations):
            for j, loc2 in enumerate(parsed_locations):
                if i != j and self._is_contained_in(loc1, loc2):
                    conflicts.append({
                        'specific': locations[i],
                        'broad': locations[j],
                        'recommendation': 'use_specific'
                    })
        
        return conflicts
    
    def _is_contained_in(self, specific_loc: Dict, broad_loc: Dict) -> bool:
        """Check if specific location is contained within broader location"""
        if specific_loc['specificity'] <= broad_loc['specificity']:
            return False
        
        # Check if city is in a selected state/region
        if (specific_loc['type'] == 'city' and 
            broad_loc['type'] == 'country_or_region' and
            'region' in specific_loc and 
            specific_loc['region'] == broad_loc['location']):
            return True
        
        # Check if city/region is in a selected country
        if ('country' in specific_loc and 
            broad_loc['type'] == 'country_or_region' and
            specific_loc['country'] == broad_loc['location']):
            return True
        
        return False
    
    def optimize_locations(self, locations: List[str]) -> Tuple[List[str], Dict]:
        """Optimize location list to minimize duplicate searches"""
        if not locations:
            return [], {'removed': 0, 'conflicts': [], 'credits_saved': 0}
        
        conflicts = self.detect_hierarchy_conflicts(locations)
        optimized_locations = locations.copy()
        removed_count = 0
        
        # Remove broader locations when specific ones exist
        for conflict in conflicts:
            if conflict['broad'] in optimized_locations:
                optimized_locations.remove(conflict['broad'])
                removed_count += 1
        
        # Remove exact duplicates
        optimized_locations = list(dict.fromkeys(optimized_locations))
        
        optimization_report = {
            'removed': removed_count,
            'conflicts': conflicts,
            'credits_saved': removed_count,
            'efficiency_score': self._calculate_efficiency_score(locations, optimized_locations)
        }
        
        return optimized_locations, optimization_report
    
    def _calculate_efficiency_score(self, original: List[str], optimized: List[str]) -> float:
        """Calculate efficiency score (0-100)"""
        if not original:
            return 100.0
        
        savings = len(original) - len(optimized)
        return min(100.0, (savings / len(original)) * 100)
    
    def suggest_location_improvements(self, locations: List[str]) -> List[Dict]:
        """Suggest improvements to location selection"""
        suggestions = []
        parsed_locations = [self.parse_location(loc) for loc in locations]
        
        # Group by country
        country_groups = {}
        for i, parsed in enumerate(parsed_locations):
            country = parsed.get('country', parsed.get('parent', 'Unknown'))
            if country not in country_groups:
                country_groups[country] = []
            country_groups[country].append((locations[i], parsed))
        
        # Suggest optimizations for each country
        for country, locs in country_groups.items():
            if len(locs) > 3:  # Multiple locations in same country
                city_count = sum(1 for _, parsed in locs if parsed['type'] == 'city')
                if city_count > 5:
                    suggestions.append({
                        'type': 'country_optimization',
                        'message': f"Consider searching entire {country} instead of {city_count} individual cities",
                        'current_cost': len(locs),
                        'suggested_cost': 1,
                        'savings': len(locs) - 1
                    })
        
        return suggestions
    
    def estimate_search_cost(self, locations: List[str]) -> Dict:
        """Estimate API credit cost for search"""
        optimized_locations, optimization_report = self.optimize_locations(locations)
        
        return {
            'original_cost': len(locations),
            'optimized_cost': len(optimized_locations),
            'savings': len(locations) - len(optimized_locations),
            'efficiency_score': optimization_report['efficiency_score']
        }