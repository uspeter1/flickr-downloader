# Flickr Album Downloader

A Python script that uses Selenium to scrape and download all images from Flickr albums with multithreading support.

## Features

- Downloads all images from Flickr albums across multiple pages
- Multithreaded downloads for faster performance
- Handles rate limiting with random retry intervals
- Converts thumbnail URLs to higher resolution versions
- Automatic pagination through album pages

## Installation

1. Clone the repository:
```bash
git clone git@github.com:uspeter1/flickr-downloader.git
cd flickr-downloader
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the script:
```bash
python scrape.py
```

Enter the Flickr album URL when prompted and optionally specify:
- Output folder name (default: downloaded_images)
- Number of download threads (default: 10)

## Requirements

- Python 3.6+
- Chrome browser (ChromeDriver is automatically managed)
- Internet connection