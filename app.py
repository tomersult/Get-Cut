from flask import Flask, render_template , request ,redirect
from flask_mysqldb import MySQL
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


#create a flask instance
app = Flask(__name__)

app.config['MYSQL_HOST'] = "localhost"
app.config['MYSQL_USER'] = "root"
app.config['MYSQL_PASSWORD'] = "1234"
app.config['MYSQL_DB'] = "users_db"

mysql = MySQL(app)

@app.route('/',methods=['GET','POST']) #/login
def index():

    if request.method == 'POST':
        #json_value = request.json['key']
        username = request.form['username']
        email = request.form['email'] # password

        cur = mysql.connection.cursor()
        sql = "INSERT INTO users (name, email) VALUES (%s, %s)"
        val = (username,email)
        cur.execute(sql, val)
        mysql.connection.commit()
        cur.close()

        return "seccess" # return token

    return render_template('index.html')

@app.route('/users')
def users():
    cur = mysql.connection.cursor()

    users = cur.execute("SELECT * FROM users")

    if users > 0:
        userDetails = cur.fetchall()

        return render_template('users.html', userDetails=userDetails)

if __name__ == "__main__":
    app.run(debug=True)