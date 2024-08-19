from flask import Flask, jsonify, render_template, request, redirect, url_for, flash
import psycopg2
import subprocess

app = Flask(__name__)

app.secret_key = 's3cr3t_k3y_f0r_flask'


# Database connection parameters
DB_HOST = 'localhost'
DB_NAME = 'attendance_db'
DB_USER = 'Fares'
DB_PASSWORD = 'azertysd10'

def connect_to_db():
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    return conn

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/attendance')
def attendance():
    # Retrieve filter parameters from the query string
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    user_id = request.args.get('user_id')

    # Build SQL query with filters
    query = """
        SELECT a.user_id, a.timestamp, a.attendance_type, u.first_name, u.last_name
        FROM attendance a
        JOIN users u ON a.user_id = u.attendance_id
        WHERE 1=1
    """
    params = []
    
    if start_date:
        query += " AND a.timestamp >= %s"
        params.append(start_date)
    
    if end_date:
        query += " AND a.timestamp <= %s"
        params.append(end_date)
    
    if user_id:
        query += " AND a.user_id = %s"
        params.append(user_id)
    
    query += " ORDER BY a.timestamp DESC"

    conn = connect_to_db()
    cur = conn.cursor()
    cur.execute(query, params)
    rows = cur.fetchall()
    cur.close()
    conn.close()

    # Log the query and parameters for debugging
    print("Executed Query:", cur.mogrify(query, params).decode())

    # Pass only filtered attendance data to the template
    attendance_list = [
        {
            "user_id": row[0],
            "timestamp": row[1],
            "attendance_type": row[2],
            "first_name": row[3],
            "last_name": row[4]
        }
        for row in rows
    ]

    return render_template('attendance.html', attendance=attendance_list, start_date=start_date, end_date=end_date, user_id=user_id)



@app.route('/users')
def users():
    return render_template('users.html')

@app.route('/add_user')
def add_user():
    return render_template('add_user.html')

@app.route('/create_user', methods=['POST'])
def create_user():
    # Retrieve form data
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    attendance_id = request.form.get('attendance_id')

    # Connect to the database
    conn = connect_to_db()
    cur = conn.cursor()

    # Insert the new user into the users table
    try:
        cur.execute("""
            INSERT INTO users (first_name, last_name, email, phone, attendance_id)
            VALUES (%s, %s, %s, %s, %s);
        """, (first_name, last_name, email, phone, attendance_id))
        conn.commit()
        flash("User successfully created!", "success")
    except Exception as e:
        conn.rollback()
        flash(f"Error creating user: {e}", "danger")
    finally:
        cur.close()
        conn.close()

    # Redirect back to the form or to a success page
    return redirect(url_for('add_user'))

@app.route('/api/users', methods=['GET'])
def get_users():
    conn = connect_to_db()
    cur = conn.cursor()
    cur.execute("SELECT id, first_name, last_name, email, phone, attendance_id FROM users ORDER BY last_name ASC")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    user_list = [
        {
            "id": row[0],
            "first_name": row[1],
            "last_name": row[2],
            "email": row[3],
            "phone": row[4],
            "attendance_id": row[5]
        }
        for row in rows
    ]
    
    return jsonify(user_list)

if __name__ == '__main__':
    app.run(debug=True)