from flask import Flask, request, Markup
from flask import render_template, flash, Markup

import os
import json

app = Flask(__name__)


if __name__ == '__main__':
    app.run(debug=False) # change to False when running in production