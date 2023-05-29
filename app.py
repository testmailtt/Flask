from flask import Flask, request, send_file, jsonify
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydub import AudioSegment
import youtube_dl

app = Flask(__name__)
Base = declarative_base()
engine = create_engine('sqlite:///audio.db', echo=True)
Session = sessionmaker(bind=engine)
session = Session()

class Audio(Base):
    __tablename__ = 'audio'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    filename = Column(String)

Base.metadata.create_all(engine)

@app.route('/')
def home():
    audios = session.query(Audio).all()
    audio_list = [{'id': audio.id, 'title': audio.title} for audio in audios]
    return jsonify(audio_list)

@app.route('/download', methods=['POST'])
def download():
    url = request.form.get('url')
    if not url:
        return 'No URL provided.', 400

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
            'preferredquality': '192',
        }],
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        audio_file = ydl.prepare_filename(info_dict)

        audio = Audio(title=info_dict.get('title'), filename=audio_file)
        session.add(audio)
        session.commit()

    return 'Audio downloaded and saved to the database.'

@app.route('/audio/<int:audio_id>')
def serve_audio(audio_id):
    audio = session.query(Audio).get(audio_id)
    if not audio:
        return 'Audio not found.', 404

    return send_file(audio.filename)

@app.route('/transcribe/<int:audio_id>')
def transcribe(audio_id):
    audio = session.query(Audio).get(audio_id)
    if not audio:
        return 'Audio not found.', 404

    r = sr.Recognizer()
    with sr.AudioFile(audio.filename) as audio_file:
        audio_data = r.record(audio_file)
        transcription = r.recognize_google(audio_data)

    audio.transcription = transcription
    session.commit()

    return jsonify({'audio_id': audio_id, 'transcription': transcription})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
