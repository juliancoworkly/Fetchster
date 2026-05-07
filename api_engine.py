"""
Centralized API Engine for Serper.dev Integration
Handles all search functionality with proper error handling and no duplication
"""

import requests
import time
import re
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse


class SerperAPIEngine:
    """Centralized Serper.dev API handler"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_headers = {
            'X-API-KEY': api_key,
            'Content-Type': 'application/json'
        }
    
    def search_maps(self, query: str, max_results: int = 20) -> List[Dict]:
        """Search Google Maps/Places using Serper.dev with multiple strategies"""
        
        # Generate multiple search variations to find more businesses
        search_variations = self._generate_search_variations(query)
        all_results = []
        
        for search_query in search_variations:
            print(f"Searching Maps for variation: {search_query}")
            
            # Try multiple Maps API endpoints and configurations
            endpoints_to_try = [
                {
                    'url': 'https://google.serper.dev/maps',
                    'payload': {
                        'q': search_query,
                        'num': max_results // len(search_variations)
                    }
                },
                {
                    'url': 'https://google.serper.dev/places',
                    'payload': {
                        'q': search_query,
                        'num': max_results // len(search_variations),
                        'type': 'search'
                    }
                }
            ]
            
            for endpoint_config in endpoints_to_try:
                try:
                    print(f"Trying Maps endpoint: {endpoint_config['url']}")
                    response = requests.post(
                        endpoint_config['url'],
                        headers=self.base_headers,
                        json=endpoint_config['payload'],
                        timeout=15  # Reduced timeout to prevent connection issues
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        print(f"Maps API response keys: {list(data.keys())}")
                        
                        # Process different response formats
                        results = self._process_maps_response(data)
                        if results:
                            print(f"Found {len(results)} maps results for: {search_query}")
                            all_results.extend(results)
                            break  # Move to next search variation
                    else:
                        print(f"Maps API error {response.status_code}: {response.text}")
                        
                except Exception as e:
                    print(f"Maps search error with {endpoint_config['url']}: {str(e)}")
                    continue
        
        # Remove duplicates and return
        unique_results = self._remove_duplicate_places(all_results)
        print(f"Total unique Maps results: {len(unique_results)}")
        
        if not unique_results:
            print("No Maps results found, falling back to web search")
            return self._fallback_web_search_for_maps(query, max_results)
        
        return unique_results
    
    def search_web(self, query: str, max_results: int = 20) -> List[Dict]:
        """Search Google Web using Serper.dev"""
        
        try:
            response = requests.post(
                'https://google.serper.dev/search',
                headers=self.base_headers,
                json={'q': query, 'num': max_results},
                timeout=15  # Reduced timeout to prevent connection issues
            )
            
            if response.status_code == 200:
                data = response.json()
                return self._process_web_response(data)
            else:
                print(f"Web search error {response.status_code}: {response.text}")
                return []
                
        except Exception as e:
            print(f"Web search error: {str(e)}")
            return []
    
    def _process_maps_response(self, data: Dict) -> List[Dict]:
        """Process Maps API response in different formats"""
        results = []
        
        # Try different possible response structures
        places_data = (
            data.get('places', []) or
            data.get('local', []) or
            data.get('localResults', []) or
            data.get('organic', [])  # Fallback to organic results
        )
        
        for place in places_data:
            # Skip closed businesses
            business_status = str(place.get('businessStatus', '')).lower()
            if any(status in business_status for status in ['closed', 'permanently']):
                continue
            
            # Extract business information
            title = place.get('title') or place.get('name') or 'Unknown Business'
            
            # Try multiple website field variations
            website = (
                place.get('website') or
                place.get('url') or
                place.get('link') or
                place.get('websiteUri') or
                ''
            )
            
            # Extract contact information
            phone = (
                place.get('phoneNumber') or
                place.get('phone') or
                place.get('formattedPhoneNumber') or
                ''
            )
            
            address = (
                place.get('address') or
                place.get('formattedAddress') or
                place.get('vicinity') or
                ''
            )
            
            results.append({
                'title': self._clean_text(title),
                'link': self._clean_text(website),
                'address': self._clean_text(address),
                'phone': self._clean_text(phone),
                'rating': str(place.get('rating', '')),
                'reviews': str(place.get('ratingCount', place.get('userRatingsTotal', ''))),
                'source': 'Google Maps'
            })
        
        return results
    
    def _process_web_response(self, data: Dict) -> List[Dict]:
        """Process Web search API response"""
        results = []
        
        organic_results = data.get('organic', [])
        for result in organic_results:
            results.append({
                'title': self._clean_text(result.get('title', '')),
                'link': self._clean_text(result.get('link', '')),
                'snippet': self._clean_text(result.get('snippet', '')),
                'source': 'Google Search'
            })
        
        return results
    
    def _fallback_web_search_for_maps(self, query: str, max_results: int) -> List[Dict]:
        """Fallback to web search when Maps API fails"""
        
        # Create Maps-focused web queries
        maps_queries = [
            f"{query} Google Maps",
            f"{query} business directory",
            f"{query} local business",
            f"{query} phone number address"
        ]
        
        all_results = []
        for maps_query in maps_queries:
            web_results = self.search_web(maps_query, max_results // len(maps_queries))
            
            # Filter for business-like results
            for result in web_results:
                link = result.get('link', '')
                title = result.get('title', '')
                
                # Look for business indicators
                if any(indicator in link.lower() for indicator in [
                    'maps.google', 'yelp.', 'facebook.', 'yellowpages.',
                    'foursquare.', 'tripadvisor.', 'zomato.'
                ]) or any(indicator in title.lower() for indicator in [
                    'phone', 'address', 'hours', 'reviews', 'location'
                ]):
                    result['source'] = 'Web Search (Business Focus)'
                    all_results.append(result)
        
        return all_results[:max_results]
    
    def _generate_search_variations(self, query: str) -> List[str]:
        """Generate multiple search variations to find more businesses"""
        variations = []
        
        # Split query into keyword and location
        parts = query.split()
        if len(parts) >= 2:
            location = parts[-1]  # Assume last part is location
            keywords = ' '.join(parts[:-1])
        else:
            keywords = query
            location = ""
        
        # Generate variations for broader search coverage
        base_variations = [
            query,  # Original query
            f"{keywords} {location}",
            f"{keywords} near {location}",
            f"{keywords} in {location}",
            f"{keywords} business {location}",
            f"{keywords} services {location}",
            f"{keywords} company {location}",
            f"best {keywords} {location}",
            f"top {keywords} {location}",
            f"{keywords} directory {location}",
        ]
        
        # Add keyword variations if dealing with coworking
        if 'cowork' in keywords.lower():
            base_variations.extend([
                f"coworking space {location}",
                f"shared office {location}",
                f"workspace {location}",
                f"office rental {location}",
                f"business center {location}",
                f"flexible office {location}",
                f"hot desk {location}",
                f"co working {location}",
                f"collaborative workspace {location}"
            ])
        
        # Remove duplicates and empty strings
        variations = list(set([v.strip() for v in base_variations if v.strip()]))
        
        print(f"Generated {len(variations)} search variations")
        return variations[:5]  # Limit to 5 variations to avoid too many API calls
    
    def _remove_duplicate_places(self, results: List[Dict]) -> List[Dict]:
        """Remove duplicate places based on multiple criteria"""
        seen = set()
        unique_results = []
        
        for result in results:
            # Create unique identifier using multiple fields
            name = result.get('title', '').lower().strip()
            url = result.get('link', '').lower().strip()
            phone = result.get('phone', '').strip()
            address = result.get('address', '').lower().strip()
            
            # Create composite key
            key_parts = []
            if name:
                key_parts.append(name)
            if url:
                key_parts.append(url)
            if phone:
                key_parts.append(phone)
            if address:
                key_parts.append(address[:50])  # First 50 chars of address
            
            unique_key = '|'.join(key_parts)
            
            if unique_key and unique_key not in seen:
                seen.add(unique_key)
                unique_results.append(result)
        
        return unique_results
    
    def _clean_text(self, text: Any) -> str:
        """Clean and normalize text"""
        if text is None:
            return ''
        return str(text).encode('utf-8', errors='replace').decode('utf-8').strip()


class BusinessEmailExtractor:
    """Handles email extraction from business websites"""
    
    def __init__(self):
        self.email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    
    def extract_emails_from_text(self, text: str) -> List[str]:
        """Extract emails from text using regex"""
        if not text:
            return []
        
        emails = self.email_pattern.findall(text)
        
        # Filter out common false positives and file extensions
        filtered_emails = []
        for email in emails:
            email_lower = email.lower()
            # Skip if it's a file extension or common false positive
            if (email_lower.endswith(('.png', '.jpg', '.jpeg', '.gif', '.css', '.js', '.svg', '.ico', '.webp')) or
                any(skip in email_lower for skip in [
                    'example.com', 'test.com', 'placeholder',
                    'noreply', 'no-reply', 'donotreply',
                    '@sentry.wixpress.com', '@sentry-next.wixpress.com'
                ])):
                continue
            
            # Only include valid email formats
            if '@' in email and '.' in email.split('@')[-1]:
                filtered_emails.append(email)
        
        return list(set(filtered_emails))  # Remove duplicates
    
    def generate_common_emails(self, url: str) -> List[str]:
        """Generate common email patterns for a domain"""
        try:
            parsed = urlparse(url if url.startswith('http') else f'http://{url}')
            domain = parsed.netloc.replace('www.', '')
            
            if not domain:
                return []
            
            common_prefixes = [
                'info', 'contact', 'hello', 'support', 'admin',
                'office', 'mail', 'sales', 'team', 'help',
                'service', 'inquiry', 'business', 'welcome',
                'general', 'customer', 'marketing', 'booking',
                'reservations', 'manager', 'director', 'owner',
                'reception', 'enquiry'
            ]
            
            return [f"{prefix}@{domain}" for prefix in common_prefixes]
            
        except Exception:
            return []
    
    def validate_email(self, email: str) -> bool:
        """Basic email validation"""
        return bool(self.email_pattern.match(email))


class WebScraper:
    """Handles website content scraping"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def safe_request(self, url: str, timeout: int = 5, max_retries: int = 2):
        """Make a safe HTTP request with retries and shorter timeouts"""
        for attempt in range(max_retries):
            try:
                # Use shorter timeout to prevent connection hanging
                response = self.session.get(url, timeout=timeout, allow_redirects=True)
                if response.status_code == 200:
                    return response
                else:
                    print(f"HTTP {response.status_code} for {url}")
            except Exception as e:
                print(f"Request attempt {attempt + 1} failed for {url}: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(0.5)  # Shorter wait between retries
        return None
    
    def scrape_for_emails(self, url: str) -> List[str]:
        """Scrape a website for email addresses with comprehensive extraction"""
        if not url:
            return []
        
        all_emails = []
        
        try:
            print(f"Scraping website: {url}")
            response = self.safe_request(url)
            if not response:
                print(f"Failed to get response from {url}")
                return []
            
            # Get raw HTML content for email extraction
            html_content = response.text
            
            # Initialize email extractor
            extractor = BusinessEmailExtractor()
            
            # 1. Extract emails from raw HTML using regex
            import re
            
            # Look for mailto links
            mailto_pattern = r'mailto:([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
            mailto_emails = re.findall(mailto_pattern, html_content, re.IGNORECASE)
            for email in mailto_emails:
                if extractor.validate_email(email):
                    all_emails.append(email)
                    print(f"Found mailto email: {email}")
            
            # 2. Extract from HTML using BeautifulSoup
            try:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # Remove script and style elements
                for script in soup(['script', 'style', 'meta', 'link']):
                    script.decompose()
                
                # Get clean text content
                clean_text = soup.get_text()
                
                # Extract emails from clean text
                text_emails = extractor.extract_emails_from_text(clean_text)
                all_emails.extend(text_emails)
                
            except Exception as bs_error:
                print(f"BeautifulSoup parsing error: {bs_error}")
                # Fallback to direct text extraction
                text_emails = extractor.extract_emails_from_text(html_content)
                all_emails.extend(text_emails)
            
            # 3. Look for obfuscated emails (common patterns)
            obfuscated_patterns = [
                r'([a-zA-Z0-9._%+-]+)\s*\[at\]\s*([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
                r'([a-zA-Z0-9._%+-]+)\s*@\s*([a-zA-Z0-9.-]+)\s*\.\s*([a-zA-Z]{2,})',
                r'([a-zA-Z0-9._%+-]+)\s*\(at\)\s*([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
            ]
            
            for pattern in obfuscated_patterns:
                matches = re.findall(pattern, html_content, re.IGNORECASE)
                for match in matches:
                    if len(match) == 2:
                        email = f"{match[0]}@{match[1]}"
                    else:
                        email = f"{match[0]}@{match[1]}.{match[2]}"
                    
                    if extractor.validate_email(email):
                        all_emails.append(email)
                        print(f"Found obfuscated email: {email}")
            
            # Remove duplicates and return
            unique_emails = list(set(all_emails))
            print(f"Total emails found on {url}: {len(unique_emails)}")
            return unique_emails
            
        except Exception as e:
            print(f"Error scraping {url}: {str(e)}")
            return []