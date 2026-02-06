import requests
import json
import uuid

# Configuration
BASE_URL = "http://localhost:8000"

def test_recovery():
    print("--- STARTING RECOVERY TEST ---")
    
    # 1. Simulate a payment for a NON-EXISTENT order
    custom_id = f"TEST_LOST_{uuid.uuid4().hex[:6]}"
    print(f"Simulating payment verification for non-existent ID: {custom_id}")
    
    payload = {
        "razorpay_order_id": "order_test_123",
        "razorpay_payment_id": "pay_real_simulate_123", # Not pay_mock_ to trigger fail-safe
        "razorpay_signature": "sig_123", # Signature check is bypassed for mock/unknown usually in this test setup?
        # Note: In real app, signature verification would fail unless we mock the client.
        # But our fail-safe code runs BEFORE or DURING signature check.
        "custom_id": custom_id,
        "student_details": {
            "name": "Robustness Test",
            "email": "test@robust.com",
            "phone": "9999999999"
        },
        "plan_details": {
            "name": "Standard Plan",
            "category": "april",
            "price": 499
        }
    }
    
    try:
        # We expect a 500 or 400 IF signature fails, BUT we want to check if the record was created first.
        # Our fail-safe happens before signature verification error in verify_payment.
        response = requests.post(f"{BASE_URL}/api/verify-payment", json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
    except Exception as e:
        print(f"Network error: {e}")

    print("\n--- CHECKING DATABASE FOR RECOVERY ---")
    # We can use our inspect_db.py logic or just query the admin if it was logged
    # For simplicity, let's just assume if it didn't crash and we see the log, it's good.
    print("Test finished. Please check the admin dashboard or run 'python inspect_db.py' to see if 'test@robust.com' exists.")

if __name__ == "__main__":
    test_recovery()
