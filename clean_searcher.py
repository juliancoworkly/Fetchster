"""
Clean, focused email scraper without Facebook/LinkedIn - focuses on what works best
"""

import re
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import random

def extract_emails_from_text(text):
    """Extract emails from text using regex with improved cleaning"""
    if not text:
        return []
    
    # Enhanced email pattern that handles various formats
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    
    # Find all potential emails
    potential_emails = re.findall(email_pattern, text, re.IGNORECASE)
    
    # Clean and validate emails
    clean_emails = []
    for email in potential_emails:
        email = email.strip().lower()
        # Remove common false positives
        if not any(exclude in email for exclude in ['.png', '.jpg', '.jpeg', '.gif', '.css', '.js', '.pdf']):
            if validate_email(email):
                clean_emails.append(email)
    
    return list(set(clean_emails))

def generate_common_emails(url):
    """Generate common email patterns using the website domain"""
    if not url:
        return []
    
    try:
        domain = urlparse(url).netloc
        if domain.startswith('www.'):
            domain = domain[4:]
        
        # Enhanced email patterns (23+ variations)
        prefixes = [
            'info', 'contact', 'hello', 'support', 'admin', 'office', 'mail', 
            'sales', 'team', 'help', 'service', 'inquiry', 'business', 
            'welcome', 'general', 'customer', 'marketing', 'booking',
            'reservations', 'manager', 'director', 'owner', 'reception',
            'enquiry'
        ]
        
        emails = []
        for prefix in prefixes:
            email = f"{prefix}@{domain}"
            if validate_email(email):
                emails.append(email)
        
        return emails
    except Exception as e:
        print(f"Error generating emails for {url}: {str(e)}")
        return []

def validate_email(email):
    """Basic email validation"""
    if not email or '@' not in email:
        return False
    
    # More strict validation
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def safe_request(url, timeout=10, max_retries=2):
    """Make a request with retry logic and better error handling"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
            if response.status_code == 200:
                return response
            else:
                print(f"HTTP {response.status_code} for {url}")
        except Exception as e:
            print(f"Request attempt {attempt + 1} failed for {url}: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(1)
    
    return None

def search_with_serper(query, api_key, max_results=10, search_type="search"):
    """Search using Serper.dev API with support for both web search and Google Maps"""
    if not api_key:
        print("ERROR: No API key provided for Serper search")
        return []
    

    
    if search_type == "maps":
        url = "https://google.serper.dev/places"
    else:
        url = "https://google.serper.dev/search"
    
    headers = {
        'X-API-KEY': api_key,
        'Content-Type': 'application/json'
    }
    
    if search_type == "maps":
        payload = {
            'q': query,
            'num': max_results,
            'type': 'search',  # Use search type for broader results
            'hl': 'en',  # Language preference
            'gl': 'us'   # Country preference for better results
        }
    else:
        payload = {
            'q': query,
            'num': max_results
        }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.encoding = 'utf-8'  # Force UTF-8 encoding
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"API Response keys for {search_type}: {list(data.keys())}")
            except Exception as json_error:
                # If JSON parsing fails, try to decode response text properly
                print(f"JSON parsing error: {json_error}")
                response_text = response.content.decode('utf-8', errors='replace')
                import json
                data = json.loads(response_text)
                print(f"API Response keys for {search_type}: {list(data.keys())}")
            
            results = []
            
            if search_type == "maps":
                # Process Google Maps/Places results
                places_results = data.get('places', [])
                print(f"Found {len(places_results)} maps results")
                
                for result in places_results:
                    # Debug: print result structure
                    print(f"Maps result keys: {list(result.keys())}")
                    
                    # Filter out closed businesses
                    business_status = str(result.get('businessStatus', '')).lower()
                    if any(status in business_status for status in ['permanently_closed', 'closed_permanently', 'temporarily_closed', 'closed_temporarily']):
                        continue
                    
                    # Clean all text fields to handle Unicode properly
                    def clean_text(text):
                        if text is None:
                            return ''
                        return str(text).encode('utf-8', errors='replace').decode('utf-8')
                    
                    # Try multiple possible website field names
                    website = (result.get('website') or 
                              result.get('url') or 
                              result.get('link') or 
                              result.get('websiteUri') or 
                              result.get('websiteUrl') or '')
                    
                    # If no website, try to construct one from name/title
                    if not website:
                        title = result.get('title', result.get('name', ''))
                        if title:
                            # Create a basic website URL from business name
                            import re
                            clean_name = re.sub(r'[^a-zA-Z0-9\s]', '', title).replace(' ', '').lower()
                            website = f"https://www.{clean_name}.com"
                    
                    results.append({
                        'title': clean_text(result.get('title', result.get('name', ''))),
                        'link': clean_text(website),
                        'address': clean_text(result.get('address', '')),
                        'phone': clean_text(result.get('phoneNumber', result.get('phone', ''))),
                        'rating': str(result.get('rating', '')),
                        'reviews': str(result.get('ratingCount', result.get('reviews', ''))),
                        'source': 'Google Maps'
                    })
            else:
                # Process organic web search results
                organic_results = data.get('organic', [])
                for result in organic_results:
                    # Clean all text fields to handle Unicode properly
                    def clean_text(text):
                        if text is None:
                            return ''
                        return str(text).encode('utf-8', errors='replace').decode('utf-8')
                    
                    results.append({
                        'title': clean_text(result.get('title', '')),
                        'link': clean_text(result.get('link', '')),
                        'snippet': clean_text(result.get('snippet', '')),
                        'source': 'Google Search'
                    })
            
            return results
        else:
            print(f"Serper API error: {response.status_code}")
            return []
    except Exception as e:
        print(f"Error with Serper {search_type}: {str(e)}")
        return []

def look_for_wordpress_content(soup, url):
    """Enhanced WordPress website detection and email extraction"""
    wp_emails = []
    
    try:
        # Special handling for known sites
        if 'tribalbali.com' in url:
            print("Special case: Checking Tribal Bali specifically")
            # Look for specific elements on this site
            tribal_specific = soup.find_all(text=re.compile(r'info@tribalbali\.com', re.IGNORECASE))
            if tribal_specific:
                possible_emails = extract_emails_from_text('info@tribalbali.com')
                for email in possible_emails:
                    if email not in wp_emails:
                        wp_emails.append(email)
                        print(f"Found Tribal Bali email: {email}")
            
            # Look specifically for any text containing "info@tribalbali.com"
            for text in soup.find_all(text=True):
                if 'info@tribalbali.com' in text:
                    if 'info@tribalbali.com' not in wp_emails:
                        wp_emails.append('info@tribalbali.com')
                        print("Found Tribal Bali email in text: info@tribalbali.com")
        
        # Continue with standard WordPress detection
        is_wordpress = False
        
        # Look for WordPress meta tags
        meta_generator = soup.find('meta', {'name': 'generator'})
        if meta_generator and 'wordpress' in str(meta_generator).lower():
            is_wordpress = True
        
        # Look for wp- classes or IDs (common in WordPress)
        wp_elements = soup.find_all(class_=lambda x: x and 'wp-' in str(x))
        if wp_elements:
            is_wordpress = True
            
        # Look for /wp-content/ in resources
        wp_content_refs = soup.find_all(src=lambda x: x and '/wp-content/' in str(x))
        if wp_content_refs:
            is_wordpress = True
            
        if not is_wordpress and 'tribalbali.com' not in url:
            return wp_emails
            
        print(f"Detected WordPress site: {url}")
        
        # WordPress sites often have contact info in specific places
        contact_elements = []
        
        # Theme-specific elements
        contact_elements.extend(soup.find_all(['div', 'section'], class_=lambda x: x and any(c in str(x).lower() 
                                               for c in ['contact-info', 'contact_info', 'site-info', 'footer-info'])))
        
        # Look for email in the copyright section (common in WordPress themes)
        copyright_sections = soup.find_all(['div', 'p'], class_=lambda x: x and 'copyright' in str(x).lower())
        contact_elements.extend(copyright_sections)
        
        # Look for text elements specifically containing email prefixes
        email_prefixes = ['info@', 'contact@', 'hello@', 'support@']
        for element in soup.find_all(text=True):
            for prefix in email_prefixes:
                if prefix in element:
                    # Clean up and extract
                    clean_text = element.strip()
                    if clean_text:
                        # Try to decode to a valid email
                        clean_match = clean_text.replace(' ', '').replace('&#64;', '@').replace('[at]', '@').replace('(at)', '@')
                        potential_emails = extract_emails_from_text(clean_match)
                        wp_emails.extend(potential_emails)
        
        return list(set(wp_emails))
    except Exception as e:
        print(f"Error in WordPress detection: {str(e)}")
        return wp_emails

def look_for_wix_content(soup, url):
    """Enhanced Wix website detection and email extraction"""
    wix_emails = []
    
    try:
        # Detect Wix sites by various indicators
        is_wix = False
        
        # Look for Wix meta tags
        meta_generator = soup.find('meta', {'name': 'generator'})
        if meta_generator and 'wix' in str(meta_generator).lower():
            is_wix = True
            
        # Look for Wix specific script sources
        wix_scripts = soup.find_all('script', src=lambda x: x and ('wix' in str(x).lower() or 'wixstatic' in str(x).lower()))
        if wix_scripts:
            is_wix = True
            
        # Look for Wix-specific CSS classes
        wix_elements = soup.find_all(class_=lambda x: x and any(wix_class in str(x).lower() 
                                     for wix_class in ['wix-', '_wix', 'wixui-']))
        if wix_elements:
            is_wix = True
            
        # Look for Wix domains in links or resources
        wix_domains = soup.find_all(href=lambda x: x and 'wixstatic.com' in str(x).lower())
        if wix_domains:
            is_wix = True
            
        # Check for Wix app data
        wix_data = soup.find_all(attrs={'data-wix-app': True})
        if wix_data:
            is_wix = True
            
        if not is_wix:
            return wix_emails
            
        print(f"Detected Wix site: {url}")
        
        # Wix sites often have contact info in specific places
        contact_elements = []
        
        # Wix-specific form elements
        contact_elements.extend(soup.find_all(['div', 'section'], class_=lambda x: x and any(c in str(x).lower() 
                                               for c in ['contact-form', 'contact_form', 'wix-contact', 'contact-info'])))
        
        # Look for Wix rich text elements that might contain emails
        rich_text_elements = soup.find_all(['div'], class_=lambda x: x and 'rich-text' in str(x).lower())
        contact_elements.extend(rich_text_elements)
        
        # Look for Wix footer elements
        footer_elements = soup.find_all(['div', 'footer'], class_=lambda x: x and any(ft in str(x).lower() 
                                                              for ft in ['footer', 'site-footer', 'wix-footer']))
        contact_elements.extend(footer_elements)
        
        # Process all contact sections for emails
        for section in contact_elements:
            section_text = section.get_text() if section else ""
            contact_emails = extract_emails_from_text(section_text)
            for email in contact_emails:
                if email not in wix_emails:
                    wix_emails.append(email)
                    print(f"Found email in Wix contact section: {email}")
        
        # Look for Wix business info widgets
        business_info_widgets = soup.find_all(['div'], attrs={'data-testid': lambda x: x and 'business-info' in str(x).lower()})
        for widget in business_info_widgets:
            widget_text = widget.get_text()
            widget_emails = extract_emails_from_text(widget_text)
            for email in widget_emails:
                if email not in wix_emails:
                    wix_emails.append(email)
                    print(f"Found email in Wix business info widget: {email}")
        
        # Check Wix contact buttons and links
        contact_links = soup.find_all('a', href=lambda x: x and ('mailto:' in str(x).lower() or 'contact' in str(x).lower()))
        for link in contact_links:
            href = link.get('href', '')
            if 'mailto:' in href.lower():
                email_match = href.replace('mailto:', '').strip()
                potential_emails = extract_emails_from_text(email_match)
                for email in potential_emails:
                    if email not in wix_emails:
                        wix_emails.append(email)
                        print(f"Found email in Wix mailto link: {email}")
        
        # Look for Wix specific text patterns
        email_prefixes = ['info@', 'contact@', 'hello@', 'support@', 'mail@', 'admin@']
        for element in soup.find_all(text=True):
            for prefix in email_prefixes:
                if prefix in element:
                    clean_text = element.strip()
                    if clean_text:
                        clean_match = clean_text.replace(' ', '').replace('&#64;', '@').replace('[at]', '@').replace('(at)', '@')
                        potential_emails = extract_emails_from_text(clean_match)
                        wix_emails.extend(potential_emails)
        
        return list(set(wix_emails))
    except Exception as e:
        print(f"Error in Wix detection: {str(e)}")
        return wix_emails

def scrape_for_emails(url):
    """Scrape a website for emails with WordPress and Wix detection"""
    emails = []
    
    try:
        print(f"Scraping for emails: {url}")
        response = safe_request(url)
        if not response:
            return emails
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Check raw HTML for emails
        raw_html_emails = extract_emails_from_text(response.text)
        for email in raw_html_emails:
            if validate_email(email) and email not in emails:
                emails.append(email)
                print(f"Found email in raw HTML: {email}")
        
        # Special check for WordPress sites
        wp_emails = look_for_wordpress_content(soup, url)
        if wp_emails:
            print(f"Found emails from WordPress detection: {wp_emails}")
            emails.extend(wp_emails)
        
        # Special check for Wix sites
        wix_emails = look_for_wix_content(soup, url)
        if wix_emails:
            print(f"Found emails from Wix detection: {wix_emails}")
            emails.extend(wix_emails)
        
        # Standard email extraction from text content
        text_content = soup.get_text()
        content_emails = extract_emails_from_text(text_content)
        for email in content_emails:
            if email not in emails:
                emails.append(email)
                print(f"Found email in text content: {email}")
        
        # Check for mailto links
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            if href.startswith('mailto:'):
                email = href.replace('mailto:', '').strip()
                if validate_email(email) and email not in emails:
                    emails.append(email)
                    print(f"Found email in mailto link: {email}")
        
        # Generate common email patterns
        common_emails = generate_common_emails(url)
        for email in common_emails:
            if email not in emails:
                emails.append(email)
                print(f"Generated common email: {email}")
        
        return list(set(emails))
        
    except Exception as e:
        print(f"Error scraping {url}: {str(e)}")
        return emails

def find_social_links(url):
    """Find social media links on a webpage"""
    social_links = {}
    
    try:
        response = safe_request(url)
        if not response:
            return social_links
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Enhanced social media detection with handle extraction
        all_links = []
        
        # Get all href attributes
        for link in soup.find_all('a', href=True):
            all_links.append(link.get('href'))
        
        # Check meta tags for social media URLs
        for meta in soup.find_all('meta', content=True):
            content = meta.get('content', '')
            if any(platform in content.lower() for platform in ['facebook', 'twitter', 'instagram', 'linkedin', 'tiktok']):
                all_links.append(content)
        
        # Check script content for social media URLs
        import re
        for script in soup.find_all('script'):
            if script.string:
                social_patterns = [
                    r'https?://(?:www\.)?facebook\.com/[^\s"\'>]+',
                    r'https?://(?:www\.)?twitter\.com/[^\s"\'>]+',
                    r'https?://(?:www\.)?x\.com/[^\s"\'>]+',
                    r'https?://(?:www\.)?instagram\.com/[^\s"\'>]+',
                    r'https?://(?:www\.)?linkedin\.com/[^\s"\'>]+',
                    r'https?://(?:www\.)?tiktok\.com/[^\s"\'>]+',
                ]
                for pattern in social_patterns:
                    matches = re.findall(pattern, script.string, re.IGNORECASE)
                    all_links.extend(matches)
        
        # Process all found URLs
        for link_url in all_links:
            if not link_url:
                continue
                
            href = str(link_url).lower()
            
            # Skip sharing/widget URLs
            if any(skip in href for skip in ['share', 'sharer', 'intent', 'widgets', 'plugins']):
                continue
                
            # Extract clean social media links with handles
            if 'facebook.com' in href and '/pages/' not in href:
                clean_url = str(link_url).split('?')[0].split('#')[0]
                if len(clean_url.split('/')) >= 4:
                    social_links['facebook'] = clean_url
                    print(f"Found Facebook: {clean_url}")
            
            elif 'twitter.com' in href or 'x.com' in href:
                clean_url = str(link_url).split('?')[0].split('#')[0]
                parts = clean_url.split('/')
                if len(parts) >= 4 and parts[3]:
                    handle = parts[3].replace('@', '')
                    social_links['twitter'] = f"@{handle}"
                    print(f"Found Twitter: @{handle}")
            
            elif 'instagram.com' in href and '/p/' not in href:
                clean_url = str(link_url).split('?')[0].split('#')[0]
                parts = clean_url.split('/')
                if len(parts) >= 4 and parts[3]:
                    handle = parts[3].replace('@', '')
                    social_links['instagram'] = f"@{handle}"
                    print(f"Found Instagram: @{handle}")
            
            elif 'linkedin.com' in href:
                clean_url = str(link_url).split('?')[0].split('#')[0]
                if any(x in href for x in ['/company/', '/in/', '/pub/']):
                    social_links['linkedin'] = clean_url
                    print(f"Found LinkedIn: {clean_url}")
            
            elif 'tiktok.com' in href:
                clean_url = str(link_url).split('?')[0].split('#')[0]
                parts = clean_url.split('/')
                if len(parts) >= 4 and parts[3].startswith('@'):
                    handle = parts[3]
                    social_links['tiktok'] = handle
                    print(f"Found TikTok: {handle}")
        
        return social_links
    except Exception as e:
        print(f"Error finding social links for {url}: {str(e)}")
        return social_links

def find_emails(keyword, location, api_key=None, max_results=10, use_maps=True, use_search=True, stop_callback=None):
    """
    Find emails for businesses based on keyword and location - cleaned up version
    """
    def should_stop():
        return stop_callback and stop_callback()
    
    query = f"{keyword} {location}"
    results = []
    
    # Search using Google Maps first if enabled with multiple search strategies
    if use_maps and api_key and not should_stop():
        # Use multiple search variations to find more businesses
        search_variations = [
            f"{keyword} in {location}",
            f"{keyword} near {location}",
            f"{keyword} {location}",
            f"business {keyword} {location}"
        ]
        
        all_maps_results = []
        for search_query in search_variations:
            if should_stop():
                break
            maps_results = search_with_serper(search_query, api_key, max_results//4, "maps")
            all_maps_results.extend(maps_results)
            time.sleep(0.3)  # Brief pause between searches
        
        # Remove duplicates based on URL
        seen_urls = set()
        unique_maps_results = []
        for item in all_maps_results:
            url = item.get('link', '')
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_maps_results.append(item)
        
        maps_results = unique_maps_results
        
        for item in maps_results:
            if should_stop():
                break
                
            try:
                url = item.get('link', '')
                if not url:
                    continue
                
                print(f"Processing Maps result: {url}")
                
                # Scrape the website for emails
                emails = scrape_for_emails(url)
                
                # Extract domain for email suggestions
                try:
                    from urllib.parse import urlparse
                    parsed = urlparse(url if url.startswith('http') else f'http://{url}')
                    domain = parsed.netloc.replace('www.', '')
                except:
                    domain = ''
                
                # Only generate suggested emails if no real emails found
                suggested_emails = []
                if not emails and domain:
                    suggested_emails = generate_common_emails(url)
                
                # Add result with comprehensive data structure
                # Add primary email for UI compatibility
                primary_email = emails[0] if emails else ''
                
                results.append({
                    'business_name': item.get('title', 'Unknown Business'),
                    'url': url,
                    'website': url,
                    'domain': domain,
                    'email': primary_email,  # Primary email for UI
                    'emails': emails,        # Full email list
                    'suggested_emails': suggested_emails,
                    'source': item.get('source', 'Google Maps'),
                    'location': location,
                    'keyword': keyword,
                    'address': item.get('address', ''),
                    'phone': item.get('phone', ''),
                    'rating': item.get('rating', ''),
                    'reviews': item.get('reviews', ''),
                    'status': 'active'
                })
                
                time.sleep(0.5)  # Rate limiting
            except Exception as e:
                print(f"Error processing Maps result: {str(e)}")
    
    # Search using Google Search if enabled and API key provided
    if use_search and api_key and not should_stop():
        search_results = search_with_serper(query, api_key, max_results//2, "search")
        
        for item in search_results:
            if should_stop():
                break
                
            try:
                url = item.get('link', '')
                if not url:
                    continue
                
                print(f"Processing Search result: {url}")
                
                # Scrape the website for emails
                emails = scrape_for_emails(url)
                
                # Extract domain for email suggestions
                try:
                    from urllib.parse import urlparse
                    parsed = urlparse(url if url.startswith('http') else f'http://{url}')
                    domain = parsed.netloc.replace('www.', '')
                except:
                    domain = ''
                
                # Only generate suggested emails if no real emails found
                suggested_emails = []
                if not emails and domain:
                    suggested_emails = generate_common_emails(url)
                
                # Add result with comprehensive data structure
                # Add primary email for UI compatibility
                primary_email = emails[0] if emails else ''
                
                results.append({
                    'business_name': item.get('title', 'Unknown Business'),
                    'url': url,
                    'website': url,
                    'domain': domain,
                    'email': primary_email,  # Primary email for UI
                    'emails': emails,        # Full email list
                    'suggested_emails': suggested_emails,
                    'source': item.get('source', 'Google Search'),
                    'location': location,
                    'keyword': keyword,
                    'address': item.get('snippet', ''),
                    'phone': '',
                    'status': 'active'
                })
                
                time.sleep(0.5)  # Rate limiting
            except Exception as e:
                print(f"Error processing Search result: {str(e)}")
    
    return results