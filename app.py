from flask import Flask, render_template, request, flash, redirect, url_for, session, send_file
import moviepy.editor as mp
import whisper
from gtts import gTTS
from googletrans import Translator
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

uploaded = False
@app.route('/upload', methods = ['GET','POST'])
def upload():
    global uploaded
    if 'video' not in request.files:
        return redirect(url_for('getstarted'))
    video = request.files['video']
    if video.filename == '':
        flash('No video selected')

    filename = video.filename    
    if video and allowed_file(filename):
        video.save(UPLOAD_FOLDER + filename)
        flash('File uploaded successfully!')
        uploaded = True
        session['uploaded_filename'] = filename

    return redirect(url_for('getstarted'))

@app.route('/set_language', methods = ['POST'])
def set_language():
    selected_language = request.form['language']
    session['selected_language'] = selected_language

    return redirect(url_for('getstarted'))

processed = False
@app.route('/process', methods = ['GET','POST'])
def process():
    if uploaded:
        global processed
        selected_language = session.get('selected_language','en')
        filename = session.get('uploaded_filename')
        #Writing Video to Audio
        clip = mp.VideoFileClip(r'Files/videos/' + filename)
        audio_filename = filename[:-3]+"mp3"
        clip.audio.write_audiofile(r'Files/audios/' + audio_filename)

        #Transcribing Video
        model = whisper.load_model("base")
        result = model.transcribe('Files/audios/' + audio_filename)

        #Converting Transcription into Text file
        text_filename = filename[:-3]+"txt"
        with open("Files/transcriptions/" + text_filename,"w") as file:
                file.write(result['text'])

        translator = Translator()

        #Opening Transripted file
        file = open("Files/transcriptions/" + text_filename, "r")
        if file.mode == 'r':
            contents = file.read()


        # Translation to Hindi
        translated_to_hindi = translator.translate(contents, dest=selected_language)
        text_hi = translated_to_hindi.text

        #Making Translation text file 
        translated_text_fielname = filename[:-4] + "translated.txt"
        with open("Files/translated transcriptions/" + translated_text_fielname, "w") as f:
            f.write(text_hi)

        #Reading Translated text file
        file = open("Files/translated transcriptions/" + translated_text_fielname, "r")
        if file.mode == 'r':
            translated_contents = file.read()

        #Converting text to speech
        translated_audio_filename = filename[:-4] + "translated.mp3"
        myobj = gTTS(text = translated_contents, lang = selected_language, slow = False)
        myobj.save("Files/translated audios/" + translated_audio_filename)

        #Embedding audio to original video
        translated_video_filename = filename[:-4] + "translated.mp4"
        clip = mp.VideoFileClip("Files/videos/" + filename)
        audioclip = mp.AudioFileClip("Files/translated audios/"+ translated_audio_filename)
        videofile = clip.set_audio(audioclip)
        videofile.write_videofile("Files/translated videos/" + translated_video_filename, codec="libx264", audio_codec="aac", temp_audiofile = "Files/translated audios/" + filename[:-4] + "translated.m4a", remove_temp = True)
        session['translated_filename'] = translated_video_filename
        flash("Process Completed!")
        processed = True
    
    else:
        flash("Video not uploaded")

    return redirect(url_for('getstarted'))

@app.route('/download', methods = ['GET'])
def download():
    if processed:
        filename = session.get('translated_filename')
        video_path = "Files/translated videos/" + filename
        
        return send_file(video_path, as_attachment=True)
    
    else:
        flash("Process not completed")
    
    return redirect(url_for('getstarted'))
    
if __name__ == '__main__':
    app.run(debug = True, port = 9100)
