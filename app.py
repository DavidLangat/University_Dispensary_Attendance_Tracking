import datetime
from flask import Flask, render_template, request, redirect, session, flash, jsonify
from flask_bootstrap import Bootstrap
import mysql.connector

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Set your secret key for session management
bootstrap = Bootstrap(app)

db = mysql.connector.connect(
    host='localhost',
    user='root',
    password='',
    database='university_dispensary'
)
cursor = db.cursor()

# Create the students table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS students (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        student_id VARCHAR(20) UNIQUE NOT NULL,
        department VARCHAR(255) NOT NULL,
        email VARCHAR(255) NOT NULL,
        phone VARCHAR(20) NOT NULL
    )
''')

# Create the check_ins table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS check_ins (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        student_id VARCHAR(20) NOT NULL,
        reason VARCHAR(255) NOT NULL,
        check_in_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        check_out_time TIMESTAMP NULL DEFAULT NULL
    )
''')


@app.route('/')
def home():
    if 'username' in session:
        return redirect('/dashboard')
    return redirect('/login')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        student_id = request.form['student_id']
        department = request.form['department']
        email = request.form['email']
        phone = request.form['phone']

        cursor.execute('INSERT INTO students (name, student_id, department, email, phone) VALUES (%s, %s, %s, %s, %s)',
                       (name, student_id, department, email, phone))
        db.commit()

        flash('Registration successful!', 'success')
        return redirect('/register')

    return render_template('studentreg.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Retrieve username and password from the login form
        username = request.form['username']
        password = request.form['password']
        

        # Check if the user exists in the database
        cursor.execute(
            'SELECT * FROM users WHERE username = %s AND password = %s', (username, password))
        user = cursor.fetchone()

        if user:
            session['username'] = user[1]  # Store the username in the session
            return redirect('/dashboard')
        else:
            flash('Invalid username or password', 'error')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('username', None)  # Remove the username from the session
    return redirect('/login')

def get_total_visits():
    
    cursor.execute("SELECT COUNT(*) FROM check_ins")
    total_visits = cursor.fetchone()[0]
    return total_visits


def get_pending_checkouts():
    
    cursor.execute("SELECT COUNT(*) FROM check_ins WHERE check_out_time IS NULL")
    pending_checkouts = cursor.fetchone()[0]
    return pending_checkouts


def get_total_checkouts():
    
    cursor.execute("SELECT COUNT(*) FROM check_ins WHERE check_out_time IS NOT NULL")
    total_checkouts = cursor.fetchone()[0]
    return total_checkouts


def get_today_attendance():
    today = datetime.date.today()
    cursor.execute("SELECT COUNT(*) FROM check_ins WHERE DATE(check_in_time) = %s", (today,))
    today_attendance = cursor.fetchone()[0]
    return today_attendance



@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect('/login')

    # Retrieve check-in records for the dashboard
    cursor.execute(
        'SELECT * FROM check_ins ORDER BY check_in_time DESC LIMIT 10')
    records = cursor.fetchall()
    total_visits = get_total_visits()
    pending_checkouts = get_pending_checkouts()
    total_checkouts = get_total_checkouts()
    todays_attendance = get_today_attendance()

    return render_template('dashboard.html', total_visits=total_visits,
                           pending_checkouts=pending_checkouts,
                           total_checkouts=total_checkouts,
                           todays_attendance=todays_attendance, records=records)


@app.route('/check-in', methods=['GET'])
def check_in_form():
    if 'username' not in session:
        return redirect('/login')

    return render_template('form.html')


@app.route('/submit', methods=['POST'])
def submit():
    if 'username' not in session:
        return redirect('/login')

    name = request.form['name']
    student_id = request.form['student_id']
    reason = request.form['reason']

    # Check if the student exists
    cursor.execute('SELECT * FROM students WHERE student_id = %s', (student_id,))
    student = cursor.fetchone()

    if not student:
        flash('Student does not exist!', 'error')
        return redirect('/check-in')

    cursor.execute(
        'INSERT INTO check_ins (name, student_id, reason) VALUES (%s, %s, %s)', (name, student_id, reason))
    db.commit()

    flash('Check-in successful!', 'success')
    return redirect('/check-in')


@app.route('/check-out', methods=['GET'])
def check_out_form():
    if 'username' not in session:
        return redirect('/login')

    return render_template('checkout.html')


@app.route('/checkout', methods=['POST'])
def checkout():
    if 'username' not in session:
        return redirect('/login')

    student_id = request.form['student_id']

    cursor.execute(
        'UPDATE check_ins SET check_out_time = CURRENT_TIMESTAMP WHERE student_id = %s and check_out_time IS NULL', (student_id,))
    db.commit()
    affected_rows = cursor.rowcount

    if affected_rows == 0:
        flash('Checkout failed. Student not found or already checked out.', 'error')
    else:
        flash('Check-out successful!', 'success')

    return redirect('/check-out')


@app.route('/medical-records/<student_id>', methods=['GET'])
def medical_records(student_id):
    if 'username' not in session:
        return redirect('/login')

    cursor.execute(
        'SELECT * FROM check_ins WHERE student_id = %s', (student_id,))
    records = cursor.fetchall()

    return render_template('medical_records.html', records=records)

@app.route('/adminregister', methods=['GET', 'POST'])
def adminregister():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        cursor.execute('INSERT INTO users (username, password, role) VALUES (%s, %s, %s)', (username, password, role))
        db.commit()
        flash('Registration successful!', 'success')


    return render_template('register.html')
@app.route('/reports', methods=['GET'])
def reports():
    if 'username' not in session:
        return redirect('/login')

    # Retrieve all check-in records from the database
    cursor.execute('SELECT * FROM check_ins')
    records = cursor.fetchall()

    cursor.execute('SELECT * FROM users')
    records2 = cursor.fetchall()

    return render_template('reports.html', records=records, hello=records2)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.route('/get_student_name')
def get_student_name():
    student_id = request.args.get('student_id')

    query = "SELECT name FROM students WHERE student_id = %s"
    cursor.execute(query, (student_id,))
    result = cursor.fetchone()

    if result:
        student_name = result[0]

    else:
        student_name = 'Student Not Found'

    return jsonify({'name': student_name})


if __name__ == '__main__':
    app.run(debug=True)
