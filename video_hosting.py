# coding=utf-8
import sqlite3

from flask import Flask
from flask import render_template, request, redirect
app = Flask(__name__)

global videos, categories, keywords, taxeis, video_keywords
con = None
videos = []
categories = []
keywords = []
taxeis = []
video_keywords = []
try:
    con = sqlite3.connect('sxoleio.pw.videos.db')
    cur = con.cursor()

    cur.execute('select * from videos')
    for row in cur.fetchall():
        videos.append(row)

    cur.execute('select * from video_keywords')
    for row in cur.fetchall():
        video_keywords.append(row)

    cur.execute('select * from categories order by description')
    for row in cur.fetchall():
        counter=0
        for item in videos:
            if item[2]==row[0]:
                counter+=1
        categories.append([row[0], row[1], counter])

    cur.execute('select * from keywords')
    for row in cur.fetchall():
        counter=0
        for item in video_keywords:
            if item[1]==row[0]:
                counter+=1
        keywords.append([row[0], row[1], counter])

    cur.execute('select * from taxeis')
    for row in cur.fetchall():
        counter=0
        for item in videos:
            if row[0]==item[1]:
                counter+=1
        taxeis.append([row[0], row[1], counter])



except sqlite3.Error, e:
    print "Error %s:" % e.args[0]
    sys.exit(1)


@app.route('/')
def index():
    return render_template('homepage.html', t_categories=categories, t_keywords=keywords, t_taxeis=taxeis)

@app.route('/category/<name>')
def category(name):
    category_name=''
    for item in categories:
        if int(name)==item[0]:
            category_name=item[1]
    if category_name=='':
        print 'error' #TODO Create an error template

    category_videos = []
    for item in videos:
        if item[2]==int(name):
            category_videos.append(item)

    return render_template('list-videos.html', category=category_name, videos=category_videos, t_categories=categories, t_keywords=keywords, t_taxeis=taxeis)


@app.route('/taxi/<name>')
def taxi(name):
    taxi_name=''
    for item in taxeis:
        if item[0]==int(name):
            taxi_name=item[1]
    if taxi_name=='':
        print 'error' #TODO Create an error template

    taxi_videos = []
    for item in videos:
        if item[1]==int(name):
            taxi_videos.append(item)

    return render_template('list-videos.html', taxi=taxi_name, videos=taxi_videos, t_categories=categories, t_keywords=keywords)

@app.route('/video/<id>')
def video(id):
    return render_template('video.html', video=getVideoFromId(id), t_categories=categories, t_taxeis=taxeis)

def getVideoFromId(id):
    global videos
    for item in videos:
        if item[0]==int(id):
            return item
    return -1
