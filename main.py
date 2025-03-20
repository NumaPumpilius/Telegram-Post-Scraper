import asyncio
import os
import re
import time
import json
import argparse
from datetime import datetime
from bs4 import BeautifulSoup
import html2text
import requests
import pyperclip

class TeleScraper:
    def __init__(self, link=None, bulk_mode=False, start_id=None, num_posts=None):        
        if link:
            self.postURL = link
        else:
            self.postURL = input('Please enter the Telegram post URL:\n > ')
        
        self.bulk_mode = bulk_mode
        self.start_id = start_id
        self.num_posts = num_posts
        
        self.urlSplit = self.postURL.split(',')
        self.urlList = [entry + '?embed=1&mode=tme' for entry in self.urlSplit]
        self.imageUrls = []
        self.videoUrls = []
        self.imageFound = None
        self.author = ""
        self.content = ""
        self.dateTime = ""
        self.bulkContent = ""
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36 TelegramBot (like TwitterBot)'
        }
        
    def clClr(self):
        match(os.name):
            case 'nt':
                os.system('cls')
            case _:
                os.system('clear')
    
    def html_to_text(self, html):
        h = html2text.HTML2Text()
        h.body_width = 0  # Disable line wrapping
        h.ignore_links = False  # Ignore hyperlinks
        h.ignore_emphasis = True  # Ignore bold and italic formatting
        h.ignore_images = True  # Ignore images
        h.protect_links = True  # Protect hyperlinks from being stripped out
        h.unicode_snob = True  # Use Unicode characters instead of ASCII
        h.wrap_links = False  # Disable link wrapping
        h.wrap_lists = False  # Disable list wrapping
        h.decode_errors = 'ignore'  # Ignore Unicode decoding errors

        text = h.handle(html)
        text = re.sub(r'\*+', '', text)  # Remove asterisks
        text = re.sub(r'^[ \t]*[\\`]', '', text, flags=re.MULTILINE)  # Remove leading \ or `
        return text    
        
    async def run_bulk(self):
        """Process multiple posts in bulk mode"""
        base_url = self.postURL.rstrip("/")
        posts_data = []
        success_count = 0
        error_count = 0
        missing_count = 0
        
        for i in range(self.num_posts):
            post_id = self.start_id + i
            url = f"{base_url}/{post_id}?embed=1&mode=tme"
            print(f"Processing post {i+1}/{self.num_posts}: {url}")
            
            try:
                linkReq = requests.get(url=url, headers=self.headers)
                linkReq.raise_for_status()
                linkHTML = BeautifulSoup(linkReq.text, 'html.parser')
                
                # Handle the case where post content might be None
                content_element = linkHTML.find('div', {'class': 'tgme_widget_message_text js-message_text', 'dir': 'auto'})
                content = self.html_to_text(str(content_element)) if content_element else ""
                
                # Get date and time with error handling
                datetime_container = linkHTML.find('span', {'class': 'tgme_widget_message_meta'})
                time_element = datetime_container.find('time', {'class': 'datetime'}) if datetime_container else None
                date_time = self.html_to_text(str(time_element)) if time_element else ""
                
                # Check if post is missing (no content AND no date)
                # Some posts might have empty content but still have a date
                if not date_time:
                    print(f"Post {post_id} appears to be missing")
                    missing_count += 1
                    continue
                
                # Add post data to our collection
                posts_data.append({
                    "post_id": post_id,
                    "content": content,
                    "dateTime": date_time
                })
                
                success_count += 1
                # Small delay to avoid rate limiting
                time.sleep(0.5)
                
            except requests.exceptions.RequestException as err:
                print(f"Error processing post {post_id}: {err}")
                error_count += 1
                continue
            except AttributeError as err:
                print(f"Error parsing post {post_id}: {err}")
                error_count += 1
                continue
            except Exception as err:
                print(f"Unexpected error processing post {post_id}: {err}")
                error_count += 1
                continue
        
        # Save the collected data to a JSON file if any posts were successfully processed
        if posts_data:
            url_data = base_url.split('/')
            main_folder = url_data[-1]
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            
            # Create data folder if it doesn't exist
            data_folder = "data"
            if not os.path.exists(data_folder):
                os.makedirs(data_folder)
            
            # Create subfolder for the channel inside data folder
            channel_folder = os.path.join(data_folder, main_folder)
            if not os.path.exists(channel_folder):
                os.makedirs(channel_folder)
                
            file_path = os.path.join(channel_folder, f"{main_folder}-bulk-{self.start_id}-{self.start_id+self.num_posts-1}-{timestamp}.json")
            
            with open(file_path, "w", encoding="utf-8") as file:
                json.dump(posts_data, file, ensure_ascii=False, indent=2)
                
            print(f"Bulk data saved to {os.path.abspath(file_path)}")
            print(f"Summary: Attempted {self.num_posts} posts, {success_count} successful, {error_count} failed, {missing_count} missing")
        else:
            print("No valid posts were found, no output file created.")
    
    async def run(self):
        def appendImageUrls(urlList):
            for div in urlList:
                        style = div['style']
                        match = re.search(r"background-image:url\('(.*)'\)", style)
                        if match:
                            bg_image_url = match.group(1)
                            self.imageUrls.append(bg_image_url)
            
        def appendVideoUrls(linkHTML):
            video_tags = linkHTML.find_all('video')
            for video in video_tags:
                src = video.get('src')
                if src:
                    self.videoUrls.append(src)
        
        def postTextHandler():
            time.sleep(1)
            self.clClr()
            print(f'Text Contents Of Post'.center(80))
            print(f'{self.content}'.center(80))
            #print()
            url_data = self.postURL.split('/')
            main_folder = url_data[-2]
            post_id = url_data[-1]
            bulkData = f'Author: {self.author}\nDate / Time: {self.dateTime}\nContent: \n{self.content}'
            match(input('[TG Scraper] Would you like to:\n1. Copy Post Contents\n2. Save Post Contents\n3. Copy Bulk Data\n4. Save Bulk Content\nSelection: ')):
                case '1':
                    pyperclip.copy(str(self.content))
                case '2':
                    pyperclip.copy(bulkData)
                case '3':
                    if not os.path.exists(main_folder):
                        os.makedirs(main_folder)
                    file_path = os.path.join(main_folder, f"{main_folder}-{post_id}", f"{main_folder}-Post-Content.txt")
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    with open(file_path, "w", encoding="utf-8") as file:
                        file.writelines(self.content)
                case '4':
                    if not os.path.exists(main_folder):
                        os.makedirs(main_folder)
                    file_path = os.path.join(main_folder, f"{main_folder}-{post_id}", f"{main_folder}-Bulk-Content.txt")
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    with open(file_path, "w", encoding="utf-8") as file:
                        file.writelines(bulkData)
                case _:
                    print('[TG Scraper] Invalid Selection!');time.sleep(0.5);self.clClr();postTextHandler()
        def downloadMedia(img, vid, mediaType):
            def download(file_type):
                url_data = self.postURL.split('/')
                main_folder = url_data[-2]
                post_id = url_data[-1]

                if not os.path.exists(main_folder):
                    os.makedirs(main_folder)

                if file_type == 'img':
                    array_to_watch = self.imageUrls
                    file_extension = '.jpg'
                elif file_type == 'vid':
                    array_to_watch = self.videoUrls
                    file_extension = '.mp4'
                else:
                    print('Invalid file type')
                    return

                for file_num, url in enumerate(array_to_watch, start=1):
                    file_path = os.path.join(main_folder, f"{main_folder}-{post_id}", f"{file_type}-{self.dateTime}-{file_num}{file_extension}")

                    #if os.path.exists(file_path):
                    #    print(f"File {file_num} already exists at {os.path.abspath(file_path)}")
                    #else:
                    response = requests.get(url)
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    with open(file_path, 'wb') as f:
                        f.write(response.content)

                    print(f"File {file_num} downloaded to {os.path.abspath(file_path)}")
            if not any([img, vid]):
                print("[TG Scraper] Why are you trying to download media from a post with no media? Skill issue, imo.")
                return
            if len(img) <= 0:
                print('[TG Scraper] No images found! Skipping...')
            if len(vid) <= 0:
                print('[TG Scraper] No videos found! Skipping...')
            match(mediaType):
                case 'img':
                    for link in img:
                        print(f'[TG Scraper] Downloading {len(self.imageUrls)} image(s).')
                        download('img')
                case 'vid':
                    for link in vid:
                        print(f'[TG Scraper] Downloading {len(self.imageUrls)} video(s).')
                        download('vid')
                case _:
                    for link in vid:
                        print(f'[TG Scraper] Downloading {len(self.imageUrls)} video(s).')
                        download('vid')
                    for link in img:
                        print(f'[TG Scraper] Downloading {len(self.imageUrls)} image(s).')
                        download('img')
            postTextHandler()
            
        def mediaDLPrompt():
            match(input('[TG Scraper] Would you like to download the media?\nYou can select images or videos.\n[Y] - Download Media | [N] - Proceed To PostHandler\nSelection: ').upper()):
                case 'Y':
                    match(input('[TG Scraper] 1. Download Videos Exclusively\n2. Download Images Exclusively\n3. Download Images & Videos\nSelection: ')):
                        case '1':    
                            downloadMedia(img=self.imageUrls,vid=self.videoUrls,mediaType='vid')
                        case '2':
                            downloadMedia(img=self.imageUrls,vid=self.videoUrls,mediaType='img')
                        case _:
                            downloadMedia(img=self.imageUrls,vid=self.videoUrls,mediaType='both')
                case 'N':
                    postTextHandler()
                case _:
                    self.clClr()
                    print('Invalid selection!')
                    time.sleep(0.5);self.clClr()
                    mediaDLPrompt()
        try:
            for link in self.urlList:
                print(link)
                linkReq = requests.get(url=link,headers=self.headers); linkReq.raise_for_status()
                linkHTML = BeautifulSoup(linkReq.text, 'html.parser')
                self.content = self.html_to_text(str(linkHTML.find('div', {'class': 'tgme_widget_message_text js-message_text', 'dir': 'auto'})))
                self.author = self.html_to_text(str(linkHTML.find('div', {'class': 'tgme_widget_message_author accent_color'}).find('a', {'class': 'tgme_widget_message_owner_name'}).find('span', {'dir': 'auto'})))
                self.dateTime = self.html_to_text(str(linkHTML.find('span', {'class': 'tgme_widget_message_meta'}).find('time', {'class': 'datetime'})))
                imgCt = linkHTML.findAll('a', {'class': 'tgme_widget_message_photo_wrap'})
                vidUrls = linkHTML.findAll('div', {'class': 'tgme_widget_message_video_wrap'}) 
                if len(imgCt) > 0 or len(vidUrls) > 0:
                    print(f'[TG Scraper] Found {len(imgCt)} image(s) and {len(vidUrls)} video(s).')
                    appendImageUrls(imgCt)
                    appendVideoUrls(linkHTML)
                    mediaDLPrompt()
                else:
                    print('No Media Found. Continuing to PostHandler.')
                    time.sleep(0.25)
                    postTextHandler()
                    
        except requests.exceptions.RequestException as err:
            print(err)

def parse_arguments():
    parser = argparse.ArgumentParser(description='Telegram Post Scraper')
    parser.add_argument('-l', '--link', help='URL of the Telegram post to scrape')
    parser.add_argument('--bulk', help='Base URL for bulk processing (format: https://t.me/somegroup/)')
    parser.add_argument('start', type=int, nargs='?', help='Starting post ID for bulk processing')
    parser.add_argument('number', type=int, nargs='?', help='Number of posts to process in bulk mode')
    
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_arguments()
    
    if args.bulk and args.start is not None and args.number is not None:
        _scraper = TeleScraper(link=args.bulk, bulk_mode=True, start_id=args.start, num_posts=args.number)
        asyncio.run(_scraper.run_bulk())
    elif args.link:
        _scraper = TeleScraper(link=args.link)
        asyncio.run(_scraper.run())
    else:
        _scraper = TeleScraper()
        asyncio.run(_scraper.run())