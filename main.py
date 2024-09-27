from flask import Flask
import pandas as pd
from flask import request

app = Flask(__name__)


@app.get("/api/books")
def books():
    return request.args.get('title', '')

if __name__ == '__main__':
    app.run(debug=True)