def normalize(val):
    return str(val).strip().lower() if val else None

# Simulated user data from DB
users = [
    {"name": "Asees", "email": "Asees@gmail.com ", "phone": "7658016401 "}, # Whitespace in DB
    {"name": "Test", "email": "test@test.com", "phone": "+919999999999"}
]

# Simulated payment data from DB
# Note: In app.py, the map is built from orders
orders = [
    {"custom_id": "#ORDER001", "student_phone": " 7658016401", "student_email": "asees@GMAIL.com"},
    {"custom_id": "#ORDER002", "student_phone": "9999999999", "student_email": "test@test.com"}
]

# Build map in app.py (admin_dashboard)
user_latest_order = {}
for order in orders:
    norm_phone = normalize(order['student_phone'])
    if norm_phone and norm_phone not in user_latest_order:
        user_latest_order[norm_phone] = order['custom_id']
        
    norm_email = normalize(order['student_email'])
    if norm_email and norm_email not in user_latest_order:
        user_latest_order[norm_email] = order['custom_id']

# Test lookup in template
print("--- TESTING MAPPING ---")
for user in users:
    phone_lookup = user_latest_order.get(normalize(user['phone']))
    email_lookup = user_latest_order.get(normalize(user['email']))
    final_id = phone_lookup or email_lookup or '-'
    print(f"User: {user['name']}, Phone: '{user['phone']}', Derived Order ID: {final_id}")

assert user_latest_order.get(normalize("7658016401 ")) == "#ORDER001"
assert user_latest_order.get(normalize("Asees@GMAIL.com ")) == "#ORDER001"
print("\nSUCCESS: Normalization and Fallback works!")
