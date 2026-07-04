import sqlite3

def init_db():
    conn = sqlite3.connect('appointments.db')
    cursor = conn.cursor()

    # Users table (patients, doctors, admin)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL
    )
    ''')

    # Doctors table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS doctors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        specialization TEXT,
        experience INTEGER,
        fee INTEGER,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    ''')

    # Availability table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS availability (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        doctor_id INTEGER,
        date TEXT,
        time_slot TEXT,
        is_booked INTEGER DEFAULT 0,
        FOREIGN KEY (doctor_id) REFERENCES doctors(id)
    )
    ''')

    # Appointments table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS appointments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER,
        doctor_id INTEGER,
        slot_id INTEGER,
        status TEXT DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (patient_id) REFERENCES users(id),
        FOREIGN KEY (doctor_id) REFERENCES doctors(id),
        FOREIGN KEY (slot_id) REFERENCES availability(id)
    )
    ''')

    conn.commit()
    conn.close()
    print("Database created successfully!")

if __name__ == '__main__':
    init_db()