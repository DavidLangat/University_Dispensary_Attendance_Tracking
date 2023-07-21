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



# Route to handle user login


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


# Route to display the check-in form



# Route to handle check-in form submission


# Route to display the check-out form


# Route to handle check-out form submission


# Route to display medical records of a specific student


# Route to handle admin registration


# Route to display reports for administrators


# route to get student name based on student ID


# Route to display the admin edit form


# Route to delete an admin by ID


# Route to view all registered members (students and admins)


# Route to display the student edit form


# Route to delete a student by ID

# Route to display the admin profile details

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
