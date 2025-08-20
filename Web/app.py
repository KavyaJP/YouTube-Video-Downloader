from flask import Flask, render_template, request, jsonify, Response
import yt_dlp
import os
import threading
import queue
import json

app = Flask(__name__)
os.makedirs("downloads", exist_ok=True)

# A thread-safe queue to hold progress updates
progress_queue = queue.Queue()


def my_hook(d):
    """
    The yt-dlp hook. It's called for each progress update.
    We'll put a dictionary with the progress into our queue.
    """
    if d["status"] == "downloading":
        total_bytes = d.get("total_bytes") or d.get("total_bytes_estimate", 0)
        if total_bytes > 0:
            percent = d["downloaded_bytes"] / total_bytes * 100
            progress_queue.put(
                json.dumps(
                    {
                        "status": "downloading",
                        "percent": f"{percent:.1f}",
                    }
                )
            )
    elif d["status"] == "finished":
        full_path = d.get("info_dict", {}).get("filename", d.get("filename"))
        base_filename = os.path.basename(full_path) if full_path else "Unknown file"
        progress_queue.put(
            json.dumps({"status": "finished", "filename": base_filename})
        )


def download_threaded(url, format_id):
    """
    This function will run in a separate thread to not block the web server.
    """
    ydl_opts = {
        "outtmpl": "downloads/%(title)s.%(ext)s",
        "progress_hooks": [my_hook],
        "format": format_id,
    }

    if format_id == "bestaudio/best":
        ydl_opts["postprocessors"] = [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ]

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        progress_queue.put(json.dumps({"status": "error", "message": str(e)}))


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/get-formats", methods=["POST"])
def get_formats():
    # This function remains the same as before
    video_url = request.json.get("url")
    if not video_url:
        return jsonify({"error": "URL is required."}), 400
    try:
        ydl_opts = {"quiet": True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
        format_options = [
            {"id": "bestaudio/best", "text": "Audio Only (Best Quality MP3)"}
        ]
        target_resolutions = [1080, 720, 480, 360]
        found_resolutions = set()
        for f in info.get("formats", []):
            if (
                f.get("ext") == "mp4"
                and f.get("vcodec") != "none"
                and f.get("acodec") != "none"
            ):
                height = f.get("height")
                if height in target_resolutions and height not in found_resolutions:
                    filesize = f.get("filesize") or f.get("filesize_approx", 0)
                    filesize_mb = (
                        f"{filesize / 1024 / 1024:.2f} MB"
                        if filesize
                        else "Unknown size"
                    )
                    format_options.append(
                        {
                            "id": f["format_id"],
                            "text": f"{height}p - MP4 ({filesize_mb})",
                        }
                    )
                    found_resolutions.add(height)
        return jsonify(format_options)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/download", methods=["POST"])
def download():
    """
    This route now just starts the download in a new thread.
    """
    video_url = request.form.get("url")
    format_id = request.form.get("format_id")

    # Start the download function in a new thread
    thread = threading.Thread(target=download_threaded, args=(video_url, format_id))
    thread.start()

    # Immediately return a response to the user
    return jsonify({"status": "started"})


@app.route("/progress-stream")
def progress_stream():
    """
    This is the Server-Sent Event stream. The browser will connect to this.
    It's a generator function that yields progress updates.
    """

    def generate():
        while True:
            # Wait for a message in the queue
            message = progress_queue.get()
            # Yield the message in the SSE format
            yield f"data: {message}\n\n"

            # If the message indicates the end, break the loop
            data = json.loads(message)
            if data["status"] in ["finished", "error"]:
                break

    # Return a streaming response
    return Response(generate(), mimetype="text/event-stream")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
