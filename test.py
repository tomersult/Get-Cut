from flask import Flask , request

app = Flask(__name__)

@app.route('/',methods=['GET','POST'])
def index():
    value = request.json['key']
    return value

if __name__ == '__main__':
    app.run(debug=True)