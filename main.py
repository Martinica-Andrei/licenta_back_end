from flask import Flask

app = Flask(__name__)


@app.route("/")
def hello_world():
    with open('test.html', 'r') as file:
        return file.read()

if __name__ == '__main__':
    app.run(debug=True)