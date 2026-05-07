"""
Login page functionality - separated for clean code organization
"""
import streamlit as st
from auth import register_user, login_user, reset_password
from login_styles import get_login_styles

def show_auth_interface():
    """Display clean, modern login/registration interface"""
    
    # Apply login-specific styles
    st.markdown(get_login_styles(), unsafe_allow_html=True)
    
    # Center the login interface
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<h1 style='text-align: center; margin-bottom: 1rem;'>Fetchster</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; margin-bottom: 1rem; color: rgba(255,255,255,0.8); font-size: 1.2em;'>Professional Email Harvesting Tool</p>", unsafe_allow_html=True)
        
        # Enhanced description
        st.markdown("""
        <div style='text-align: center; margin-bottom: 2rem; color: rgba(255,255,255,0.7); line-height: 1.6;'>
            <p><strong>Find business emails efficiently using Google Maps and Search.</strong></p>
            <p>• Search by business type and location<br>
            • Extract emails from company websites<br>
            • Download results as CSV for immediate use<br>
            • Access search history and analytics</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Pricing information
        st.markdown("""
        <div style='text-align: center; margin-bottom: 2rem; padding: 1rem; background: rgba(255,255,255,0.1); border-radius: 8px; border-left: 4px solid #ff4444;'>
            <h3 style='color: #ff4444; margin-bottom: 0.5rem;'>Simple Pricing</h3>
            <p style='font-size: 1.5em; margin: 0; color: white;'><strong>$20 Annual Subscription</strong></p>
            <p style='color: rgba(255,255,255,0.8); margin: 0.5rem 0 0 0;'>All features included • Professional email harvesting</p>
        </div>
        """, unsafe_allow_html=True)
        
        # API requirement notice
        st.markdown("""
        <div style='text-align: center; margin-bottom: 2rem; padding: 1rem; background: rgba(255,165,0,0.1); border-radius: 8px; border-left: 4px solid #ffa500;'>
            <h4 style='color: #ffa500; margin-bottom: 0.5rem;'>Requirements</h4>
            <p style='color: rgba(255,255,255,0.8); margin: 0;'>You'll need a Serper.dev API account to use Fetchster</p>
            <p style='color: rgba(255,255,255,0.6); margin: 0.5rem 0 0 0; font-size: 0.9em;'>Sign up at serper.dev and add your API key after registration</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Login/Registration tabs
        tab1, tab2 = st.tabs(["Sign In", "Create Account"])
        
        with tab1:
            # Login form with proper Enter key handling
            with st.form(key="login_form", clear_on_submit=False):
                email = st.text_input("Email", placeholder="your@email.com")
                password = st.text_input("Password", type="password", placeholder="Enter your password")
                
                # Remember me checkbox
                remember_me = st.checkbox("Remember me for 30 days", help="Stay logged in on this device")
                
                # Submit button (Enter key will trigger this)
                col1, col2, col3 = st.columns([2, 1, 2])
                with col2:
                    login_button = st.form_submit_button("Sign In", use_container_width=True)
                
                # Handle form submission (triggered by Enter key or button click)
                if login_button:
                    if email and password:
                        try:
                            success, message = login_user(email, password, remember_me)
                            if success:
                                st.success("Welcome back!")
                                st.rerun()
                            else:
                                st.error(f"Login failed: {message}")
                        except Exception as e:
                            st.error(f"Login error: {str(e)}")
                    else:
                        st.warning("Please fill in all fields")
            
            # Forgot password - centered button
            st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("Forgot Password", key="forgot_password_btn"):
                    st.session_state.show_forgot_password = True
                    st.rerun()
            
            # Show forgot password form if requested
            if st.session_state.get('show_forgot_password', False):
                st.markdown("---")
                st.markdown("<h3 style='text-align: center;'>Reset Password</h3>", unsafe_allow_html=True)
                st.markdown("<p style='text-align: center; margin-bottom: 20px;'>Enter your email for password reset</p>", unsafe_allow_html=True)
                reset_email = st.text_input("", placeholder="your@email.com", label_visibility="collapsed")
                
                # Send and Cancel buttons centered
                col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 2])
                with col2:
                    if st.button("Send", key="send_reset", use_container_width=True):
                        if reset_email:
                            success, message = reset_password(reset_email)
                            if success:
                                st.success("Password reset email sent! Check your inbox.")
                                st.session_state.show_forgot_password = False
                                st.rerun()
                            else:
                                st.error(message)
                        else:
                            st.warning("Please enter your email address")
                
                with col4:
                    if st.button("Cancel", key="cancel_reset", use_container_width=True):
                        st.session_state.show_forgot_password = False
                        st.rerun()
        
        with tab2:
            # Registration form
            with st.form(key="modular_register_form", clear_on_submit=False):
                full_name = st.text_input("Full Name", placeholder="Your full name")
                reg_email = st.text_input("Email", placeholder="your@email.com", key="reg_email")
                reg_password = st.text_input("Password", type="password", placeholder="Create a secure password", key="reg_password")
                confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")
                
                # Terms of service checkbox
                st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
                terms_accepted = st.checkbox("I agree to the Terms of Service and Privacy Policy", key="terms_checkbox")
                
                col1, col2, col3 = st.columns([2, 1, 2])
                with col2:
                    reg_submitted = st.form_submit_button("Create Account", use_container_width=True)
                
                if reg_submitted:
                    if not terms_accepted:
                        st.error("Please accept the Terms of Service and Privacy Policy to continue.")
                    elif all([full_name, reg_email, reg_password, confirm_password]):
                        if reg_password == confirm_password:
                            success, message = register_user(reg_email, reg_password, full_name)
                            if success:
                                st.success("Account created successfully! Please sign in.")
                                st.rerun()
                            else:
                                st.error(message)
                        else:
                            st.error("Passwords do not match")
                    else:
                        st.warning("Please fill in all fields")
        
        # Legal footer with working links
        st.markdown("<div style='margin-top: 3rem;'></div>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if st.button("Terms of Service", key="terms_link"):
                st.session_state.show_terms = True
                st.rerun()
        
        with col2:
            if st.button("Privacy Policy", key="privacy_link"):
                st.session_state.show_privacy = True
                st.rerun()
        
        with col3:
            st.markdown("**Contact:** hello@fetchster.io")
        
        st.markdown("""
        <div style='text-align: center; padding: 1rem; border-top: 1px solid rgba(255,255,255,0.2); color: rgba(255,255,255,0.6); margin-top: 1rem;'>
            <p style='margin: 0; font-size: 0.9em;'>
                By using Fetchster, you agree to our terms and policies above
            </p>
        </div>
        """, unsafe_allow_html=True)