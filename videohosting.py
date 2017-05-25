# coding=utf-8
import sqlite3, sys, string

from flask import Flask
from flask import render_template, request, redirect
app = Flask(__name__)

global videos, categories, keywords, taxeis, video_keywords, con, cur
try:
    con = sqlite3.connect('sxoleio.pw.videos.db')
    cur = con.cursor()
except sqlite3.Error, e:
    print "Error %s:" % e.args[0]
    sys.exit(1)

videos = []
categories = []
keywords = []
taxeis = []
video_keywords = []

def load_globals():
    global videos, categories, keywords, taxeis, video_keywords, con, cur
    videos = []
    categories = []
    keywords = []
    taxeis = []
    video_keywords = []
    try:
        print 'loading globals'
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

        cur.execute('select * from keywords order by description')
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
    load_globals()
    return render_template('homepage.html', t_categories=categories, t_keywords=keywords, t_taxeis=taxeis)

@app.route('/keyword/<keyword_id>')
def keyword(keyword_id):
    keyword_name=''
    for item in keywords:
        if item[0]==int(keyword_id):
            keyword_name=item[1]
    if keyword_name=='':
        print 'error' #TODO Create an error template
    keyword_videos = []
    for item in video_keywords:
        if item[1]==int(keyword_id):
            for video in videos:
                if video[0]==item[2]:
                    keyword_videos.append(video)

    return render_template('list-videos.html', keyword=keyword_name, videos=keyword_videos, t_categories=categories, t_keywords=keywords, t_video_keywords=video_keywords, t_taxeis=taxeis)

@app.route('/category/<name>')
def category(name):
    category_name=''
    for item in categories:
        if int(name)==item[0]:
            category_name=item[1]
    if category_name=='':
        print 'error' #TODO Create an error template

    category_videos = []
    category_videos_keywords = []
    for item in videos:
        if item[2]==int(name):
            category_videos.append(item)
            for key_video in video_keywords:
                if item[0]==key_video[2]:
                    for keyword in keywords:
                        if (keyword[0]==key_video[1]):
                            category_videos_keywords.append([item[0], keyword[0], keyword[1]])  #video_id, keyword_id, keyword_name

    return render_template('list-videos.html', category=category_name, videos=category_videos, video_keywords=category_videos_keywords, t_categories=categories, t_keywords=keywords, t_video_keywords=video_keywords, t_taxeis=taxeis)


@app.route('/taxi/<name>')
def taxi(name):
    taxi_name=''
    for item in taxeis:
        if item[0]==int(name):
            taxi_name=item[1]
    if taxi_name=='':
        print 'error' #TODO Create an error template

    taxi_videos = []
    taxi_videos_keywords = []
    for item in videos:
        if item[1]==int(name):
            taxi_videos.append(item)
            for key_video in video_keywords:
                if item[0]==key_video[2]:
                    for keyword in keywords:
                        if (keyword[0]==key_video[1]):
                            taxi_videos_keywords.append([item[0], keyword[0], keyword[1]])  #video_id, keyword_id, keyword_name

    return render_template('list-videos.html', taxi=taxi_name, videos=taxi_videos, video_keywords=taxi_videos_keywords, t_categories=categories, t_keywords=keywords)

@app.route('/edit/<id>')
def edit(id):
    return render_template('edit.html', video=getVideoFromId(id), keywords=getKeywordsFromVideoId(id), t_categories=categories, t_taxeis=taxeis, t_keywords=keywords)

@app.route('/commit', methods=["POST"])
def commit_edit_changes():
    f_id = request.form.get('theid')
    f_perigrafh = request.form.get('perigrafh')
    f_taxh = request.form.get('taxh')
    f_category = request.form.get('category')
    f_keywords = request.form.get('keywords')

    cur.execute('select * from videos where `id`=%d' % int(f_id))
    for row in cur.fetchall():
        s_taxh = row[1]
        s_category = row[2]

    if (f_perigrafh!=""):
        query = "update videos set notes='%s' where id=%d" % (f_perigrafh, int(f_id))
        cur.execute(query)

    if (f_taxh!=s_taxh):
        query = "update videos set taxi_id=%d where id=%d" % (int(f_taxh), int(f_id))
        cur.execute(query)

    if (f_category!=s_category):
        query = "update videos set category_id=%d where id=%d" % (int(f_category), int(f_id))
        cur.execute(query)

    #keywords
    cur_keywords = getKeywordsFromVideoId(int(f_id))
    f_keywords_lower = f_keywords.lower()
    new_keywords = f_keywords_lower.split(',')
    for i in range(0, len(new_keywords)):
        new_keywords[i]=new_keywords[i].strip()


    for new_k in new_keywords:
        found_in_video=False
        # Αρχικά η αναζήτηση γίνεται μέσα στα ήδη υπάρχοντα keywords του video - αν φυσικά υπάρχουν
        for old_k in cur_keywords:
            if (new_k==old_k[1]):
                found_in_video=True # To keyword υπάρχει ήδη - απλά αλλάζει το flag

        # Αν όμως το keyword δεν υπάρχει μέσα στα ήδη υπάρχοντα του video, πρέπει πρώτα να αναζητήσω αν υπάρχει τέτοιo keyword ήδη ώστε να μην το ξαναδημιουργήσω
        if not found_in_video:
            found_in_db=False
            for keyword in keywords: # Αναζήτηση μέσα σε  όλα τα keywords
                if (keyword[1]==new_k):
                    found_in_db=True # Υπάρχει ήδη στη ΒΔ μένει μόνο να δημιουργηθεί η συσχέτιση
                    query = "insert into video_keywords values (null, %d, %d)" % (int(keyword[0]), int(f_id))
                    cur.execute(query)
            if not found_in_db: # Εισαγωγή νέου keyword και μετά της συσχέτισης
                query1 = "insert into keywords values(null, '%s')" % new_k
                cur.execute(query1)
                new_keyword_id = cur.lastrowid
                query2 = "insert into video_keywords values (null, %d, %d)" % (int(new_keyword_id), int(f_id))
                cur.execute(query2)
    # Τέλος ένας ακόμη έλεγχος - Αν κάποιο από τα αρχικά keywords δεν υπάρχει στα νέα, πρέπει να διαγραφεί.
    for item in cur_keywords:
        if item[1] not in new_keywords:
            query = "delete from video_keywords where keyword_id=%d and video_id=%d" % (int(item[0]), int(f_id))
            cur.execute(query)
    # Διαγραφή ορφανών keywords
    con.commit()
    cur.execute("select * from keywords")
    for row in cur.fetchall():
        query = "select * from video_keywords where keyword_id=%d" % int(row[0])
        cur.execute(query)
        if (len(cur.fetchall())==0):
            cur.execute("delete from keywords where id=%d" % int(row[0]))

    con.commit()
    load_globals()
    return render_template('error.html', id=f_id, perigrafh=f_perigrafh, taxh=f_taxh, category=f_category, keywords=f_keywords)

@app.route('/video/<id>')
def video(id):
    return render_template('video.html', video=getVideoFromId(id), keywords=getKeywordsFromVideoId(id), t_categories=categories, t_taxeis=taxeis)

def getVideoFromId(id):
    global videos
    for item in videos:
        if item[0]==int(id):
            return item
    return -1

def getKeywordsFromVideoId(id):
    global video_keywords, keywords
    vid_keywords = []
    for item in video_keywords:
        if (int(id)==item[2]):
            for keyword in keywords:
                if (item[1]==keyword[0]):
                    vid_keywords.append([keyword[0], keyword[1]])
    return vid_keywords
