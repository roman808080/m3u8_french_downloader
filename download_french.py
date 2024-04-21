import sys
import subprocess
import requests
import m3u8


def download_video(master_url, output_file):
    # Fetch the master playlist
    response = requests.get(master_url)
    if response.status_code != 200:
        print("Failed to download the master playlist.")
        return

    # Parse the master playlist
    master_playlist = m3u8.loads(response.text)

    # Find subtitles for French language
    french_subtitle_uri = None
    for media in master_playlist.media:
        print(media.type, media.language)
        if media.type == 'SUBTITLES' and media.language == 'fr':
            french_subtitle_uri = media.uri
            break

    if french_subtitle_uri is None:
        print("No French subtitles found.")
        return

    # Resolve relative URL if necessary
    if not french_subtitle_uri.startswith("http"):
        from urllib.parse import urljoin
        french_subtitle_uri = urljoin(master_url, french_subtitle_uri)

    # Download the video
    video_cmd = [
        'ffmpeg',
        '-i', master_url,
        '-c', 'copy',
        '-bsf:a', 'aac_adtstoasc',
        f'{output_file}.mp4'
    ]
    subprocess.run(video_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Download subtitles using the resolved URI
    subtitle_cmd = [
        'ffmpeg',
        '-i', french_subtitle_uri,
        '-map', '0:s:0',
        '-c:s', 'webvtt',
        f'{output_file}.vtt'
    ]
    subprocess.run(subtitle_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python script.py <master_url> <output_file_base>")
        sys.exit(1)
    master_url = sys.argv[1]
    output_file = sys.argv[2]
    download_video(master_url, output_file)

