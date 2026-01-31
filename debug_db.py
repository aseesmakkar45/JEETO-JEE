from app import app, db, Payment
import uuid
from sqlalchemy import text

with app.app_context():
    print("--- DEBUG START ---")
    try:
        # Inspect actual DB
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        existing_tables = inspector.get_table_names()
        print("Existing tables in DB:", existing_tables)
        
        if 'payment' not in existing_tables:
            print("CRITICAL: 'payment' table MISSING from database file.")
            print("Attempting to create tables...")
            db.create_all()
            print("Tables created. Checking again:", inspect(db.engine).get_table_names())
        else:
            print("Payment table exists.")
            columns = [c['name'] for c in inspector.get_columns('payment')]
            print("Payment columns:", columns)
            
            # Check for custom_id column specifically
            if 'custom_id' not in columns:
                print("CRITICAL: 'custom_id' column MISSING from payment table.")
        
        # Try test insert
        print("Attempting test insert...")
        temp_id = str(uuid.uuid4())
        p = Payment(custom_id=temp_id)
        db.session.add(p)
        db.session.commit()
        print(f"Successfully created payment with ID {p.id}")
        
        # Try update
        p.custom_id = f"#DEBUG{p.id}"
        db.session.commit()
        print("Successfully updated custom_id")
        
    except Exception as e:
        print(f"EXCEPTION OCCURRED: {e}")
        import traceback
        traceback.print_exc()
    print("--- DEBUG END ---")
