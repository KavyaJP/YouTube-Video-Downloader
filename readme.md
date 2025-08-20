# YouTube Downloader (Python)

A simple Python script to download videos and playlists from YouTube using the [pytube](https://pypi.org/project/pytube/) library.  
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

2. Install dependencies:

```bash
pip install pytube
```

---

## ▶️ Usage

Run the script:

```bash
python downloader.py
```

Enter either:
- A single video URL  
- A playlist URL  

The script will detect automatically and download accordingly.

Example:

```text
Enter YouTube video/playlist URL: https://www.youtube.com/watch?v=abcd1234
```

Files will be saved in the `downloads/` folder.

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
