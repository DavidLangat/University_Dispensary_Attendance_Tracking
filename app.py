import datetime
from flask import Flask, render_template, request, redirect, session, flash, jsonify
from flask_bootstrap import Bootstrap
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector

# Create the Flask app and set a secret key for session management
app = Flask(__name__)
app.secret_key = 'your_secret_key' 
bootstrap = Bootstrap(app)

# Establish a connection to the MySQL database
db = mysql.connector.connect(
    host='localhost',
    user='root',
    password='',
    database='university_dispensary'
)
cursor = db.cursor()

# function to generate hashed passwords
def generate_hashed_password(password):
    return generate_password_hash(password)

# function to check if the password matches the hashed password
def check_password(plain_password, hashed_password):
    return check_password_hash(hashed_password, plain_password)



# Route to handle the home page
@app.route('/')
def home():
    if 'username' in session:
        return redirect('/dashboard')
    return redirect('/login')


# Route to handle student registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        student_id = request.form['student_id']
        department = request.form['department']
        email = request.form['email']
        phone = request.form['phone']
        cursor.execute('INSERT INTO students (name, student_id, department, email, phone) VALUES (%s, %s, %s, %s, %s)',(name, student_id, department, email, phone))
        db.commit()
        flash('Registration successful!', 'success')
        return redirect('/register')
    return render_template('studentreg.html')



# Route to handle user login
@app.route('/login', methods=['GET', 'POST'])
def login():
        if request.method == 'POST':
     # Retrieve username and password from the login form
            username = request.form['username']
            password = request.form['password'] 
            test = check_password(password, 'hashed_password')
            password1 = generate_hashed_password(password)
             
             # Check if the user exists in the database
            cursor.execute(
            'SELECT * FROM users WHERE username = %s ', (username,))
            user = cursor.fetchone()
     
            if user:
                test = check_password(password, user[2])
                session['username'] = user[1] 
            if test:
                return redirect('/dashboard')
            else:
                flash('Check your username or Password', 'error')
        else:
            flash('Check your username or Password', 'error')
        return render_template('login.html')

# Route to handle user logout
@app.route('/logout')
def logout():
    session.pop('username', None)  # Remove the username from the session
    return redirect('/login')


# function to get the total number of visits to the dispensary
def get_total_visits():
    
    cursor.execute("SELECT COUNT(*) FROM check_ins")
    total_visits = cursor.fetchone()[0]
    return total_visits

# function to get the number of pending checkouts (students who have checked in but not checked out)
def get_pending_checkouts():
    
    cursor.execute("SELECT COUNT(*) FROM check_ins WHERE check_out_time IS NULL")
    pending_checkouts = cursor.fetchone()[0]
    return pending_checkouts

# function to get the total number of checkouts (students who have checked in and checked out)
def get_total_checkouts():
    
    cursor.execute("SELECT COUNT(*) FROM check_ins WHERE check_out_time IS NOT NULL")
    total_checkouts = cursor.fetchone()[0]
    return total_checkouts


# function to get the number of students who checked in on the current day
def get_today_attendance():
    today = datetime.date.today()
    cursor.execute("SELECT COUNT(*) FROM check_ins WHERE DATE(check_in_time) = %s", (today,))
    today_attendance = cursor.fetchone()[0]
    return today_attendance

# Route to display the dashboard
@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect('/login')

    # Retrieve check-in records for the dashboard
    cursor.execute(
        'SELECT students.name,check_ins.student_id, check_ins.reason, check_ins.check_in_time, check_ins.check_out_time FROM check_ins JOIN students ON check_ins.student_id = students.student_id ORDER BY check_in_time DESC LIMIT 10')
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

# Route to handle admin registration
@app.route('/adminregister', methods=['GET', 'POST'])
def adminregister():
    if request.method == 'POST':
        username = request.form['username']
        password1 = request.form['password']
        password = generate_hashed_password(password1)
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
    cursor.execute('SELECT students.name,check_ins.student_id, check_ins.reason, check_ins.check_in_time, check_ins.check_out_time FROM check_ins JOIN students ON check_ins.student_id = students.student_id ORDER BY check_in_time DESC LIMIT 10')
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





# Route to display the admin edit form
@app.route('/edit-admin/<int:admin_id>', methods=['GET', 'POST'])
def edit_admin(admin_id):
    if 'username' not in session:
        return redirect('/login')

    # Fetch the admin data by ID
    cursor.execute('SELECT * FROM users WHERE id = %s', (admin_id,))
    admin = cursor.fetchone()

    if request.method == 'POST':
        # Get the updated data from the form
        username = request.form['username']
        role = request.form['role']

        # Update the admin data in the database
        cursor.execute('UPDATE users SET username = %s, role = %s WHERE id = %s',
                       (username, role, admin_id))
        db.commit()

        flash('Admin updated successfully!', 'success')
        return redirect('/view-members')

    return render_template('edit_admin.html', admin=admin)

@app.route('/delete-admin/<int:admin_id>', methods=['POST'])
def delete_admin(admin_id):
    if 'username' not in session:
        return redirect('/login')

    # Delete the admin from the database
    cursor.execute('DELETE FROM users WHERE id = %s', (admin_id,))
    db.commit()

    flash('Admin deleted successfully!', 'success')
    return redirect('/view-members')

@app.route('/view-members')
def view_members():
    if 'username' not in session:
        return redirect('/login')

    # Fetch all student members
    cursor.execute('SELECT * FROM students')
    students = cursor.fetchall()

    # Fetch all admin members
    cursor.execute('SELECT * FROM users')
    admins = cursor.fetchall()
    
    

    return render_template('view_members.html', students=students, admins=admins)

@app.route('/edit-student/<int:student_id>', methods=['GET', 'POST'])
def edit_student(student_id):
    if 'username' not in session:
        return redirect('/login')

    # Fetch the student data by ID
    cursor.execute('SELECT * FROM students WHERE id = %s', (student_id,))
    student = cursor.fetchone()

    if request.method == 'POST':
        # Get the updated data from the form
       # NAME	STUDENT ID	DEPARTMENT	EMAIL	MOBILE NUMBER 
        name = request.form['name']
        student_id = request.form['student_id']
        department = request.form['department']
        email = request.form['email']
        phone = request.form['phone']

        # Update the student data in the database
        cursor.execute('UPDATE students SET name = %s, student_id = %s, department = %s, email = %s, phone = %s WHERE student_id = %s',
                       (name, student_id, department, email, phone, student_id))
        db.commit()
        flash('Student updated successfully!', 'success')
        return redirect('/view-members')

    return render_template('edit_student.html', student=student)

@app.route('/delete-student/<int:student_id>', methods=['POST'])
def delete_student(student_id):
    if 'username' not in session:
        return redirect('/login')

    # Delete the student from the database
    cursor.execute('DELETE FROM students WHERE id = %s', (student_id,))
    db.commit()

    flash('Student deleted successfully!', 'success')
    return redirect('/view-members')

# Route to display the admin profile details
@app.route('/profile')
def profile():
    if 'username' not in session:
        return redirect('/login')

    # Get the admin's profile details
    cursor.execute('SELECT * FROM users WHERE username = %s', [session['username']])
    admin = cursor.fetchone()

    return render_template('profile.html', admin=admin)
# Route to handle admin password change
@app.route('/change-password', methods=['GET', 'POST'])
def change_password():
    if 'username' not in session:
        return redirect('/login')


    if request.method == 'POST':
        # Get the form data
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        # Check if the current password is correct
        cursor.execute('SELECT * FROM users WHERE username = %s', (session['username'],))
        user = cursor.fetchone()

        if not check_password_hash(user[2], current_password):
            flash('Current password is incorrect', 'danger')
            return redirect('/change-password')

        if new_password != confirm_password:
            flash('New password and confirm password do not match', 'danger')
            return redirect('/change-password')

        # If the current password is correct and new password matches confirm password, update the password in the database
        cursor.execute('UPDATE users SET password = %s WHERE username = %s',
                    (generate_password_hash(new_password), session['username']))
        db.commit()
      

        flash('Password changed successfully!', 'success')
        return redirect('/change-password')

    return render_template('change_password.html')



if __name__ == '__main__':
    app.run(debug=True) 
