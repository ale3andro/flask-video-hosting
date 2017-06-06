# coding=utf-8
import sqlite3, sys, string, os

from flask import Flask
from flask import render_template, request, redirect, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'sxoleio.pw.videos.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = "asu9japfj09ruj230jx0q3QR#@#R Kk3"

db = SQLAlchemy(app)

class videos(db.Model):
    id = db.Column('id', db.Integer, primary_key=True)
    taxi_id = db.Column('taxi_id', db.Integer)
    category_id = db.Column('category_id', db.Integer)
    width = db.Column('width', db.Integer)
    height = db.Column('height', db.Integer)
    filename = db.Column('filename', db.String(100))
    notes = db.Column('notes', db.String(300))

class categories(db.Model):
    id = db.Column('id', db.Integer, primary_key=True)
    description = db.Column('description', db.String(50))

class keywords(db.Model):
    id = db.Column('id', db.Integer, primary_key=True)
    description = db.Column('description', db.String(50))

class taxeis(db.Model):
    id = db.Column('id', db.Integer, primary_key=True)
    description = db.Column('description', db.String(5))

class video_keywords(db.Model):
    id = db.Column('id', db.Integer, primary_key=True)
    keyword_id = db.Column('keyword_id', db.Integer)
    video_id = db.Column('video_id', db.Integer)


@app.route('/')
def index():
    t_categories = categories.query.all()
    t_counter_categories = []
    for item in t_categories:
        vids = videos.query.filter_by(category_id=item.id)
        t_counter_categories.append(vids.count())

    t_taxeis = taxeis.query.all()
    t_counter_taxeis = []
    for item in t_taxeis:
        vids = videos.query.filter_by(taxi_id=item.id)
        t_counter_taxeis.append(vids.count())

    t_keywords = keywords.query.all()
    t_counter_keywords = []
    for item in t_keywords:
        vids = video_keywords.query.filter_by(keyword_id=item.id)
        t_counter_keywords.append(vids.count())

    return render_template('homepage.html', t_categories=t_categories, t_counter_categories=t_counter_categories, t_keywords=t_keywords, t_counter_keywords=t_counter_keywords, t_taxeis=t_taxeis, t_counter_taxeis=t_counter_taxeis)

@app.route('/keyword/<keyword_id>')
def keyword(keyword_id):
    keyword=keywords.query.get(int(keyword_id))
    tmp_vidkeys = video_keywords.query.filter_by(keyword_id=int(keyword_id))
    vidIds = []
    for tmp_vidkey in tmp_vidkeys:
        vidIds.append(tmp_vidkey.video_id)
    keyword_videos = videos.query.filter(videos.id.in_(vidIds))

    return render_template('list-videos.html', keyword=keyword, videos=keyword_videos, t_categories=categories.query.all(), t_taxeis=taxeis.query.all())

@app.route('/category/<category_id>')
def category(category_id):
    category = categories.query.get(int(category_id))
    category_videos = videos.query.filter_by(category_id=int(category_id))

    category_videos_keywords = []
    for item in category_videos:
        tmp_vidkeys = video_keywords.query.filter_by(video_id=item.id)
        for tmp_vidkey in tmp_vidkeys:
            keyword = keywords.query.get(tmp_vidkey.keyword_id)
            if (keyword!=None):
                category_videos_keywords.append([item.id, keyword.id, keyword.description])

    return render_template('list-videos.html', category=category, videos=category_videos, video_keywords=category_videos_keywords, t_taxeis=taxeis.query.all())


@app.route('/taxi/<taxi_id>')
def taxi(taxi_id):
    taxi = taxeis.query.get(int(taxi_id))
    taxi_videos = videos.query.filter_by(taxi_id=int(taxi_id))

    taxi_videos_keywords = []
    for item in taxi_videos:
        tmp_vidkeys = video_keywords.query.filter_by(video_id=item.id)
        for tmp_vidkey in tmp_vidkeys:
            keyword = keywords.query.get(tmp_vidkey.keyword_id)
            if (keyword!=None):
                taxi_videos_keywords.append([item.id, keyword.id, keyword.description])

    return render_template('list-videos.html', taxi=taxi, videos=taxi_videos, video_keywords=taxi_videos_keywords, t_categories=categories.query.all())

@app.route('/commit', methods=["POST"])
def commit_edit_changes():
    f_id = request.form.get('theid')
    f_perigrafh = request.form.get('perigrafh')
    f_taxh = request.form.get('taxh')
    f_category = request.form.get('category')
    f_keywords = request.form.get('keywords')

    selected_video = videos.query.get(int(f_id))
    s_taxh = selected_video.taxi_id
    s_category = selected_video.category_id

    if (f_perigrafh!=""):
        selected_video.notes=f_perigrafh
        db.session.commit()

    if (f_taxh!=s_taxh):
        selected_video.taxi_id=int(f_taxh)
        db.session.commit()

    if (f_category!=s_category):
        selected_video.category_id=int(f_category)
        db.session.commit()

    #keywords
    # Αρχικά βρίσκω τα ήδη αποθηκευμένα keywords του video
    current_keywords=[]
    tmp_vidkeys = video_keywords.query.filter_by(video_id=int(f_id))
    for tmp_vidkey in tmp_vidkeys:
        keyword = keywords.query.get(tmp_vidkey.keyword_id)
        if (keyword!=None):
            current_keywords.append([keyword.id, keyword.description])
    # Μετά κάνω πεζά και strip από κενά τα νέα keywords
    f_keywords_lower = f_keywords.lower()
    f_keywords_lower = f_keywords.strip()

    # Αν ο τελευταίας χαρακτήρας είναι το κόμμα τότε πρέπει να φύγει για να μην έχω κενό keyword
    while (f_keywords_lower.endswith(",")):
        f_keywords_lower=f_keywords_lower[0:len(f_keywords_lower)-1]

    new_keywords = []
    the_keywords = f_keywords_lower.split(',')
    counter=0
    for item in the_keywords:
        if(item!=''):
            new_keywords.append(item.strip())
            counter+=1

    for new_k in new_keywords:
        found_in_video=False
        # Αρχικά η αναζήτηση γίνεται μέσα στα ήδη υπάρχοντα keywords του video - αν φυσικά υπάρχουν
        for old_k in current_keywords:
            if (new_k==old_k[1]):
                found_in_video=True # To keyword υπάρχει ήδη - απλά αλλάζει το flag found_in_video (δεν χρειάζεται άλλο aciton)

        # Αν όμως το keyword δεν υπάρχει μέσα στα ήδη υπάρχοντα του video, πρέπει πρώτα να αναζητήσω αν υπάρχει τέτοιo keyword ήδη ώστε να μην το ξαναδημιουργήσω
        if not found_in_video:
            found_in_db=False
            srch_keywords = keywords.query.filter_by(description=new_k) # Αναζήτηση μέσα σε  όλα τα keywords
            if (srch_keywords.count()!=0):
                found_in_db=True # Υπάρχει ήδη στη ΒΔ μένει μόνο να δημιουργηθεί η συσχέτιση
                new_video_keyword = video_keywords(keyword_id=int(srch_keywords[0].id), video_id=int(f_id))
                db.session.add(new_video_keyword)
                db.session.commit()
            if not found_in_db: # Εισαγωγή νέου keyword και μετά της συσχέτισης
                new_keyword = keywords(description=new_k)
                print new_keyword
                db.session.add(new_keyword)
                db.session.commit()
                new_video_keyword = video_keywords(keyword_id=int(new_keyword.id), video_id=int(f_id))
                db.session.add(new_video_keyword)
                db.session.commit()

    # Τέλος ένας ακόμη έλεγχος - Αν κάποιο από τα αρχικά keywords δεν υπάρχει στα νέα, πρέπει να διαγραφεί.
    for item in current_keywords:
        if item[1] not in new_keywords:
            keyword = keywords.query.get(int(item[0]))
            db.session.delete(keyword)
            db.session.commit()

    # Διαγραφή ορφανών keywords
    all_keywords = keywords.query.all()
    for row in all_keywords:
        tmp_vidkeys = video_keywords.query.filter_by(keyword_id=row.id)
        if (tmp_vidkeys.count()==0):
            key = keywords.query.get(row.id)
            db.session.delete(key)
            db.session.commit()

    flash('Τα στοιχεία του video ενημερώθηκαν με επιτυχία!')
    return redirect('/video/'+f_id)

@app.route('/video/<id>')
def video(id):
    video=videos.query.get(int(id))
    f_keywords=[]
    tmp_keywords=video_keywords.query.filter_by(video_id=int(id))
    for item in tmp_keywords:
        tmp_key=keywords.query.get(item.keyword_id)
        if (tmp_key!=None):
            f_keywords.append([tmp_key.id, tmp_key.description])

    return render_template('video.html', video=video, keywords=f_keywords, t_categories=categories.query.all(), t_taxeis=taxeis.query.all())

@app.route('/edit/<id>')
def edit(id):
    video=videos.query.get(int(id))
    f_keywords=[]
    tmp_keywords=video_keywords.query.filter_by(video_id=int(id))
    for item in tmp_keywords:
        tmp_key=keywords.query.get(item.keyword_id)
        if (tmp_key!=None):
            f_keywords.append([tmp_key.id, tmp_key.description])

    return render_template('edit.html', video=video, keywords=f_keywords, t_categories=categories.query.all(), t_taxeis=taxeis.query.all(), t_keywords=keywords.query.all())
