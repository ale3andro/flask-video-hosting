# coding=utf-8
import sqlite3

from flask import Flask
from flask import render_template, request, redirect
app = Flask(__name__)

con = None
try:
    con = sqlite3.connect('sxoleio.pw.videos.db')
    cur = con.cursor()
    cur.execute('SELECT SQLITE_VERSION()')
    data = cur.fetchone()
    print "SQLite version: %s" % data
except lite.Error, e:
    print "Error %s:" % e.args[0]
    sys.exit(1)


@app.route('/')
def index():
    return render_template('homepage.html')

@app.route('/taxi/<name>')
def taxi(name):
    return render_template('taxi.html', taxi=name)
