import json

from flask import Flask, request
from flask_restful import Api, Resource
from mysql import connector

app = Flask(__name__)

mydb = connector.connect(host="localhost", user="root",
                         passwd="or123iel45678", auth_plugin='mysql_native_password', database="users")
mycursor = mydb.cursor()


@app.route('/', methods=['POST'])
def login():
    if request.method == 'POST':
        val = request
        user = request.json['userName']
        password = request.json['password']
        mycursor.execute("select * from users where UserName "
                         "=\"" + user + "\" and Password=\"" + password + "\"")
        result = mycursor.fetchall()
        return {
            "userName": user,
            "userId": "1234"
        }


if __name__ == "__main__":
    app.run(debug=True)
