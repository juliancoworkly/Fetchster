"""
Stripe payment integration for Email Scraper SaaS
Handles subscriptions, one-time payments, and billing management
"""

import os
import stripe
import streamlit as st
from datetime import datetime, timedelta
from auth import get_user_profile, get_current_user
from supabase import create_client

# Initialize Stripe
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
STRIPE_PUBLISHABLE_KEY = os.environ.get("STRIPE_PUBLISHABLE_KEY")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET")
ANNUAL_PRICE_ID = "price_1RTdKxQszO6ybCSk2aytrX1n"  # $20 annual subscription

# Initialize Supabase
@st.cache_resource
def init_supabase():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    return create_client(url, key)

def create_stripe_customer(user_email, user_name=""):
    """Create a Stripe customer for the user"""
    try:
        customer = stripe.Customer.create(
            email=user_email,
            name=user_name,
            metadata={
                'source': 'email_scraper_saas',
                'user_id': get_current_user().id if get_current_user() else ''
            }
        )
        return customer
    except Exception as e:
        st.error(f"Failed to create customer: {str(e)}")
        return None

def create_checkout_session():
    """Create a Stripe checkout session for $20 annual subscription"""
    profile = get_user_profile()
    if not profile:
        return None
    
    try:
        # Create checkout session for $20 annual subscription using Stripe price ID
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': ANNUAL_PRICE_ID,
                'quantity': 1
            }],
            mode='subscription',
            success_url=f"{os.environ.get('REPLIT_DOMAINS', 'http://localhost:5000')}?payment=success&session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{os.environ.get('REPLIT_DOMAINS', 'http://localhost:5000')}?payment=cancelled",
            customer_email=profile.get('email'),
            metadata={
                'user_id': profile.get('id'),
                'subscription_type': 'annual',
                'plan': 'professional'
            }
        )
        
        return session
        
    except Exception as e:
        st.error(f"Failed to create checkout session: {str(e)}")
        return None

def create_billing_portal_session():
    """Create a billing portal session for subscription management"""
    profile = get_user_profile()
    if not profile:
        return None
    
    try:
        # First, find the customer by email
        customers = stripe.Customer.list(email=profile.get('email'), limit=1)
        
        if not customers.data:
            st.error("No billing account found. Please contact support.")
            return None
        
        customer = customers.data[0]
        
        # Create billing portal session
        session = stripe.billing_portal.Session.create(
            customer=customer.id,
            return_url=f"{st.secrets.get('app_url', 'http://localhost:5000')}"
        )
        
        return session
        
    except Exception as e:
        st.error(f"Failed to create billing portal: {str(e)}")
        return None

def verify_payment_and_upgrade_user(session_id):
    """Verify payment and upgrade user subscription"""
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        
        if session.payment_status == 'paid':
            user_id = session.metadata.get('user_id')
            
            if user_id:
                # Update user subscription directly in PostgreSQL
                import psycopg2
                conn = psycopg2.connect(os.environ.get("DATABASE_URL"))
                cur = conn.cursor()
                
                try:
                    # Update user subscription status
                    cur.execute("""
                        UPDATE user_profiles 
                        SET subscription_status = 'active',
                            subscription_activated_at = %s,
                            subscription_expires_at = %s,
                            stripe_customer_id = %s
                        WHERE id = %s
                    """, (
                        datetime.now(),
                        datetime.now() + timedelta(days=365),  # Annual subscription
                        session.customer,
                        user_id
                    ))
                    
                    conn.commit()
                    
                    # Update session state if it's the current user  
                    if 'user_profile' in st.session_state:
                        st.session_state.user_profile['subscription_status'] = 'active'
                        st.session_state.user_profile['subscription_activated_at'] = datetime.now().isoformat()
                        st.session_state.user_profile['subscription_expires_at'] = (datetime.now() + timedelta(days=365)).isoformat()
                    
                    return True
                    
                except Exception as e:
                    conn.rollback()
                    st.error(f"Database error: {str(e)}")
                    return False
                finally:
                    cur.close()
                    conn.close()
        
        return False
        
    except Exception as e:
        st.error(f"Payment verification failed: {str(e)}")
        return False

def show_pricing_cards():
    """Display single $20 annual subscription with Stripe integration"""
    st.markdown("### 💳 Professional Plan")
    
    # Center the single pricing card
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Professional Annual Plan
        st.markdown("""
        <div style="border: 2px solid #FF0000; border-radius: 20px; padding: 30px; text-align: center; background: rgba(255,0,0,0.1);">
            <h3 style="color: #FF0000; margin-bottom: 1rem;">Fetchster Professional</h3>
            <div style="margin-bottom: 1.5rem;">
                <span style="font-size: 3em; font-weight: bold; color: white;">$20</span>
                <span style="font-size: 1.2em; color: rgba(255,255,255,0.8);">/year</span>
            </div>
            <p style="margin-bottom: 1.5rem; font-size: 1.1em;"><strong>All features included</strong></p>
            <ul style="text-align: left; padding-left: 20px; margin-bottom: 1.5rem;">
                <li>Professional email harvesting tools</li>
                <li>Google Maps business lookup</li>
                <li>Google Search website scraping</li>
                <li>CSV export functionality</li>
                <li>Search history access</li>
                <li>Analytics dashboard</li>
                <li>Priority customer support</li>
                <li>Annual billing</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Subscribe - $20/year", key="annual_btn", use_container_width=True, type="primary"):
            session = create_checkout_session()
            if session:
                st.markdown(f"""
                <script>
                window.open('{session.url}', '_blank');
                </script>
                """, unsafe_allow_html=True)
                st.success("Redirecting to secure payment...")
                st.markdown(f"**[Click here if redirect doesn't work]({session.url})**")
        
        # API requirement notice
        st.markdown("---")
        st.markdown("""
        <div style='text-align: center; padding: 1rem; background: rgba(255,165,0,0.1); border-radius: 8px; border-left: 4px solid #ffa500; margin-top: 1rem;'>
            <h4 style='color: #ffa500; margin-bottom: 0.5rem;'>Requirements</h4>
            <p style='color: rgba(255,255,255,0.8); margin: 0;'>You'll need a Serper.dev API account to use Fetchster</p>
            <p style='color: rgba(255,255,255,0.6); margin: 0.5rem 0 0 0; font-size: 0.9em;'>Sign up at serper.dev and add your API key after subscribing</p>
        </div>
        """, unsafe_allow_html=True)

def show_subscription_management():
    """Display subscription management interface for $20 annual plan"""
    profile = get_user_profile()
    if not profile:
        return
    
    status = profile.get('subscription_status', 'trial')
    
    st.markdown("### 🔧 Subscription Management")
    
    if status == 'active':
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Current Plan:** Fetchster Professional ($20/year)")
            expires = profile.get('subscription_expires_at')
            if expires:
                try:
                    exp_date = datetime.fromisoformat(expires.replace('Z', '+00:00'))
                    st.markdown(f"**Next Billing:** {exp_date.strftime('%B %d, %Y')}")
                except:
                    st.markdown("**Next Billing:** Active")
            
            st.success("✅ Your subscription is active")
            
        with col2:
            if st.button("Manage Billing", use_container_width=True):
                portal_session = create_billing_portal_session()
                if portal_session:
                    st.markdown(f"**[Open Billing Portal]({portal_session.url})**")
    
    else:
        # Show upgrade option for trial users
        st.info("💡 Upgrade to Fetchster Professional for $20/year")
        if st.button("Subscribe Now", type="primary", use_container_width=True):
            # Show pricing cards
            show_pricing_cards()

def handle_payment_callback():
    """Handle payment success/failure callbacks"""
    # Check URL parameters for payment status
    query_params = st.query_params
    
    if 'payment' in query_params:
        payment_status = query_params['payment']
        
        if payment_status == 'success':
            session_id = query_params.get('session_id')
            
            if session_id:
                # Verify and process the payment
                if verify_payment_and_upgrade_user(session_id):
                    st.success("🎉 Payment successful! Your subscription has been activated.")
                    st.balloons()
                    st.info("Your account now has access to all Fetchster Professional features!")
                else:
                    st.warning("Payment received but there was an issue activating your subscription. Please contact support.")
            else:
                st.success("🎉 Payment successful! Your subscription should be activated shortly.")
            
            # Clear the query parameters
            if 'payment' in st.query_params:
                del st.query_params['payment']
            if 'session_id' in st.query_params:
                del st.query_params['session_id']
            
        elif payment_status == 'cancelled':
            st.warning("Payment was cancelled. You can try again anytime.")
            
            # Clear the query parameter
            if 'payment' in st.query_params:
                del st.query_params['payment']

def handle_stripe_webhook(payload, sig_header):
    """Handle Stripe webhook events"""
    try:
        # Verify webhook signature
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
        
        # Handle the event
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            
            # Process the successful payment
            if session.payment_status == 'paid':
                user_id = session.metadata.get('user_id')
                
                if user_id:
                    # Update user subscription in database
                    try:
                        import psycopg2
                        conn = psycopg2.connect(os.environ.get("DATABASE_URL"))
                        cur = conn.cursor()
                        
                        # Update user subscription status
                        cur.execute("""
                            UPDATE user_profiles 
                            SET subscription_status = 'active',
                                subscription_activated_at = %s,
                                subscription_expires_at = %s,
                                stripe_customer_id = %s
                            WHERE id = %s
                        """, (
                            datetime.now(),
                            datetime.now() + timedelta(days=365),  # Annual subscription
                            session.customer,
                            user_id
                        ))
                        
                        conn.commit()
                        cur.close()
                        conn.close()
                        
                        return {"status": "success"}
                        
                    except Exception as e:
                        print(f"Database error: {str(e)}")
                        return {"status": "error", "message": str(e)}
        
        elif event['type'] == 'customer.subscription.deleted':
            # Handle subscription cancellation
            subscription = event['data']['object']
            customer_id = subscription.customer
            
            try:
                import psycopg2
                conn = psycopg2.connect(os.environ.get("DATABASE_URL"))
                cur = conn.cursor()
                
                # Update user subscription status
                cur.execute("""
                    UPDATE user_profiles 
                    SET subscription_status = 'cancelled',
                        subscription_expires_at = %s
                    WHERE stripe_customer_id = %s
                """, (
                    datetime.now(),
                    customer_id
                ))
                
                conn.commit()
                cur.close()
                conn.close()
                
            except Exception as e:
                print(f"Database error: {str(e)}")
                return {"status": "error", "message": str(e)}
        
        return {"status": "success"}
        
    except ValueError as e:
        # Invalid payload
        return {"status": "error", "message": "Invalid payload"}
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return {"status": "error", "message": "Invalid signature"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def get_subscription_analytics():
    """Get subscription analytics for the user"""
    profile = get_user_profile()
    if not profile:
        return {}
    
    # Handle admin account gracefully
    if profile.get('id') == 'admin_fetchster':
        return {
            'monthly_searches': 0,
            'total_searches': 0,
            'subscription_status': 'lifetime',
            'trial_remaining': 999999
        }
    
    supabase = init_supabase()
    
    try:
        # Get search count this month
        current_month = datetime.now().strftime('%Y-%m')
        
        searches = supabase.table('search_history').select('*').eq('user_id', profile['id']).gte('created_at', f'{current_month}-01').execute()
        
        monthly_searches = len(searches.data) if searches.data else 0
        total_searches = profile.get('total_searches', 0)
        
        return {
            'monthly_searches': monthly_searches,
            'total_searches': total_searches,
            'subscription_status': profile.get('subscription_status'),
            'trial_remaining': profile.get('trial_searches_remaining', 0)
        }
        
    except Exception as e:
        # Return clean defaults instead of showing error messages
        return {
            'monthly_searches': 0,
            'total_searches': 0,
            'subscription_status': profile.get('subscription_status', 'trial'),
            'trial_remaining': profile.get('trial_searches_remaining', 10)
        }