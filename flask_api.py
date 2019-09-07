#!/usr/bin/env python
import os
from flask import Flask, abort, request, jsonify, g, url_for, Response, make_response, render_template, redirect
from flask_sqlalchemy import SQLAlchemy

from lyrics import *
from random import randint

# initialization
app = Flask(__name__)
app.secret_key = 'A0Zr98j/3yR~XHH!jmN]dgsLWX/,?RT'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'

db = SQLAlchemy(app)


class Visit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    page_count = db.Column(db.Integer)
    lyrics_count = db.Column(db.Integer)

    def __init__(self):
        self.page_count = 0
        self.lyrics_count=0


@app.route('/',methods=['GET','POST'])
def home():
    v = Visit.query.first()
    if not v:
        v = Visit()
        v.page_count += 1
        db.session.add(v)
    v.page_count +=1
    db.session.commit()
    return render_template('index.html', page_count = v.page_count, lyrics_count = v.lyrics_count)


@app.route('/download')
def fetchsrt():
    v = Visit.query.first()
    if not v:
        v = Visit()
        v.lyrics_count += 1
        db.session.add(v)
    v.lyrics_count +=1
    db.session.commit()
    try:
        i=0
        song = request.args.get('song')
        artist = request.args.get('artist')
        search = request.args.get('search')
        print "heelo"
        if not search and not song:
            return "Enter Song name or Search value"
        else:
            if search:
                song  = search
            else:
                if song:
                    if artist:
                        song = song+" "+artist
                    else:
                        song = song

        print song
        youtube_id=""
        lyrics=""
        while (len(lyrics)<40 and i < 5):
            print i
            (lyrics,youtube_id) = fetch_srt(song,youtube_id)
            
            i=i+1
            if len(lyrics)>39:
                break

        if(len(lyrics)<40):
            lyrics=fetch_subtitle(song)
            #print "2nd"
        if(len(lyrics)<40):
            return "Lyrics Not Found. "

        file_name=song+".srt"
        response = make_response(lyrics)
        # This is the key: Set the right header for the response
        # to be downloaded, instead of just printed on the browser
        response.headers["Content-Disposition"] = "attachment; filename=\"" + file_name +"\""
        #"attachment; filename=\"" + Path.GetFileName( filePath ) + "\"")
        return response
    except:
        return "An error occurred. Please check your request."

@app.route('/down/',methods = ['POST'])
def fetchsrts():
    v = Visit.query.first()
    if not v:
        v = Visit()
        v.lyrics_count += 1
        db.session.add(v)
    v.lyrics_count +=1
    db.session.commit()
    try:
        i=0
        song = request.form.get("name")
        youtube_id=""
        lyrics=""
        while (len(lyrics)<40 and i < 5):
            print i
            (lyrics,youtube_id) = fetch_srt(song,youtube_id)
            
            i=i+1
            if len(lyrics)>39:
                break

        if(len(lyrics)<40):
            lyrics=fetch_subtitle(song)
            #print "2nd"
        if(len(lyrics)<40):
            return "Lyrics Not Found. "

        file_name=song+".srt"
        response = make_response(lyrics)
        # This is the key: Set the right header for the response
        # to be downloaded, instead of just printed on the browser
        response.headers["Content-Disposition"] = "attachment; filename=\"" + file_name +"\""
        #"attachment; filename=\"" + Path.GetFileName( filePath ) + "\"")
        return response
    except:
        msg= "y"
        return redirect(url_for('home',msg=msg))

@app.route('/api')
def fetchContent():
    v = Visit.query.first()
    if not v:
        v = Visit()
        v.lyrics_count += 1
        db.session.add(v)
    v.lyrics_count +=1
    db.session.commit()

    try:
        i=0
        song = request.args.get('song')
        artist = request.args.get('artist')
        search = request.args.get('search')
        if not search and not song:
            return "Enter Song name or Search value"
        else:
            if search:
                song  = search
            else:
                if song:
                    if artist:
                        song = song+" "+artist
                    else:
                        song = song

        
        #lyrics = fetch_srt(song)
        youtube_id=""
        #f = tempfile.TemporaryFile(mode='w+t')
        lyrics=""
        while (len(lyrics)<40 and i < 5):
            #print i
            (lyrics,youtube_id) = fetch_srt(song,youtube_id)
            
            i=i+1
            if len(lyrics)>39:
                break

        if(len(lyrics)<40):
            lyrics=fetch_subtitle(song)
            #print "2nd"
        if(len(lyrics)<40):
            return "Lyrics Not Found. "

        return lyrics
    except:
        return "An error occurred. Please check your request."


if __name__ == '__main__':
    if not os.path.exists('db.sqlite'):
        db.create_all()
    port = int(os.environ.get("PORT", 2000))
    app.run(host='0.0.0.0', port=port,debug=True)
