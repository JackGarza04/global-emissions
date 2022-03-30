from flask import Flask, request, Markup
from flask import render_template, flash, Markup

import os
import json

app = Flask(__name__)

@app.route("/")
def render_main():
    return render_template('index.html')

@app.route("/p1")
def render_page1():
    return render_template('page1.html')

    
if __name__ == '__main__':
    app.run(debug=False) # change to False when running in production