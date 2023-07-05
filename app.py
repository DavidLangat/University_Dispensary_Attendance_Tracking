from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', state='dashboard')

@app.route('/register')
def register():
    return render_template('dashboard.html', state='register')

@app.route('/medical-records')
def medical_records():
    return render_template('dashboard.html', state='medical-records')

# Add more routes for other content options as needed

if __name__ == '__main__':
    app.run(debug=True)
