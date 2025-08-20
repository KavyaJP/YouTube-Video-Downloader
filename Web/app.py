from flask import Flask, render_template, request, jsonify
import yt_dlp
import os

app = Flask(__name__)
os.makedirs("downloads", exist_ok=True)


def get_available_formats(url):
    """
    Fetches available formats for a given YouTube URL without downloading.
    Returns a curated list of format options.
    """
    ydl_opts = {"quiet": True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

    # We will create a curated list of formats for the user
    format_options = []

    # Add an audio-only option first
    format_options.append(
        {"id": "bestaudio/best", "text": "Audio Only (Best Quality MP3)"}
    )

    # Filter for some common mp4 video resolutions
    target_resolutions = [1080, 720, 480, 360]
    found_resolutions = set()

    for f in info.get("formats", []):
        # We only want mp4 files that have video and audio
        if (
            f.get("ext") == "mp4"
            and f.get("vcodec") != "none"
            and f.get("acodec") != "none"
        ):
            height = f.get("height")
            if height in target_resolutions and height not in found_resolutions:
                filesize = f.get("filesize") or f.get("filesize_approx", 0)
                filesize_mb = (
                    f"{filesize / 1024 / 1024:.2f} MB" if filesize else "Unknown size"
                )

                format_options.append(
                    {"id": f["format_id"], "text": f"{height}p - MP4 ({filesize_mb})"}
                )
                found_resolutions.add(height)

    return format_options


@app.route("/")
def index():
    """Renders the main page."""
    return render_template("index.html")


@app.route("/get-formats", methods=["POST"])
def get_formats():
    """
    API endpoint to be called by JavaScript.
    Receives a URL and returns a JSON list of available formats.
    """
    video_url = request.json.get("url")
    if not video_url:
        return jsonify({"error": "URL is required."}), 400
    try:
        formats = get_available_formats(video_url)
        return jsonify(formats)
    except Exception as e:
        # Handle cases where the URL is invalid or yt-dlp fails
        return jsonify({"error": str(e)}), 500


@app.route("/download", methods=["POST"])
def download():
    """Handles the final download request."""
    video_url = request.form.get("url")
    format_id = request.form.get("format_id")

    ydl_opts = {
        "outtmpl": "downloads/%(title)s.%(ext)s",
    }

    # Check if the chosen format is audio to add post-processor
    if format_id == "bestaudio/best":
        ydl_opts["postprocessors"] = [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ]

    # Set the format
    ydl_opts["format"] = format_id

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            title = info.get("title", "Unknown Title")
        return render_template(
            "result.html", message=f"Successfully downloaded: {title}"
        )
    except Exception as e:
        return render_template("result.html", message=f"An error occurred: {str(e)}")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
