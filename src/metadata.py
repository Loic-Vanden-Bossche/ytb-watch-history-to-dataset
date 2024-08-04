import json
from yt_dlp import YoutubeDL
from colorama import Fore, Style


def get_metadata(url):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
        'forceurl': True,
        'forcetitle': True,
        'forcedescription': True,
        'writeinfojson': True,
        'simulate': True,
        'youtube_include_dash_manifest': False
    }

    with YoutubeDL(ydl_opts) as ydl:
        try:
            meta = ydl.extract_info(url, download=False)
            return meta
        except Exception:
            print(f"{Fore.RED}Failed to get metadata for {url}{Style.RESET_ALL}")
            return None


def get_row(meta):
    video_id = meta.get('id', "")
    fulltitle = meta.get('fulltitle', "")
    thumbnail = meta.get('thumbnail', "")
    description = meta.get('description', "")
    channel_id = meta.get('channel_id', "")
    duration = str(meta.get('duration', ""))
    view_count = str(meta.get('view_count', ""))
    age_limit = str(meta.get('age_limit', ""))
    categories = ", ".join(meta.get('categories', []))
    tags = ", ".join(meta.get('tags', []))
    live_status = meta.get('live_status', "")
    timestamp = str(meta.get('timestamp', ""))
    comment_count = str(meta.get('comment_count', ""))
    heatmap = json.dumps(meta.get('heatmap', {}))
    like_count = str(meta.get('like_count', ""))
    channel = meta.get('channel', "")
    channel_follower_count = str(meta.get('channel_follower_count', ""))
    channel_is_verified = str(meta.get('channel_is_verified', ""))

    return [video_id, fulltitle, thumbnail, description, channel_id, duration, view_count, age_limit,
            categories, tags, live_status, timestamp, comment_count, heatmap, like_count, channel,
            channel_follower_count, channel_is_verified]
