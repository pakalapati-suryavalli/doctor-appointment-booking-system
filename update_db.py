import sqlite3

conn = sqlite3.connect('appointments.db')
cursor = conn.cursor()

columns_to_add = [
    ("patient_name", "TEXT"),
    ("patient_phone", "TEXT"),
]

for col_name, col_type in columns_to_add:
    try:
        cursor.execute(f"ALTER TABLE appointments ADD COLUMN {col_name} {col_type}")
        print(f"Added column: {col_name}")
    except sqlite3.OperationalError as e:
        print(f"Skipped {col_name}: {e}")

conn.commit()
conn.close()
print("Done! Database updated.")