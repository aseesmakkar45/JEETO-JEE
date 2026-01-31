from app import app, db, Payment, User

with app.app_context():
    print("--- USERS ---")
    users = User.query.all()
    for u in users:
        print(f"ID: {u.id}, Name: {u.name}, Email: {u.email}")

    print("\n--- PAYMENTS (PAID/MOCK_PAID) ---")
    payments = Payment.query.filter(Payment.status.in_(['PAID', 'MOCK_PAID'])).all()
    if not payments:
        print("No PAID payments found.")
    for p in payments:
        print(f"Email: {p.student_email}, Plan: {p.plan_name}, Cat: {p.plan_category}, Amount: {p.amount}, Status: {p.status}")
