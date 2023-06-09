FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y ffmpeg

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --force-reinstall 'https://github.com/ytdl-org/youtube-dl/archive/refs/heads/master.tar.gz'

COPY . .

CMD ["python", "app.py"]
