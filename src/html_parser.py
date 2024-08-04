import csv
import re
import time
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import pytz
from colorama import Fore, Style

from metadata import get_metadata, get_row
from progress import get_last_processed_index, save_last_processed_index
from utils import format_estimated_time


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
            print(f"{Fore.YELLOW}Unable to determine the last processed index. Resuming from the beginning.{Style.RESET_ALL}")
            last_processed_index = 0
        else:
            last_processed_index += 1
        divs = divs[last_processed_index:]

    with open(output_file, 'a', newline='', encoding="utf-8") as file:
        writer = csv.writer(file)

        if last_processed_index == 0:
            writer.writerow(
                ['url', 'watch_timestamp', 'video_id', 'fulltitle', 'thumbnail', 'description', 'channel_id', 'duration',
                 'view_count', 'age_limit', 'categories', 'tags', 'live_status', 'release_timestamp', 'comment_count',
                 'heatmap', 'like_count', 'channel', 'channel_follower_count', 'channel_is_verified'])

        processed_videos = 0
        print(f"{Fore.MAGENTA}Starting...{Style.RESET_ALL}")
        start_time = time.time()

        with ThreadPoolExecutor(max_workers=16) as executor:
            future_to_url = {executor.submit(get_metadata,
                                             div.find('a', href=re.compile(r'https://www.youtube.com/watch\?v=.+'))['href']): div for div in divs if
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
                        lines = text_content.split('\n')
                        date_time_str = lines[-2].strip()
                        date_time_str = date_time_str.replace(' CEST', '')

                        month_map = {
                            'janv.': 'Jan', 'févr.': 'Feb', 'mars': 'Mar', 'avr.': 'Apr', 'mai': 'May', 'juin': 'Jun',
                            'juil.': 'Jul', 'août': 'Aug', 'sept.': 'Sep', 'oct.': 'Oct', 'nov.': 'Nov', 'déc.': 'Dec'
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

                    time_str = format_estimated_time(estimated_remaining_time)
                    print(f'{Fore.CYAN}{index + 1}/{total_videos} {Fore.MAGENTA}avg.{"%.2f" % average_processing_time}s {Fore.YELLOW}{time_str}{Style.RESET_ALL}')

    print(f"{Fore.GREEN}Parsing complete.{Style.RESET_ALL}")