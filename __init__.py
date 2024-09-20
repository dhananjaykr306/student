from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL
from math import ceil
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Email
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
app.secret_key = 'many random bytes'
csrf = CSRFProtect(app)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Shaurya@123!'
app.config['MYSQL_DB'] = 'market'

mysql = MySQL(app)

RECORDS_PER_PAGE = 10  # Number of records per page

@app.route('/')
def Index():
    # Get current page number from query parameter, default is 1
    page = request.args.get('page', 1, type=int)
    
    # Calculate total number of records
    cur = mysql.connection.cursor()
    cur.execute("SELECT COUNT(*) FROM student")
    total_records = cur.fetchone()[0]
    cur.close()
    
    # Calculate total number of pages
    total_pages = ceil(total_records / RECORDS_PER_PAGE)
    
    # Calculate offset for SQL query
    offset = (page - 1) * RECORDS_PER_PAGE
    
    # Fetch records for the current page
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM student LIMIT %s OFFSET %s", (RECORDS_PER_PAGE, offset))
    data = cur.fetchall()
    cur.close()
    
    return render_template('index2.html',
                           student=data,
                           page=page,
                           total_pages=total_pages)

@app.route('/insert', methods=['POST'])
def insert():
    if request.method == "POST":
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO student (name, email, phone) VALUES (%s, %s, %s)", (name, email, phone))
        mysql.connection.commit()
        cur.close()
        flash("Data Inserted Successfully", "success")
        return redirect(url_for('Index'))

@app.route('/delete/<string:id_data>', methods=['GET'])
def delete(id_data):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM student WHERE id=%s", (id_data,))
    mysql.connection.commit()
    cur.close()
    flash("Record Has Been Deleted Successfully", "success")
    return redirect(url_for('Index'))

@app.route('/update', methods=['POST'])
def update():
    if request.method == 'POST':
        id_data = request.form['id']
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        cur = mysql.connection.cursor()
        cur.execute("""
               UPDATE student
               SET name=%s, email=%s, phone=%s
               WHERE id=%s
            """, (name, email, phone, id_data))
        mysql.connection.commit()
        cur.close()
        flash("Data Updated Successfully", "success")
        return redirect(url_for('Index'))

@app.route('/search', methods=['GET'])
def search():
    search_query = request.args.get('name')  # Get the search query from the form input
    page = request.args.get('page', 1, type=int)
    
    # Modify the query to search by name, email, or phone
    like_query = f"%{search_query}%"
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT COUNT(*) FROM student 
        WHERE name LIKE %s OR email LIKE %s OR phone LIKE %s
    """, (like_query, like_query, like_query))
    total_records = cur.fetchone()[0]
    total_pages = ceil(total_records / RECORDS_PER_PAGE)
    
    offset = (page - 1) * RECORDS_PER_PAGE
    
    cur.execute("""
        SELECT * FROM student 
        WHERE name LIKE %s OR email LIKE %s OR phone LIKE %s
        LIMIT %s OFFSET %s
    """, (like_query, like_query, like_query, RECORDS_PER_PAGE, offset))
    
    data = cur.fetchall()
    cur.close()
    
    return render_template('index2.html',
                           student=data,
                           page=page,
                           total_pages=total_pages,
                           search_query=search_query)

if __name__ == "__main__":
    app.run(debug=True)
