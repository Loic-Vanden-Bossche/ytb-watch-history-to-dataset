import sys
import csv
import os
import re
import time  # Import time module for tracking durations
from datetime import datetime

import pytz
from bs4 import BeautifulSoup
from yt_dlp import YoutubeDL
from colorama import Fore, Style
import json
from concurrent.futures import ThreadPoolExecutor, as_completed


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
            channel_follower_count,
            channel_is_verified]


def parse_html(input_file, output_file, resume=False):
    with open(input_file, "r", encoding="utf-8") as f:
        contents = f.read()

    soup = BeautifulSoup(contents, 'lxml')
    divs = soup.find_all('div', {'class': 'content-cell mdl-cell mdl-cell--6-col mdl-typography--body-1'})

    total_videos = len(divs)

    print(f"{Fore.GREEN}Number of videos: {total_videos}{Style.RESET_ALL}")

    if resume:
        last_processed_index = get_last_processed_index(output_file)
        if last_processed_index is None:
            print(
                f"{Fore.YELLOW}Unable to determine the last processed index. Resuming from the beginning.{Style.RESET_ALL}")
            last_processed_index = 0
        else:
            last_processed_index += 1
        divs = divs[last_processed_index:]

    with open(output_file, 'a', newline='', encoding="utf-8") as file:
        writer = csv.writer(file)

        if last_processed_index == 0:
            writer.writerow(
                ['url', 'watch_timestamp', 'video_id', 'fulltitle', 'thumbnail', 'description', 'channel_id',
                 'duration',
                 'view_count', 'age_limit', 'categories', 'tags', 'live_status', 'release_timestamp', 'comment_count',
                 'heatmap', 'like_count', 'channel', 'channel_follower_count', 'channel_is_verified'])

        processed_videos = 0

        print(f"{Fore.MAGENTA}Starting...{Style.RESET_ALL}")

        start_time = time.time()


        with ThreadPoolExecutor(max_workers=16) as executor:
            future_to_url = {executor.submit(get_metadata,
                                             div.find('a', href=re.compile(r'https://www.youtube.com/watch\?v=.+'))[
                                                 'href']): div for div in divs if
                             div.find('a', href=re.compile(r'https://www.youtube.com/watch\?v=.+'))}

            for index, future in enumerate(as_completed(future_to_url), start=last_processed_index):
                div = future_to_url[future]
                link = div.find('a', href=re.compile(r'https://www.youtube.com/watch\?v=.+'))

                if link:
                    url = link['href']
                    try:
                        meta = future.result()

                        if meta is None:
                            continue

                        text_content = div.get_text()

                        # Split the text to isolate the date and time
                        lines = text_content.split('\n')
                        date_time_str = lines[-2].strip()

                        date_time_str = date_time_str.replace(' CEST', '')

                        month_map = {
                            'janv.': 'Jan',
                            'févr.': 'Feb',
                            'mars': 'Mar',
                            'avr.': 'Apr',
                            'mai': 'May',
                            'juin': 'Jun',
                            'juil.': 'Jul',
                            'août': 'Aug',
                            'sept.': 'Sep',
                            'oct.': 'Oct',
                            'nov.': 'Nov',
                            'déc.': 'Dec'
                        }

                        for fr_month, en_month in month_map.items():
                            if fr_month in date_time_str:
                                date_time_str = date_time_str.replace(fr_month, en_month)
                                break

                        date_time_format = "%d %b %Y, %H:%M:%S"
                        date_time_obj = datetime.strptime(date_time_str, date_time_format)

                        timezone = pytz.timezone('Europe/Paris')
                        date_time_obj = timezone.localize(date_time_obj)

                        timestamp = int(date_time_obj.timestamp())

                        row = [url, timestamp] + get_row(meta)
                        writer.writerow(row)
                        print(f"{Fore.GREEN}Parsed: {url}{Style.RESET_ALL}")

                        processed_videos += 1

                    except Exception as e:
                        print(f"{Fore.RED}Error processing {url}: {e}{Style.RESET_ALL}")

                end_time = time.time()
                duration = end_time - start_time

                save_last_processed_index(output_file, index)

                if processed_videos > 0:
                    average_processing_time = duration / processed_videos
                    remaining_videos = total_videos - (index + 1)
                    estimated_remaining_time = average_processing_time * remaining_videos

                    total_minutes = estimated_remaining_time // 60
                    seconds = estimated_remaining_time % 60
                    hours = total_minutes // 60
                    minutes = total_minutes % 60

                    if hours > 0:
                        time_str = f"Finish in {int(hours)} hour{'s' if hours > 1 else ''}"
                        if minutes > 0:
                            time_str += f" and {int(minutes)} minute{'s' if minutes > 1 else ''}"
                        if seconds > 0 and minutes == 0:
                            time_str += f" and {int(seconds)} second{'s' if seconds > 1 else ''}"
                    else:
                        if minutes > 0:
                            time_str = f"Finish in {int(minutes)} minute{'s' if minutes > 1 else ''}"
                        else:
                            time_str = f"Finish in {int(seconds)} second{'s' if seconds > 1 else ''}"

                    print(f'{Fore.CYAN}{index + 1}/{total_videos} {Fore.MAGENTA}avg.{"%.2f" % average_processing_time}s {Fore.YELLOW}{time_str}{Style.RESET_ALL}')

    print(f"{Fore.GREEN}Parsing complete.{Style.RESET_ALL}")


def get_last_processed_index(output_file):
    progress_file = f"{output_file}.progress"
    if os.path.exists(progress_file):
        with open(progress_file, 'r') as file:
            last_index = file.read()
            if last_index.isdigit():
                return int(last_index)
    return None


def save_last_processed_index(output_file, index):
    progress_file = f"{output_file}.progress"
    with open(progress_file, 'w') as file:
        file.write(str(index))


def main(input_file, output_file):
    parse_html(input_file, output_file, resume=True)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
