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


# Helper function to generate hashed passwords


# Helper function to check if the password matches the hashed password



# Route to handle the home page



# Route to handle student registration



# Route to handle user login


# Route to handle user logout



# Helper function to get the total number of visits to the dispensary


# Helper function to get the number of pending checkouts (students who have checked in but not checked out)


# Helper function to get the total number of checkouts (students who have checked in and checked out)



# Helper function to get the number of students who checked in on the current day


# Route to display the dashboard


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


if __name__ == '__main__':
    app.run(debug=True) 
