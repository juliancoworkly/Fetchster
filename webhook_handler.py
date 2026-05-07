"""
Stripe Webhook Handler for Fetchster
Handles payment confirmations and subscription updates
"""

import os
import json
import stripe
import psycopg2
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Initialize Stripe
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET")

@app.route('/stripe-webhook', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhook events"""
    payload = request.get_data()
    sig_header = request.headers.get('Stripe-Signature')
    
    try:
        # Verify webhook signature
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
        
        # Handle checkout session completed
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            
            if session.payment_status == 'paid':
                user_id = session.metadata.get('user_id')
                
                if user_id:
                    # Update user subscription in database
                    conn = psycopg2.connect(os.environ.get("DATABASE_URL"))
                    cur = conn.cursor()
                    
                    try:
                        cur.execute("""
                            UPDATE user_profiles 
                            SET subscription_status = 'active',
                                subscription_type = 'annual',
                                searches_remaining = 999999,
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
                        print(f"Subscription activated for user {user_id}")
                        
                    except Exception as e:
                        conn.rollback()
                        print(f"Database error: {str(e)}")
                        return jsonify({"error": str(e)}), 500
                    finally:
                        cur.close()
                        conn.close()
        
        # Handle subscription cancellation
        elif event['type'] == 'customer.subscription.deleted':
            subscription = event['data']['object']
            customer_id = subscription.customer
            
            conn = psycopg2.connect(os.environ.get("DATABASE_URL"))
            cur = conn.cursor()
            
            try:
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
                print(f"Subscription cancelled for customer {customer_id}")
                
            except Exception as e:
                conn.rollback()
                print(f"Database error: {str(e)}")
                return jsonify({"error": str(e)}), 500
            finally:
                cur.close()
                conn.close()
        
        return jsonify({"status": "success"}), 200
        
    except ValueError as e:
        print(f"Invalid payload: {str(e)}")
        return jsonify({"error": "Invalid payload"}), 400
    except stripe.error.SignatureVerificationError as e:
        print(f"Invalid signature: {str(e)}")
        return jsonify({"error": "Invalid signature"}), 400
    except Exception as e:
        print(f"Webhook error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False)
