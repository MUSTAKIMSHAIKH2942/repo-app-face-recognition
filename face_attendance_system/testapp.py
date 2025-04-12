# save as rtsp_to_mjpeg.py

import subprocess
from flask import Flask, Response

RTSP_URL = "rtsp://admin:Dev2105@@192.168.1.12:554/h264/ch1/main/av_stream"

app = Flask(__name__)

def generate():
    # FFmpeg command to convert RTSP to MJPEG
    cmd = [
        'ffmpeg',
        '-i', RTSP_URL,
        '-f', 'mjpeg',
        '-qscale', '5',
        '-vf', 'scale=640:360',
        '-'
    ]

    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)

    while True:
        chunk = process.stdout.read(1024)
        if not chunk:
            break
        yield chunk

@app.route('/')
def stream():
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
