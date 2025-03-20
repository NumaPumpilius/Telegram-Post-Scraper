# Telegram Post Scraper

A Python tool for scraping content from Telegram channels without using Telegram's API. This tool allows you to download post content, media (images and videos), and save data in various formats.

## Features

- **Single Post Mode**: Scrape individual Telegram posts (text content, images, videos)
- **Bulk Mode**: Download content from multiple consecutive posts at once
- **No API Required**: Works without Telegram API keys or bot tokens
- **Media Download**: Save images and videos from posts
- **Multiple Output Formats**: Save as text files or JSON
- **Error Handling**: Robust error recovery for missing posts or connection issues

## Changelog

```
Version 4.0:
Release Date: March 20, 2025

- Added bulk download mode for processing multiple consecutive posts
- Added JSON output format for bulk downloads
- Improved error handling for missing posts and network errors
- All saved files now go to a dedicated 'data' folder
- Added command-line argument support with clearer syntax

Version 3.0:
Release Date: Sept 21, 2023

- Rewrote the base code
- Added better error handling
- Converted from async back to sync
- Added basic CLI support
```

## Requirements

- Python 3.10+ (tested on 3.10.10)
- Required packages:
  - beautifulsoup4
  - html2text
  - pyperclip
  - requests

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/Telegram-Post-Scraper.git
   cd Telegram-Post-Scraper
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Usage

### Single Post Mode

To scrape a single Telegram post:

```
python main.py --link https://t.me/channelname/123
```

Or use the short form:

```
python main.py -l https://t.me/channelname/123
```

### Bulk Mode

To download multiple consecutive posts at once:

```
python main.py --bulk https://t.me/channelname/ [start_id] [number_of_posts]
```

For example, to download 10 posts starting from post ID 1000:

```
python main.py --bulk https://t.me/channelname/ 1000 10
```

This will:
- Process all posts from ID 1000 to 1009
- Save only the text content (no media)
- Store the data in a JSON file in the `data/channelname` directory
- Include the post content and date/time for each post

### Interactive Mode

Simply run the program without arguments to enter interactive mode:

```
python main.py
```

## Output

- **Single post mode**: Offers options to copy or save post content and media
- **Bulk mode**: Automatically saves a JSON file with all post content to `data/channelname/`

## Error Handling

The tool handles various error conditions:
- Missing or deleted posts
- Network connectivity issues
- Rate limiting by Telegram
- Malformed post content

## Contributing

Contributions are welcome! Feel free to submit pull requests or open issues.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

Thanks to all contributors who have helped improve this project.