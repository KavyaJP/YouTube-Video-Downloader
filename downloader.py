import yt_dlp
import os
import sys


def my_hook(d):
    """
    Hook function for yt-dlp to only show a message when a download is finished.
    yt-dlp's default progress bar will be used during the download.
    """
    if d["status"] == "finished":
        # Get the final filename from the info_dict if available
        filename = d.get("info_dict", {}).get("filename", d.get("filename"))
        print(f"\n✅ Download finished: {filename}")


def select_format(info_dict):
    """
    Lists available formats and asks the user to select one.
    """
    print("\nAvailable Formats:")
    formats = info_dict.get("formats", [])
    for f in formats:
        filesize = f.get("filesize") or f.get("filesize_approx")
        if filesize:
            filesize_mb = filesize / 1024 / 1024
            print(
                f"  ID: {f['format_id']:<5} | Ext: {f['ext']:<5} | Resolution: {f.get('resolution', 'audio only'):<15} | Size: {filesize_mb:7.2f} MB"
            )

    format_id = input(
        "Enter the format ID (e.g., '137+140' to combine best video and audio, or just one ID): "
    ).strip()
    return format_id


def download_media(url):
    """
    Main function to handle the download process.
    """
    # Create downloads directory if it doesn't exist
    os.makedirs("downloads", exist_ok=True)

    print("\nWhat do you want to download?")
    print("  1. Best Quality Video (MP4)")
    print("  2. Audio Only (MP3)")
    print("  3. Let me choose a specific format")
    choice = input("Enter your choice (1, 2, or 3): ").strip()

    base_ydl_opts = {
        "progress_hooks": [my_hook],
        "outtmpl": "downloads/%(title)s.%(ext)s",
    }

    if choice == "1":
        base_ydl_opts["format"] = (
            "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"
        )
    elif choice == "2":
        base_ydl_opts["format"] = "bestaudio/best"
        base_ydl_opts["postprocessors"] = [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ]
    elif choice == "3":
        try:
            with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
                info_dict = ydl.extract_info(url, download=False)

            selected_format = select_format(info_dict)
            if not selected_format:
                print("No format selected. Aborting.")
                return
            base_ydl_opts["format"] = selected_format
        except Exception as e:
            print(f"\n❌ Error fetching formats: {e}")
            return
    else:
        print("Invalid choice. Please enter 1, 2, or 3.")
        return

    try:
        with yt_dlp.YoutubeDL({"quiet": True, "extract_flat": True}) as ydl:
            info = ydl.extract_info(url, download=False)
            if "entries" in info and info.get("extractor_key") != "Youtube":
                playlist_count = len(info["entries"])
                confirm = input(
                    f"\nThis is a playlist with {playlist_count} videos. Download all? (y/n): "
                ).lower()
                if confirm != "y":
                    print("Aborting playlist download.")
                    return
    except Exception as e:
        print(f"\nCould not verify URL. Proceeding anyway. Error: {e}")

    print("\n🚀 Starting download...")
    try:
        with yt_dlp.YoutubeDL(base_ydl_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        print(f"\n\n❌ An error occurred during download: {e}")


if __name__ == "__main__":
    print("--- Full-Powered YouTube Downloader ---")
    try:
        while True:
            video_url = input(
                "\nEnter the YouTube video or playlist URL (or 'q' to quit): "
            )
            if video_url.lower() == "q":
                break
            if not video_url:
                continue

            download_media(video_url)

            another = input("\nDownload another? (y/n): ").lower()
            if another != "y":
                break
    except KeyboardInterrupt:
        print("\nExiting gracefully.")
    print("\nGoodbye!")
