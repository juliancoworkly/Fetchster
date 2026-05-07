# Fetchster - Professional Email Harvesting Tool

## Overview

Fetchster is a SaaS application built with Streamlit that enables professional email discovery and lead generation. The platform searches business listings via Google Maps and Google Search APIs, then extracts contact information from company websites. It features user authentication, subscription management, and comprehensive search analytics.

**Current Pricing**: $20 annual subscription with all features included
**API Requirement**: Users must provide their own Serper.dev API key

## Recent Changes (June 27, 2025)

- **Advanced Options Last Results**: Added last search results display in Advanced Options with download and preview functionality
- **Persistent User Login**: Implemented "Remember me for 30 days" functionality to keep users logged in
- **Auto-Login System**: Users with saved credentials automatically log in without re-entering details
- **Database Schema Updates**: Added login_token and login_token_expires columns for secure session persistence
- **Search Limits Implementation**: Added intelligent search scope validation to prevent connection timeouts
- **Connection Timeout Prevention**: Implemented comprehensive timeout handling and batch processing
- **Smart Search Validation**: Maximum 20 total searches with clear warnings and recommendations
- **Performance Optimization**: Reduced API timeouts and improved batch processing for large searches
- **User Experience**: Clear error messages explaining why limits exist and how to optimize searches
- **Business Name Display Fixed**: Resolved issue where business names showed as "Unknown Business" in search history
- **Email Detection Enhanced**: Improved handling of multiple business name fields and domain email generation
- **Batch Processing**: Results processed in groups of 5 to prevent API overload
- **Error Handling**: Graceful handling of connection timeouts without stopping entire search

## Previous Changes (June 26, 2025)

- **Maps Search Completely Rebuilt**: Created centralized API engine with multiple search variations and endpoints for comprehensive business discovery
- **Email Extraction Enhanced**: Restored domain-based email guessing with comprehensive website scraping for real emails
- **CSV Export Improved**: Now includes both scraped emails AND suggested domain emails for maximum lead generation effectiveness
- **Search Variations Added**: System tries multiple keyword variations (coworking, shared office, workspace, etc.) for broader coverage
- **Comprehensive Email Detection**: Enhanced scraping finds mailto links, obfuscated emails, and contact elements on websites
- **Pricing Model Updated**: Changed from multiple tiers to simple $20 annual subscription
- **Fresh Search System**: Implemented new search engine (`fresh_search.py`) to resolve UI freezing issues
- **API Requirements**: Added clear documentation that users need Serper.dev API accounts
- **Login Enhancement**: Added pricing information, API requirements, and terms of service to login page
- **Pricing Page**: Created dedicated pricing page with FAQ section
- **Terms Update**: Updated terms of service to reflect annual subscription model
- **Code Cleanup**: Removed problematic old search implementations that caused progress bar resets
- **Stripe Integration Complete**: Full payment processing with PostgreSQL subscription management
- **Payment Verification**: Automatic subscription activation upon successful payment
- **Webhook Handler**: Created standalone webhook server for production deployment

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit web application
- **UI Components**: Modular interface components separated by functionality
- **Styling**: Custom CSS modules for consistent theming (dark theme with red accents)
- **State Management**: Streamlit session state for user interactions and search progress

### Backend Architecture
- **Application Server**: Streamlit app server running on port 5000
- **Database**: PostgreSQL for user management, authentication, and search history
- **Authentication**: Custom authentication system with encrypted password storage
- **API Integration**: Serper.dev API for Google Search and Maps data

### Data Storage Solutions
- **Primary Database**: PostgreSQL with psycopg2 driver
- **User Data**: Encrypted storage for sensitive information (API keys, passwords)
- **Search Results**: CSV export functionality with local file storage
- **Session Management**: Streamlit session state for temporary data

## Key Components

### Authentication System (`auth.py`)
- User registration and login with encrypted passwords
- API key management with user-specific encryption
- Subscription tracking and search quota management
- Session management and user profile handling

### Search Engine (`clean_searcher.py`, `fresh_search.py`)
- Google Maps and Google Search integration via Serper.dev API
- Website content extraction using BeautifulSoup
- Email pattern recognition and validation
- Duplicate removal and result optimization
- **Fresh Search Implementation**: New simplified search system to prevent UI freezing
- Minimal UI interference during search execution

### User Interface Modules
- **Login Interface** (`login_page.py`, `login_styles.py`): Authentication forms with modern styling
- **Keywords Module** (`keywords_module.py`): Keyword management and suggestions
- **Location Module** (`location_module.py`, `location_ui_components.py`): Geographic search targeting
- **Search Options** (`search_options_module.py`): API configuration and search parameters
- **Progress Tracking** (`progress_module.py`): Search progress monitoring and history

### Payment System (`payments.py`)
- Stripe integration for subscription management
- Annual subscription model: $20/year for all features
- 30-day money-back guarantee
- One-time payment processing and subscription tracking

## Data Flow

1. **User Authentication**: Login/registration through PostgreSQL-backed auth system
2. **Search Configuration**: Users set keywords, locations, and search parameters
3. **API Requests**: System calls Serper.dev API for business listings
4. **Content Extraction**: Scraped websites analyzed for email addresses
5. **Result Processing**: Emails validated, deduplicated, and formatted
6. **Data Export**: Results available as CSV downloads
7. **History Tracking**: Search history saved to database for analytics

## External Dependencies

### APIs and Services
- **Serper.dev**: Primary search API for Google Maps and Search results
- **Stripe**: Payment processing and subscription management
- **PostgreSQL**: Database hosting (configured via DATABASE_URL)

### Python Libraries
- **Streamlit**: Web application framework
- **psycopg2-binary**: PostgreSQL database driver
- **beautifulsoup4**: HTML parsing and content extraction
- **requests**: HTTP client for web scraping
- **pandas**: Data manipulation and CSV export
- **cryptography**: Encryption for sensitive data storage
- **stripe**: Payment processing integration

## Deployment Strategy

### Replit Configuration
- **Runtime**: Python 3.11 with PostgreSQL 16
- **Port Configuration**: Application runs on port 5000, exposed as port 80
- **Process Management**: Streamlit server with auto-restart capabilities
- **Environment**: Configured for autoscale deployment target

### Environment Variables Required
- `DATABASE_URL`: PostgreSQL connection string
- `STRIPE_SECRET_KEY`: Stripe payment processing
- `STRIPE_PUBLISHABLE_KEY`: Stripe client-side integration
- User API keys stored encrypted in database

### File Structure
- Modular architecture with separated concerns
- CSS styles isolated in dedicated modules
- Search functionality abstracted into specialized classes
- Location data maintained in comprehensive geographic database

## Changelog

```
Changelog:
- June 26, 2025. Initial setup
```

## User Preferences

```
Preferred communication style: Simple, everyday language.
```