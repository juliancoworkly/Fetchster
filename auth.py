"""
Authentication module for Email Scraper SaaS
Handles user registration, login, and subscription management using PostgreSQL
"""

import streamlit as st
import os
import psycopg2
import psycopg2.extras
from datetime import datetime, timedelta
import hashlib
import secrets
from cryptography.fernet import Fernet
import base64
import json

# Initialize PostgreSQL connection
def init_database():
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        st.error("Database connection not found.")
        return None
    try:
        conn = psycopg2.connect(database_url)
        conn.autocommit = True
        create_admin_account_if_needed(conn)
        return conn
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return None

def create_admin_account_if_needed(conn):
    """Create admin accounts with lifetime access if they don't exist"""
    try:
        cursor = conn.cursor()
        
        # Admin accounts to create
        admin_accounts = [
            {
                "email": "admin@fetchster.io",
                "password": "*F7940531r!?!*",
                "name": "Fetchster Admin"
            },
            {
                "email": "henry@team-coworkly.com",
                "password": "julianisawesome",
                "name": "Henry Admin"
            }
        ]
        
        for admin in admin_accounts:
            # Check if admin account exists
            cursor.execute("SELECT id FROM user_profiles WHERE email = %s", (admin["email"],))
            if cursor.fetchone():
                continue
            
            # Create admin account with hashed password
            password_hash = hashlib.sha256(admin["password"].encode()).hexdigest()
            
            cursor.execute("""
                INSERT INTO user_profiles (email, password_hash, full_name, subscription_type, 
                                         searches_remaining, total_searches)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                admin["email"],
                password_hash,
                admin["name"],
                "lifetime",  # Lifetime access
                999999,  # Unlimited searches
                0  # Starting search count
            ))
            
            print(f"Admin account created successfully: {admin['email']}")
        
        cursor.close()
        
    except Exception as e:
        print(f"Failed to create admin accounts: {e}")

def get_encryption_key():
    """Generate or retrieve encryption key for API keys"""
    return base64.urlsafe_b64encode(b'encryption_key_32_bytes_long_12')[:32]

def encrypt_api_key(api_key: str, user_id: str) -> str:
    """Encrypt API key with user-specific encryption"""
    try:
        # Create user-specific encryption key
        user_salt = hashlib.sha256(f"{user_id}_salt".encode()).digest()
        key = base64.urlsafe_b64encode(user_salt[:32])
        f = Fernet(key)
        
        encrypted = f.encrypt(api_key.encode())
        return base64.urlsafe_b64encode(encrypted).decode()
    except Exception as e:
        st.error(f"Failed to encrypt API key: {str(e)}")
        return ""

def decrypt_api_key(encrypted_key: str, user_id: str) -> str:
    """Decrypt API key with user-specific decryption"""
    if not encrypted_key:
        return ""
    
    try:
        # Create user-specific decryption key
        user_salt = hashlib.sha256(f"{user_id}_salt".encode()).digest()
        key = base64.urlsafe_b64encode(user_salt[:32])
        f = Fernet(key)
        
        encrypted_data = base64.urlsafe_b64decode(encrypted_key.encode())
        decrypted = f.decrypt(encrypted_data)
        return decrypted.decode()
    except Exception as e:
        st.error(f"Failed to decrypt API key: {str(e)}")
        return ""

def save_user_api_key(api_key: str) -> bool:
    """Securely save user's Serper.dev API key"""
    if not is_authenticated():
        return False
    
    user_email = st.session_state.user_email
    
    try:
        conn = init_database()
        if not conn:
            return False
        
        cursor = conn.cursor()
        
        # Get user ID first
        cursor.execute("SELECT id FROM user_profiles WHERE email = %s", (user_email,))
        result = cursor.fetchone()
        
        if not result:
            cursor.close()
            return False
        
        user_id = result[0]
        
        # Encrypt the API key
        encrypted_key = encrypt_api_key(api_key, str(user_id))
        
        # Update user's API key
        cursor.execute(
            "UPDATE user_profiles SET api_key_encrypted = %s, updated_at = %s WHERE id = %s",
            (encrypted_key, datetime.now(), user_id)
        )
        conn.commit()
        cursor.close()
        return True
    except Exception as e:
        st.error(f"Failed to save API key: {e}")
        return False

def get_user_api_key() -> str:
    """Securely retrieve user's Serper.dev API key"""
    if not is_authenticated():
        return ""
    
    user_email = st.session_state.user_email
    
    try:
        conn = init_database()
        if not conn:
            return ""
        
        cursor = conn.cursor()
        cursor.execute("SELECT id, api_key_encrypted FROM user_profiles WHERE email = %s", (user_email,))
        result = cursor.fetchone()
        cursor.close()
        
        if not result or not result[1]:
            return ""
        
        user_id, encrypted_key = result
        return decrypt_api_key(encrypted_key, str(user_id))
    except Exception as e:
        st.error(f"Failed to retrieve API key: {e}")
        return ""

def save_user_keywords(keywords: list) -> bool:
    """Save user's custom keywords"""
    if not is_authenticated():
        return False
    
    user_email = st.session_state.user_email
    
    try:
        conn = init_database()
        if not conn:
            return False
        
        cursor = conn.cursor()
        
        # Get user ID
        cursor.execute("SELECT id FROM user_profiles WHERE email = %s", (user_email,))
        result = cursor.fetchone()
        
        if not result:
            cursor.close()
            return False
        
        user_id = result[0]
        
        # Clear existing keywords
        cursor.execute("DELETE FROM user_keywords WHERE user_id = %s AND is_recent = FALSE", (user_id,))
        
        # Insert new keywords
        for keyword in keywords:
            cursor.execute(
                "INSERT INTO user_keywords (user_id, keyword, is_recent) VALUES (%s, %s, %s)",
                (user_id, keyword, False)
            )
        
        conn.commit()
        cursor.close()
        return True
    except Exception as e:
        st.error(f"Failed to save keywords: {e}")
        return False

def get_user_keywords() -> list:
    """Get user's saved keywords"""
    if not is_authenticated():
        return []
    
    user_email = st.session_state.user_email
    
    try:
        conn = init_database()
        if not conn:
            return []
        
        cursor = conn.cursor()
        cursor.execute("""
            SELECT k.keyword FROM user_keywords k
            JOIN user_profiles u ON k.user_id = u.id
            WHERE u.email = %s AND k.is_recent = FALSE
            ORDER BY k.created_at DESC
        """, (user_email,))
        
        keywords = [row[0] for row in cursor.fetchall()]
        cursor.close()
        return keywords
    except Exception as e:
        st.error(f"Failed to retrieve keywords: {e}")
        return []

def save_recent_keyword(keyword: str) -> bool:
    """Save a recently used keyword for quick access"""
    if not is_authenticated():
        return False
    
    user_email = st.session_state.user_email
    
    try:
        conn = init_database()
        if not conn:
            return False
        
        cursor = conn.cursor()
        
        # Get user ID
        cursor.execute("SELECT id FROM user_profiles WHERE email = %s", (user_email,))
        result = cursor.fetchone()
        
        if not result:
            cursor.close()
            return False
        
        user_id = result[0]
        
        # Insert recent keyword (or update if exists)
        cursor.execute("""
            INSERT INTO user_keywords (user_id, keyword, is_recent) 
            VALUES (%s, %s, %s)
            ON CONFLICT (user_id, keyword) DO UPDATE SET created_at = CURRENT_TIMESTAMP
        """, (user_id, keyword, True))
        
        conn.commit()
        cursor.close()
        return True
    except Exception as e:
        st.error(f"Failed to save recent keyword: {e}")
        return False

def get_recent_keywords() -> list:
    """Get user's recently used keywords"""
    if not is_authenticated():
        return []
    
    user_email = st.session_state.user_email
    
    try:
        conn = init_database()
        if not conn:
            return []
        
        cursor = conn.cursor()
        cursor.execute("""
            SELECT k.keyword FROM user_keywords k
            JOIN user_profiles u ON k.user_id = u.id
            WHERE u.email = %s AND k.is_recent = TRUE
            ORDER BY k.created_at DESC
            LIMIT 5
        """, (user_email,))
        
        keywords = [row[0] for row in cursor.fetchall()]
        cursor.close()
        return keywords
    except Exception as e:
        st.error(f"Failed to retrieve recent keywords: {e}")
        return []

def register_user(email: str, password: str, full_name: str = ""):
    """Register a new user"""
    conn = None
    cursor = None
    try:
        conn = init_database()
        if not conn:
            return False, "Database connection failed"
        
        cursor = conn.cursor()
        
        # Check if user already exists
        cursor.execute("SELECT id FROM user_profiles WHERE email = %s", (email,))
        if cursor.fetchone():
            return False, "User already exists"
        
        # Hash password
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        # Insert new user
        cursor.execute("""
            INSERT INTO user_profiles (email, password_hash, full_name, subscription_type, searches_remaining)
            VALUES (%s, %s, %s, %s, %s)
        """, (email, password_hash, full_name, 'trial', 3))
        
        return True, "Registration successful"
    except Exception as e:
        return False, f"Registration failed: {e}"
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def login_user(email: str, password: str, remember_me: bool = False):
    """Login user with admin access support and remember me functionality"""
    conn = None
    cursor = None
    try:
        conn = init_database()
        if not conn:
            return False, "Database connection failed"
        
        cursor = conn.cursor()
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        cursor.execute("""
            SELECT id, email, full_name, subscription_type, searches_remaining, total_searches
            FROM user_profiles 
            WHERE email = %s AND password_hash = %s
        """, (email, password_hash))
        
        result = cursor.fetchone()
        
        if result:
            user_id = result[0]
            
            # Clear any existing session state first
            for key in ['authenticated', 'user_email', 'user_name', 'subscription_type', 'searches_remaining', 'total_searches', 'is_admin']:
                if key in st.session_state:
                    del st.session_state[key]
            
            # Set new session state
            st.session_state.authenticated = True
            st.session_state.user_email = result[1]
            st.session_state.user_name = result[2] or "User"
            st.session_state.subscription_type = result[3]
            st.session_state.searches_remaining = result[4]
            st.session_state.total_searches = result[5]
            
            # Check for admin access
            if email == "admin@fetchster.io":
                st.session_state.is_admin = True
            else:
                st.session_state.is_admin = False
            
            # Handle remember me functionality
            if remember_me:
                # Generate a secure login token
                login_token = generate_activation_key()
                
                # Save login token to database with 30-day expiry
                cursor.execute("""
                    UPDATE user_profiles 
                    SET login_token = %s, login_token_expires = CURRENT_TIMESTAMP + INTERVAL '30 days'
                    WHERE id = %s
                """, (login_token, user_id))
                conn.commit()
                
                # Store in session state for browser persistence
                st.session_state.remember_me = True
                st.session_state.saved_email = email
                st.session_state.login_token = login_token
            
            return True, "Login successful"
        else:
            return False, "Invalid credentials"
    except Exception as e:
        return False, f"Login failed: {e}"
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def logout_user():
    """Logout user"""
    for key in ['authenticated', 'user_email', 'user_name', 'subscription_type', 'searches_remaining', 'total_searches', 'is_admin']:
        if key in st.session_state:
            del st.session_state[key]

def check_auto_login():
    """Check for saved login credentials and auto-login if valid"""
    if st.session_state.get('authenticated', False):
        return  # Already logged in
    
    # Check for saved login token
    saved_email = st.session_state.get('saved_email')
    login_token = st.session_state.get('login_token')
    
    if not saved_email or not login_token:
        return  # No saved credentials
    
    conn = None
    cursor = None
    try:
        conn = init_database()
        if not conn:
            return
        
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, email, full_name, subscription_type, searches_remaining, total_searches
            FROM user_profiles 
            WHERE email = %s AND login_token = %s AND login_token_expires > CURRENT_TIMESTAMP
        """, (saved_email, login_token))
        
        result = cursor.fetchone()
        
        if result:
            # Auto-login successful
            st.session_state.authenticated = True
            st.session_state.user_email = result[1]
            st.session_state.user_name = result[2] or "User"
            st.session_state.subscription_type = result[3]
            st.session_state.searches_remaining = result[4]
            st.session_state.total_searches = result[5]
            
            # Check for admin access
            if saved_email == "admin@fetchster.io":
                st.session_state.is_admin = True
            else:
                st.session_state.is_admin = False
                
    except Exception as e:
        # Clear invalid saved credentials
        for key in ['saved_email', 'login_token', 'remember_me']:
            if key in st.session_state:
                del st.session_state[key]
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def is_authenticated():
    """Check if user is authenticated"""
    # First check for auto-login
    if not st.session_state.get('authenticated', False):
        check_auto_login()
    
    return st.session_state.get('authenticated', False)

def get_current_user():
    """Get current user info"""
    if not is_authenticated():
        return None
    
    return {
        'email': st.session_state.get('user_email'),
        'name': st.session_state.get('user_name'),
        'subscription_type': st.session_state.get('subscription_type'),
        'searches_remaining': st.session_state.get('searches_remaining'),
        'total_searches': st.session_state.get('total_searches')
    }

def get_user_profile():
    """Get current user profile"""
    return get_current_user()

def can_perform_search():
    """Check if user can perform a search based on subscription"""
    if not is_authenticated():
        return False, "Please log in to perform searches"
    
    subscription_type = st.session_state.get('subscription_type', 'trial')
    searches_remaining = st.session_state.get('searches_remaining', 0)
    
    if subscription_type in ['lifetime', 'monthly']:
        return True, "Search allowed"
    elif searches_remaining > 0:
        return True, f"Trial searches remaining: {searches_remaining}"
    else:
        return False, "No trial searches remaining. Please upgrade your account."

def update_search_count():
    """Update user's search count and trial remaining"""
    if not is_authenticated():
        return False
    
    user_email = st.session_state.user_email
    
    try:
        conn = init_database()
        if not conn:
            return False
        
        cursor = conn.cursor()
        
        # Update search counts
        cursor.execute("""
            UPDATE user_profiles 
            SET total_searches = total_searches + 1,
                searches_remaining = CASE 
                    WHEN subscription_type = 'trial' THEN GREATEST(searches_remaining - 1, 0)
                    ELSE searches_remaining
                END,
                updated_at = %s
            WHERE email = %s
        """, (datetime.now(), user_email))
        
        # Get updated counts
        cursor.execute("SELECT searches_remaining, total_searches FROM user_profiles WHERE email = %s", (user_email,))
        result = cursor.fetchone()
        
        if result:
            st.session_state.searches_remaining = result[0]
            st.session_state.total_searches = result[1]
        
        conn.commit()
        cursor.close()
        return True
    except Exception as e:
        st.error(f"Failed to update search count: {e}")
        return False

def save_search_history(keyword: str, location: str, results_count: int, results_data: list):
    """Save search to user's history"""
    if not is_authenticated():
        return False
    
    user_email = st.session_state.user_email
    
    try:
        conn = init_database()
        if not conn:
            return False
        
        cursor = conn.cursor()
        
        # Get user ID
        cursor.execute("SELECT id FROM user_profiles WHERE email = %s", (user_email,))
        result = cursor.fetchone()
        
        if not result:
            cursor.close()
            return False
        
        user_id = result[0]
        
        # Save search history
        cursor.execute("""
            INSERT INTO search_history (user_id, keyword, location, results_count, results_data)
            VALUES (%s, %s, %s, %s, %s)
        """, (user_id, keyword, location, results_count, json.dumps(results_data)))
        
        conn.commit()
        cursor.close()
        return True
    except Exception as e:
        st.error(f"Failed to save search history: {e}")
        return False

def get_user_search_history(limit: int = 10):
    """Get user's search history"""
    if not is_authenticated():
        return []
    
    user_email = st.session_state.user_email
    
    try:
        conn = init_database()
        if not conn:
            return []
        
        cursor = conn.cursor()
        cursor.execute("""
            SELECT h.keyword, h.location, h.results_count, h.created_at
            FROM search_history h
            JOIN user_profiles u ON h.user_id = u.id
            WHERE u.email = %s
            ORDER BY h.created_at DESC
            LIMIT %s
        """, (user_email, limit))
        
        history = []
        for row in cursor.fetchall():
            history.append({
                'keyword': row[0],
                'location': row[1],
                'results_count': row[2],
                'created_at': row[3]
            })
        
        cursor.close()
        return history
    except Exception as e:
        st.error(f"Failed to retrieve search history: {e}")
        return []

def generate_activation_key():
    """Generate a unique activation key"""
    return secrets.token_urlsafe(32)

def activate_subscription(activation_key: str, subscription_type: str = 'lifetime'):
    """Activate subscription with activation key"""
    conn = get_db_connection()
    if not conn:
        return False, "Database connection failed"
    
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # Check if activation key exists and is unused
        cursor.execute("""
            SELECT * FROM activation_keys 
            WHERE key = %s AND used = false
        """, (activation_key,))
        
        key_data = cursor.fetchone()
        if not key_data:
            return False, "Invalid or already used activation key"
        
        # Get current user
        user_id = st.session_state.get('user_id')
        if not user_id:
            return False, "User not found"
        
        # Update user subscription status
        if subscription_type == 'lifetime':
            cursor.execute("""
                UPDATE user_profiles 
                SET subscription_type = %s, subscription_expires_at = NULL
                WHERE user_id = %s
            """, (subscription_type, user_id))
        else:
            expires_at = datetime.now() + timedelta(days=30)
            cursor.execute("""
                UPDATE user_profiles 
                SET subscription_type = %s, subscription_expires_at = %s
                WHERE user_id = %s
            """, (subscription_type, expires_at, user_id))
        
        # Mark activation key as used
        cursor.execute("""
            UPDATE activation_keys 
            SET used = true, used_by = %s, used_at = %s
            WHERE key = %s
        """, (user_id, datetime.now(), activation_key))
        
        conn.commit()
        conn.close()
        
        # Update session state
        if 'user_profile' not in st.session_state:
            st.session_state.user_profile = {}
        st.session_state.user_profile['subscription_type'] = subscription_type
        
        return True, f"Subscription activated successfully! You now have {subscription_type} access."
        
    except Exception as e:
        if conn:
            conn.rollback()
            conn.close()
        return False, f"Activation failed: {str(e)}"

def create_activation_key(subscription_type: str = 'lifetime', customer_email: str = ""):
    """Create a new activation key (for admin use)"""
    # This would need to be implemented with activation key storage
    return generate_activation_key()

def reset_password(email: str):
    """Send password reset email"""
    # This would need to be implemented with email service
    return False, "Password reset functionality not yet implemented"