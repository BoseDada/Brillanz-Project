from flask import Flask, render_template, request, flash, redirect, url_for
import moviepy.editor as mp
import whisper
import os
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

app = Flask(__name__)
app.secret_key = 'Brillanz'

@app.route('/')
@app.route('/home')
def home():
    return render_template('index.html')

@app.route('/getstarted',methods = ['GET','POST'])
def getstarted():
    return render_template('getstarted.html')

ALLOWED_EXTENSIONS = ['mp4']
UPLOAD_FOLDER = 'Files/videos/'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods = ['GET','POST'])
def upload():
    if 'video' not in request.files:
        return redirect(url_for('getstarted'))
    video = request.files['video']
    if video.filename == '':
        flash('No video selected')
    if video and allowed_file(video.filename):
        video.save(UPLOAD_FOLDER + video.filename)
        flash('File uploaded successfully!')

    return redirect(url_for('getstarted'))



if __name__ == '__main__':
    app.run(debug = True, port = 9100)
