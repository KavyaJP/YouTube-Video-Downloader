# YouTube Downloader (Python)

A simple Python script to download videos and playlists from YouTube using the [yt-dlp](https://pypi.org/project/yt-dlp/) library.  
It supports:
- Downloading single YouTube videos
- Downloading entire playlists
- Saving files in the highest available resolution with a progress bar

---

## 🚀 Features
- Download single videos or full playlists
- Progress bar showing download completion percentage
- Displays video file size before download
- Automatically creates a `downloads/` folder
- Error handling (skips unavailable/private/deleted videos)

---

## 📦 Installation

1. Clone this repository:

```bash
git clone https://github.com/KavyaJP/YouTube-Video-Downloader.git
cd YouTube-Video-Downloader
```

2. Change to the Version you want to run:

For Web:
```bash
cd Web
```

For Desktop:
```bash
cd Desktop
```

3. Install Dependancies:

```bash
pip install -r requirements.txt
```

4. Run the App:

For Web:
```bash
flask run
```

For Desktop:
```bash
python main.py
```

    If you Want to wrap the desktop to a standalone executable:
    ```bash
    pyinstaller --name YouTubeDownloader --onefile --windowed main.py
    ```

---

## 📂 Project Structure
```
YouTube-Video-Downloader/
│── downloader.py   # Main script
│── README.md       # Documentation
│── downloads/      # Downloaded videos (auto-created)
```

---

## ⚠️ Disclaimer
This tool is for **educational purposes only**.  
Please respect YouTube’s [Terms of Service](https://www.youtube.com/static?template=terms) and only download content you have the rights to access.

---

## 📝 License
MIT License © 2025 KavyaJP
