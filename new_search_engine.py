"""
New Search Engine - Clean implementation using centralized API
Replaces all old search functionality with no duplication
"""

import time
from typing import List, Dict, Any, Callable, Optional
from api_engine import SerperAPIEngine, BusinessEmailExtractor, WebScraper


class BusinessSearchEngine:
    """Main search engine for finding business emails"""
    
    def __init__(self, api_key: str):
        self.api_engine = SerperAPIEngine(api_key)
        self.email_extractor = BusinessEmailExtractor()
        self.web_scraper = WebScraper()
    
    def search_businesses(
        self,
        keyword: str,
        location: str,
        max_results: int = 50,
        use_maps: bool = True,
        use_search: bool = True,
        stop_callback: Optional[Callable] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for businesses and extract email addresses
        """
        def should_stop():
            return stop_callback and stop_callback()
        
        all_results = []
        query = f"{keyword} {location}"
        
        # Search Google Maps first if enabled
        if use_maps and not should_stop():
            print(f"Searching Maps for: {query}")
            maps_results = self.api_engine.search_maps(query, max_results // 2)
            
            # Process results in smaller batches to prevent timeouts
            batch_size = 5
            for i in range(0, len(maps_results), batch_size):
                if should_stop():
                    break
                    
                batch = maps_results[i:i + batch_size]
                for result in batch:
                    if should_stop():
                        break
                    
                    try:
                        processed_result = self._process_business_result(result, keyword, location)
                        if processed_result:
                            all_results.append(processed_result)
                    except Exception as e:
                        print(f"Error processing business result: {str(e)}")
                        continue
                    
                # Shorter delay between batches
                time.sleep(0.1)
        
        # Search Google Web if enabled
        if use_search and not should_stop():
            print(f"Searching Web for: {query}")
            web_results = self.api_engine.search_web(query, max_results // 2)
            
            # Process web results in smaller batches to prevent timeouts
            batch_size = 5
            for i in range(0, len(web_results), batch_size):
                if should_stop():
                    break
                    
                batch = web_results[i:i + batch_size]
                for result in batch:
                    if should_stop():
                        break
                    
                    try:
                        processed_result = self._process_business_result(result, keyword, location)
                        if processed_result:
                            all_results.append(processed_result)
                    except Exception as e:
                        print(f"Error processing web result: {str(e)}")
                        continue
                    
                # Shorter delay between batches
                time.sleep(0.1)
        
        # Remove duplicates based on URL
        unique_results = self._remove_duplicates(all_results)
        
        print(f"Found {len(unique_results)} unique businesses")
        return unique_results
    
    def _process_business_result(self, result: Dict, keyword: str, location: str) -> Optional[Dict]:
        """Process a single business result and extract emails comprehensively"""
        
        url = result.get('link', '').strip()
        business_name = result.get('title', 'Unknown Business')
        
        if not url and not business_name:
            return None
        
        print(f"Processing: {business_name} - {url}")
        
        # Extract emails from the website with timeout protection
        scraped_emails = []
        if url:
            try:
                scraped_emails = self.web_scraper.scrape_for_emails(url)
            except Exception as e:
                print(f"Error scraping {url}: {str(e)}")
                scraped_emails = []
        
        # Always generate suggested emails for the domain
        suggested_emails = []
        if url:
            suggested_emails = self.email_extractor.generate_common_emails(url)
        
        # Combine all emails - scraped first, then suggested
        all_emails = scraped_emails + suggested_emails
        
        # Extract domain for categorization
        domain = ''
        if url:
            try:
                from urllib.parse import urlparse
                parsed = urlparse(url if url.startswith('http') else f'http://{url}')
                domain = parsed.netloc.replace('www.', '')
            except:
                domain = ''
        
        # Use first scraped email as primary, or first suggested if no scraped emails
        primary_email = ''
        if scraped_emails:
            primary_email = scraped_emails[0]
            print(f"Found real email: {primary_email}")
        elif suggested_emails:
            primary_email = suggested_emails[0]
            print(f"Using suggested email: {primary_email}")
        
        return {
            'name': business_name,  # Using 'name' for consistency with CSV
            'business_name': business_name,
            'url': url,
            'website': url,
            'domain': domain,
            'email': primary_email,  # Primary email for CSV
            'emails': scraped_emails,  # Real emails found
            'domain_emails': suggested_emails,  # Domain-based emails for CSV compatibility
            'suggested_emails': suggested_emails,  # Generated emails
            'all_emails': all_emails,  # Combined list
            'source': result.get('source', 'Unknown'),
            'location': location,
            'keyword': keyword,
            'address': result.get('address', ''),
            'phone': result.get('phone', ''),
            'rating': result.get('rating', ''),
            'reviews': result.get('reviews', ''),
            'status': 'active',
            'email_source': 'scraped' if scraped_emails else 'suggested'
        }
    
    def _remove_duplicates(self, results: List[Dict]) -> List[Dict]:
        """Remove duplicate results based on URL and business name"""
        seen_urls = set()
        seen_names = set()
        unique_results = []
        
        for result in results:
            url = result.get('url', '').lower()
            name = result.get('business_name', '').lower()
            
            # Create a unique key
            unique_key = f"{url}|{name}"
            
            if unique_key not in seen_urls and url and name:
                seen_urls.add(unique_key)
                unique_results.append(result)
        
        return unique_results


def find_emails_new(
    keyword: str,
    location: str,
    api_key: str,
    max_results: int = 50,
    use_maps: bool = True,
    use_search: bool = True,
    stop_callback: Optional[Callable] = None
) -> List[Dict[str, Any]]:
    """
    New main function to find business emails
    Replaces the old find_emails function
    """
    if not api_key:
        print("ERROR: No API key provided")
        return []
    
    try:
        search_engine = BusinessSearchEngine(api_key)
        return search_engine.search_businesses(
            keyword=keyword,
            location=location,
            max_results=max_results,
            use_maps=use_maps,
            use_search=use_search,
            stop_callback=stop_callback
        )
    except Exception as e:
        print(f"Search error: {str(e)}")
        return []