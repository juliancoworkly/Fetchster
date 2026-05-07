"""
Login page functionality - separated for clean code organization
"""
import streamlit as st
from auth import register_user, login_user, reset_password
from login_styles import get_login_styles


def show_auth_interface():
    """Display the login and registration interface."""
    st.markdown(get_login_styles(), unsafe_allow_html=True)

    intro_col, auth_col = st.columns([0.95, 1.05], gap="large")

    with intro_col:
        st.markdown(
            """
            <div class="auth-hero">
                <p class="auth-kicker">Fetchster</p>
                <h1>Find business emails from local search results.</h1>
                <p class="auth-lede">
                    Search Google Maps and Google Search through Serper.dev, scan company
                    websites, and export verified leads to CSV.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div class="auth-facts">
                <div>
                    <strong>$20/year</strong>
                    <span>All features included</span>
                </div>
                <div>
                    <strong>Serper.dev key required</strong>
                    <span>Users bring their own API key</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <ul class="auth-benefits">
                <li>Search by business type and location</li>
                <li>Extract contact emails from company websites</li>
                <li>Review search history and download CSV exports</li>
            </ul>
            """,
            unsafe_allow_html=True,
        )

    with auth_col:
        st.markdown('<div class="auth-panel-title">Account Access</div>', unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["Sign In", "Create Account"])

        with tab1:
            with st.form(key="login_form", clear_on_submit=False):
                email = st.text_input("Email", placeholder="your@email.com")
                password = st.text_input("Password", type="password", placeholder="Enter your password")
                remember_me = st.checkbox("Remember me for 30 days", help="Stay logged in on this device")

                login_button = st.form_submit_button("Sign In", use_container_width=True)

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

            if st.button("Forgot Password", key="forgot_password_btn", use_container_width=True):
                st.session_state.show_forgot_password = True
                st.rerun()

            if st.session_state.get("show_forgot_password", False):
                st.markdown("### Reset Password")
                st.caption("Enter your email for password reset.")
                reset_email = st.text_input("Reset email", placeholder="your@email.com", label_visibility="collapsed")

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Send", key="send_reset", use_container_width=True):
                        if reset_email:
                            success, message = reset_password(reset_email)
                            if success:
                                st.success("Password reset email sent. Check your inbox.")
                                st.session_state.show_forgot_password = False
                                st.rerun()
                            else:
                                st.error(message)
                        else:
                            st.warning("Please enter your email address")

                with col2:
                    if st.button("Cancel", key="cancel_reset", use_container_width=True):
                        st.session_state.show_forgot_password = False
                        st.rerun()

        with tab2:
            with st.form(key="modular_register_form", clear_on_submit=False):
                full_name = st.text_input("Full Name", placeholder="Your full name")
                reg_email = st.text_input("Email", placeholder="your@email.com", key="reg_email")
                reg_password = st.text_input("Password", type="password", placeholder="Create a secure password", key="reg_password")
                confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")
                terms_accepted = st.checkbox("I agree to the Terms of Service and Privacy Policy", key="terms_checkbox")

                reg_submitted = st.form_submit_button("Create Account", use_container_width=True)

                if reg_submitted:
                    if not terms_accepted:
                        st.error("Please accept the Terms of Service and Privacy Policy to continue.")
                    elif all([full_name, reg_email, reg_password, confirm_password]):
                        if reg_password == confirm_password:
                            success, message = register_user(reg_email, reg_password, full_name)
                            if success:
                                st.success("Account created successfully. Please sign in.")
                                st.rerun()
                            else:
                                st.error(message)
                        else:
                            st.error("Passwords do not match")
                    else:
                        st.warning("Please fill in all fields")

    st.markdown('<div class="auth-footer">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 2])

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

    st.markdown("</div>", unsafe_allow_html=True)
