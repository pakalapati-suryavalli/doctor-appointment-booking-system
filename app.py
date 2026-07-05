from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key_123'

def get_db():
    conn = sqlite3.connect('appointments.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']

        conn = get_db()
        try:
            conn.execute('INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)',
                         (name, email, password, role))
            conn.commit()
            conn.close()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            conn.close()
            return "Email already exists! <a href='/signup'>Try again</a>"

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db()
        user = conn.execute('SELECT * FROM users WHERE email = ? AND password = ?', (email, password)).fetchone()
        conn.close()

        if user:
            session['user_id'] = user['id']
            session['name'] = user['name']
            session['role'] = user['role']

            if user['role'] == 'doctor':
                return redirect(url_for('doctor_profile'))
            elif user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('patient_doctors'))
        else:
            return "Invalid email or password! <a href='/login'>Try again</a>"

    return render_template('login.html')

@app.route('/doctor/profile', methods=['GET', 'POST'])
def doctor_profile():
    if 'user_id' not in session or session['role'] != 'doctor':
        return redirect(url_for('login'))

    conn = get_db()

    if request.method == 'POST':
        specialization = request.form['specialization']
        experience = request.form['experience']
        fee = request.form['fee']

        existing = conn.execute('SELECT * FROM doctors WHERE user_id = ?', (session['user_id'],)).fetchone()

        if existing:
            conn.execute('UPDATE doctors SET specialization=?, experience=?, fee=? WHERE user_id=?',
                        (specialization, experience, fee, session['user_id']))
        else:
            conn.execute('INSERT INTO doctors (user_id, specialization, experience, fee) VALUES (?, ?, ?, ?)',
                        (session['user_id'], specialization, experience, fee))

        conn.commit()
        conn.close()
        return redirect(url_for('doctor_availability'))
    conn.close()
    return render_template('doctor_profile.html')
@app.route('/doctor/availability', methods=['GET', 'POST'])
def doctor_availability():
    if 'user_id' not in session or session['role'] != 'doctor':
        return redirect(url_for('login'))

    conn = get_db()
    doctor = conn.execute('SELECT * FROM doctors WHERE user_id = ?', (session['user_id'],)).fetchone()

    if not doctor:
        conn.close()
        return redirect(url_for('doctor_profile'))

    if request.method == 'POST':
        date = request.form['date']
        time_slot = request.form['time_slot']
        conn.execute('INSERT INTO availability (doctor_id, date, time_slot, is_booked) VALUES (?, ?, ?, 0)', (doctor['id'], date, time_slot))
        conn.commit()

    slots = conn.execute('SELECT * FROM availability WHERE doctor_id = ? ORDER BY date, time_slot', (doctor['id'],)).fetchall()
    conn.close()
    return render_template('doctor_availability.html', slots=slots)
@app.route('/patient/doctors')
def patient_doctors():
    conn = get_db()
    doctors = conn.execute('''
        SELECT doctors.id, users.name, doctors.specialization, doctors.experience, doctors.fee
        FROM doctors JOIN users ON doctors.user_id = users.id
    ''').fetchall()
    conn.close()
    return render_template('patient_doctors.html', doctors=doctors)
@app.route('/patient/book/<int:doctor_id>', methods=['GET', 'POST'])
def book_appointment(doctor_id):
    conn = get_db()

    if request.method == 'POST':
        slot_id = request.form['slot_id']
        problem = request.form['problem']
        patient_name = request.form['patient_name']
        patient_phone = request.form['patient_phone']

        count = conn.execute(
            'SELECT COUNT(*) as cnt FROM appointments WHERE slot_id = ? AND status != "cancelled"',
            (slot_id,)
        ).fetchone()['cnt']

        if count >= 20:
            conn.close()
            return "Ee slot full ayyindi (20 patients). Mari slot try cheyandi. <a href='/patient/book/{}'>Back</a>".format(doctor_id)

        token_number = count + 1

        conn.execute(
            '''INSERT INTO appointments 
               (doctor_id, slot_id, problem, token_number, patient_name, patient_phone, status)
               VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (doctor_id, slot_id, problem, token_number, patient_name, patient_phone, 'pending')
        )
        conn.commit()
        conn.close()
        return f"Appointment booked! Mee token number: {token_number}. <a href='/patient/doctors'>Back to doctors</a>"

    slots = conn.execute('SELECT * FROM availability WHERE doctor_id = ?', (doctor_id,)).fetchall()
    doctor = conn.execute(
        'SELECT users.name, doctors.specialization FROM doctors JOIN users ON doctors.user_id = users.id WHERE doctors.id = ?',
        (doctor_id,)
    ).fetchone()
    conn.close()
    return render_template('book_appointment.html', slots=slots, doctor=doctor, doctor_id=doctor_id)
@app.route('/patient/appointments')
def my_appointments():
    if 'user_id' not in session or session['role'] != 'patient':
        return redirect(url_for('login'))

    conn = get_db()
    appointments = conn.execute('SELECT appointments.status, users.name, doctors.specialization, availability.date, availability.time_slot FROM appointments JOIN doctors ON appointments.doctor_id = doctors.id JOIN users ON doctors.user_id = users.id JOIN availability ON appointments.slot_id = availability.id WHERE appointments.patient_id = ?', (session['user_id'],)).fetchall()
    conn.close()
    return render_template('my_appointments.html', appointments=appointments)
@app.route('/doctor/appointments')
def doctor_appointments():
    if 'user_id' not in session or session['role'] != 'doctor':
        return redirect(url_for('login'))

    conn = get_db()
    doctor = conn.execute('SELECT * FROM doctors WHERE user_id = ?', (session['user_id'],)).fetchone()
    appointments = conn.execute('''
        SELECT appointments.id, appointments.problem, appointments.status,
               appointments.patient_name, appointments.patient_phone,
               availability.date, availability.time_slot
        FROM appointments
        JOIN availability ON appointments.slot_id = availability.id
        WHERE appointments.doctor_id = ?
        ORDER BY availability.date, availability.time_slot, appointments.token_number
    ''', (doctor['id'],)).fetchall()
    conn.close()
    return render_template('doctor_appointments.html', appointments=appointments)

@app.route('/doctor/appointment/<int:appt_id>/<action>')
def update_appointment(appt_id, action):
    if 'user_id' not in session or session['role'] != 'doctor':
        return redirect(url_for('login'))

    conn = get_db()
    if action == 'approve':
        conn.execute('UPDATE appointments SET status = ? WHERE id = ?', ('confirmed', appt_id))
    elif action == 'cancel':
        conn.execute('UPDATE appointments SET status = ? WHERE id = ?', ('cancelled', appt_id))
    conn.commit()
    conn.close()
    return redirect(url_for('doctor_appointments'))

@app.route('/admin')
def admin_dashboard():
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))

    conn = get_db()
    users = conn.execute('SELECT * FROM users').fetchall()
    appointments = conn.execute('SELECT appointments.id, patients.name AS patient_name, doctors_users.name AS doctor_name, availability.date, availability.time_slot, appointments.status FROM appointments JOIN users AS patients ON appointments.patient_id = patients.id JOIN doctors ON appointments.doctor_id = doctors.id JOIN users AS doctors_users ON doctors.user_id = doctors_users.id JOIN availability ON appointments.slot_id = availability.id').fetchall()
    conn.close()
    return render_template('admin_dashboard.html', users=users, appointments=appointments)
@app.route('/admin/delete_user/<int:user_id>')
def delete_user(user_id):
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))

    conn = get_db()
    conn.execute('DELETE FROM doctors WHERE user_id = ?', (user_id,))
    conn.execute('DELETE FROM users WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_dashboard'))
@app.route('/patient/status', methods=['GET', 'POST'])
def check_status():
    appointments = None
    if request.method == 'POST':
        phone = request.form['patient_phone']
        conn = get_db()
        appointments = conn.execute('''
            SELECT appointments.id, appointments.token_number, appointments.problem, appointments.status,
                   appointments.patient_name, users.name as doctor_name,
                   availability.date, availability.time_slot
            FROM appointments
            JOIN doctors ON appointments.doctor_id = doctors.id
            JOIN users ON doctors.user_id = users.id
            JOIN availability ON appointments.slot_id = availability.id
            WHERE appointments.patient_phone = ?
            ORDER BY availability.date DESC
        ''', (phone,)).fetchall()
        conn.close()
    return render_template('check_status.html', appointments=appointments)
@app.route('/patient/appointment/<int:appt_id>/delete', methods=['POST'])
def delete_appointment(appt_id):
    conn = get_db()
    conn.execute('DELETE FROM appointments WHERE id = ?', (appt_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('check_status'))
if __name__ == '__main__':
    app.run(debug=True)