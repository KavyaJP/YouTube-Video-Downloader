import tkinter as tk
from tkinter import ttk, messagebox, font
import yt_dlp
import threading
import queue
import os


class YouTubeDownloaderApp(tk.Tk):
    def __init__(self):
        super().__init__()

        # --- Window Setup ---
        self.title("YouTube Downloader")
        self.geometry("700x600")
        self.configure(bg="#2E2E2E")

        # --- Style Configuration ---
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background="#2E2E2E")
        style.configure(
            "TLabel", background="#2E2E2E", foreground="#FFFFFF", font=("Roboto", 10)
        )
        style.configure(
            "TButton",
            background="#3b82f6",
            foreground="#FFFFFF",
            font=("Roboto", 10, "bold"),
            borderwidth=0,
        )
        style.map("TButton", background=[("active", "#2563eb")])
        style.configure(
            "TEntry", fieldbackground="#4A4A4A", foreground="#FFFFFF", borderwidth=1
        )
        style.configure(
            "TCombobox", fieldbackground="#4A4A4A", foreground="#FFFFFF", borderwidth=1
        )
        style.configure(
            "Vertical.TScrollbar", background="#4A4A4A", troughcolor="#2E2E2E"
        )
        style.configure(
            "Custom.TCheckbutton",
            background="#4A4A4A",
            foreground="#FFFFFF",
            indicatorcolor="#3b82f6",
        )

        # --- Data Members ---
        self.progress_queue = queue.Queue()
        self.is_playlist = False

        # --- UI Creation ---
        self.create_widgets()

        # Start checking the queue for progress updates
        self.process_queue()

    def create_widgets(self):
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- URL Input Section ---
        url_label = ttk.Label(main_frame, text="YouTube URL:")
        url_label.pack(fill=tk.X, pady=(0, 5))
        self.url_entry = ttk.Entry(main_frame, width=60, font=("Roboto", 11))
        self.url_entry.pack(fill=tk.X)
        self.check_button = ttk.Button(
            main_frame, text="Check Media", command=self.start_media_check
        )
        self.check_button.pack(fill=tk.X, pady=(10, 0))

        # --- Status Label ---
        self.status_label = ttk.Label(
            main_frame, text="Enter a URL and click 'Check Media'", wraplength=600
        )
        self.status_label.pack(fill=tk.X, pady=10)

        # --- Format and Playlist Section ---
        # This frame will hold either the format dropdown or the playlist view
        self.options_frame = ttk.Frame(main_frame)
        self.options_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # --- Download Button ---
        self.download_button = ttk.Button(
            main_frame, text="Download", command=self.start_download, state=tk.DISABLED
        )
        self.download_button.pack(fill=tk.X, pady=(10, 0))

        # --- Progress Bar ---
        self.progress_label = ttk.Label(main_frame, text="")
        self.progress_label.pack(fill=tk.X, pady=(10, 5))
        self.progress_bar = ttk.Progressbar(
            main_frame, orient="horizontal", length=100, mode="determinate"
        )
        self.progress_bar.pack(fill=tk.X)

    def start_media_check(self):
        """Starts the media check in a separate thread to avoid freezing the GUI."""
        url = self.url_entry.get()
        if not url:
            messagebox.showerror("Error", "Please enter a URL.")
            return

        self.status_label.config(text="Analyzing URL...")
        self.check_button.config(state=tk.DISABLED)
        self.download_button.config(state=tk.DISABLED)

        # Clear previous options
        for widget in self.options_frame.winfo_children():
            widget.destroy()

        # Run the check in a thread
        threading.Thread(
            target=self.check_media_thread, args=(url,), daemon=True
        ).start()

    def check_media_thread(self, url):
        """Fetches media info using yt-dlp."""
        try:
            with yt_dlp.YoutubeDL({"quiet": True, "extract_flat": True}) as ydl:
                info = ydl.extract_info(url, download=False)

            if "entries" in info:
                self.is_playlist = True
                self.progress_queue.put(("playlist_info", info))
            else:
                self.is_playlist = False
                with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
                    info = ydl.extract_info(url, download=False)
                self.progress_queue.put(("video_info", info))
        except Exception as e:
            self.progress_queue.put(("error", f"Failed to fetch media info: {e}"))

    def update_ui_with_info(self, info_type, info):
        """Updates the GUI based on the fetched media info."""
        if info_type == "playlist_info":
            self.status_label.config(
                text=f"Playlist Found: {info.get('title', 'Unknown')}"
            )
            self.setup_playlist_view(info["entries"])
            self.setup_quality_selector()  # Also add quality selector for playlists
        elif info_type == "video_info":
            self.status_label.config(
                text=f"Video Found: {info.get('title', 'Unknown')}"
            )
            self.setup_format_selector(info["formats"])

        self.check_button.config(state=tk.NORMAL)
        self.download_button.config(state=tk.NORMAL)

    def setup_format_selector(self, formats):
        """Creates a dropdown for single video formats."""
        format_options = ["Audio Only (Best Quality MP3)"]
        self.format_map = {"Audio Only (Best Quality MP3)": "bestaudio/best"}

        for f in formats:
            if (
                f.get("ext") == "mp4"
                and f.get("vcodec") != "none"
                and f.get("acodec") != "none"
            ):
                height = f.get("height")
                if height in [1080, 720, 480, 360]:
                    filesize = f.get("filesize") or f.get("filesize_approx", 0)
                    filesize_mb = (
                        f"{filesize / 1024 / 1024:.2f} MB"
                        if filesize
                        else "Unknown size"
                    )
                    display_text = f"{height}p - MP4 ({filesize_mb})"
                    format_options.append(display_text)
                    self.format_map[display_text] = f["format_id"]

        self.quality_combo = ttk.Combobox(
            self.options_frame, values=format_options, state="readonly"
        )
        self.quality_combo.pack(fill=tk.X)
        self.quality_combo.set(format_options[0])

    def setup_quality_selector(self):
        """Creates a quality dropdown for playlists."""
        quality_options = [
            "Audio Only (Best Quality MP3)",
            "Video - 720p (MP4)",
            "Video - 480p (MP4)",
        ]
        self.quality_map = {
            "Audio Only (Best Quality MP3)": "bestaudio/best",
            "Video - 720p (MP4)": "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            "Video - 480p (MP4)": "bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        }
        self.quality_combo = ttk.Combobox(
            self.options_frame, values=quality_options, state="readonly"
        )
        self.quality_combo.pack(fill=tk.X, pady=(0, 10))
        self.quality_combo.set(quality_options[1])  # Default to 720p

    def setup_playlist_view(self, entries):
        """Creates a scrollable list of checkboxes for playlist videos."""
        self.video_vars = {}

        list_frame = ttk.Frame(self.options_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(list_frame, bg="#4A4A4A", highlightthickness=0)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # "Select All" checkbox
        select_all_var = tk.BooleanVar(value=True)

        def toggle_all():
            for var in self.video_vars.values():
                var.set(select_all_var.get())

        select_all_cb = ttk.Checkbutton(
            scrollable_frame,
            text="Select All",
            variable=select_all_var,
            command=toggle_all,
            style="Custom.TCheckbutton",
        )
        select_all_cb.pack(anchor="w", padx=5, pady=5)

        for entry in entries:
            var = tk.BooleanVar(value=True)
            self.video_vars[entry["id"]] = var
            cb = ttk.Checkbutton(
                scrollable_frame,
                text=entry.get("title", "Unknown Title"),
                variable=var,
                style="Custom.TCheckbutton",
            )
            cb.pack(anchor="w", padx=5, fill="x")

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def start_download(self):
        """Validates selections and starts the download thread."""
        format_key = self.quality_combo.get()
        format_id = (
            self.format_map.get(format_key)
            if not self.is_playlist
            else self.quality_map.get(format_key)
        )

        if not format_id:
            messagebox.showerror("Error", "Please select a valid quality.")
            return

        video_ids_to_download = []
        if self.is_playlist:
            for video_id, var in self.video_vars.items():
                if var.get():
                    video_ids_to_download.append(video_id)
            if not video_ids_to_download:
                messagebox.showerror(
                    "Error", "Please select at least one video from the playlist."
                )
                return
        else:
            # For a single video, we need to extract its ID first
            try:
                with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
                    info = ydl.extract_info(self.url_entry.get(), download=False)
                video_ids_to_download.append(info["id"])
            except Exception as e:
                messagebox.showerror("Error", f"Could not get video ID: {e}")
                return

        self.download_button.config(state=tk.DISABLED)
        self.check_button.config(state=tk.DISABLED)
        threading.Thread(
            target=self.download_thread,
            args=(video_ids_to_download, format_id),
            daemon=True,
        ).start()

    def download_thread(self, video_ids, format_id):
        """The actual download logic that runs in the background."""
        os.makedirs("downloads", exist_ok=True)
        total_videos = len(video_ids)
        for i, video_id in enumerate(video_ids, 1):
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            self.progress_queue.put(
                ("new_video", f"Downloading video {i} of {total_videos}...")
            )

            ydl_opts = {
                "outtmpl": "downloads/%(title)s.%(ext)s",
                "progress_hooks": [self.progress_hook],
                "format": format_id,
            }
            if format_id == "bestaudio/best":
                ydl_opts["postprocessors"] = [
                    {"key": "FFmpegExtractAudio", "preferredcodec": "mp3"}
                ]

            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([video_url])
            except Exception as e:
                self.progress_queue.put(
                    ("error", f"Failed to download {video_id}: {e}")
                )

        self.progress_queue.put(("batch_finished", "All downloads complete!"))

    def progress_hook(self, d):
        """yt-dlp hook that sends progress to the queue."""
        if d["status"] == "downloading":
            total_bytes = d.get("total_bytes") or d.get("total_bytes_estimate", 0)
            if total_bytes > 0:
                percent = d["downloaded_bytes"] / total_bytes * 100
                self.progress_queue.put(("progress", percent))

    def process_queue(self):
        """Checks the queue for messages and updates the GUI."""
        try:
            message_type, data = self.progress_queue.get_nowait()

            if message_type == "video_info" or message_type == "playlist_info":
                self.update_ui_with_info(message_type, data)
            elif message_type == "new_video":
                self.progress_label.config(text=data)
                self.progress_bar["value"] = 0
            elif message_type == "progress":
                self.progress_bar["value"] = data
            elif message_type == "batch_finished":
                self.status_label.config(text=data)
                self.progress_label.config(text="")
                self.download_button.config(state=tk.NORMAL)
                self.check_button.config(state=tk.NORMAL)
                messagebox.showinfo(
                    "Success", "All selected media has been downloaded."
                )
            elif message_type == "error":
                self.status_label.config(text=f"Error: {data}")
                messagebox.showerror("Error", data)
                self.download_button.config(state=tk.NORMAL)
                self.check_button.config(state=tk.NORMAL)

        except queue.Empty:
            pass  # No messages, just continue

        # Schedule this method to run again after 100ms
        self.after(100, self.process_queue)


if __name__ == "__main__":
    app = YouTubeDownloaderApp()
    app.mainloop()
