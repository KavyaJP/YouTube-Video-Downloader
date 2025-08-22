@echo off
TITLE Speech Emotion Recognition Launcher

echo "Starting and the Web Interface"
start http://localhost:5000

python app.py

pause