# oCF.py - File Crawler Bot

![GitHub License](https://img.shields.io/github/license/TheOSuite/oCF)
![Python Version](https://img.shields.io/badge/python-3.13-blue)
![Last Updated](https://img.shields.io/date/2025-07-21)

This is a GUI-based Python script that crawls a website starting from a given URL, identifies and downloads files with common downloadable extensions using a breadth-first search (BFS) approach for improved performance.

## Features
- **GUI Interface:** Intuitive graphical interface built with Tkinter.
- **Website Crawling:** Navigates links within the same domain, with configurable max depth and max pages limits to control scope.
- **File Identification:** Detects files based on extensions and MIME types (e.g., PDFs, documents, images, media, archives).
- **File Downloading:** Downloads files concurrently using a thread pool for efficiency, saving to a user-selected folder.
- **Pause and Stop Functionality:** Pause/resume or stop the crawl at any time.
- **Progress Indicator:** Indeterminate progress bar during operation.
- **Logging:** Real-time logs in the GUI, with enhanced error details including tracebacks.
- **Export Logs:** Button to save logs to a .txt file for reporting.
- **Rate Limiting:** Built-in delays between requests to respect servers.
- **Custom Headers:** Uses a custom User-Agent for requests.
- **URL Normalization:** Strips fragments to avoid duplicate visits.
- **Non-HTML Handling:** Checks content types to download files without extensions.

## Requirements
- Python 3.x (tested on 3.12)
- `requests` library (`pip install requests`)
- `beautifulsoup4` library (`pip install beautifulsoup4`) – optionally `lxml` for faster parsing (`pip install lxml`)
- Tkinter (included in standard Python installations)
- Standard libraries: os, threading, time, concurrent.futures, traceback, urllib.parse, ttk (no additional installs needed)

## Installation
1. Clone or download the `oCF.py` file.
2. Install required libraries:
   ```
   pip install requests beautifulsoup4 lxml
   ```

## How to Use
1. Run the script:
   ```
   python oCF.py
   ```
2. Enter the **Start URL** (e.g., `https://www.example.com` – must start with http/https).
3. Enter **Max Depth** (0 for unlimited) to limit recursion depth.
4. Enter **Max Pages** (0 for unlimited) to cap total visited pages.
5. Click **Select Save Folder** to choose where files save (defaults to current directory).
6. Click **Start Crawl** to begin.
7. Monitor the log area for activity, visited URLs, and downloads.
8. Use **Pause/Resume** and **Stop Crawl** as needed.
9. After completion, use **Export Logs** to save the log to a file.

## How it Works
The script uses BFS with a queue to crawl pages, starting from the provided URL. It normalizes URLs to avoid duplicates and respects domain boundaries.

For each URL:
- Fetches content with a custom User-Agent and timeout.
- Applies rate limiting (0.5s delay).
- If non-HTML (via content-type), checks if downloadable via MIME mapping and queues for download.
- For HTML, extracts links from various tags (a, img, etc.) using BeautifulSoup (lxml preferred, fallback to html.parser).
- Enqueues same-domain links if within max depth/pages.
- Downloads are offloaded to a thread pool (max 5 workers) for concurrency, streaming content to avoid memory issues.

Visited URLs are tracked in a set. Pause/stop flags are checked frequently for responsiveness.

## Customization
Modify `DOWNLOADABLE_EXTENSIONS` for file types:
```python
DOWNLOADABLE_EXTENSIONS = {'.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
                           '.jpg', '.jpeg', '.png', '.gif', '.mp3', '.mp4', '.zip', '.rar', '.exe', '.apk'}
```
Expand MIME mappings in `is_downloadable` for more types. Adjust thread pool workers or rate limit sleep time as needed.

## Important Notes
- **Ethical Use:** Always obtain permission before crawling. Respect robots.txt and terms of service. This tool is for ethical hacking/auditing.
- **Rate Limiting:** Implemented with 0.5s delays; adjust for slower/faster crawls.
- **Concurrency:** Downloads run in parallel, but crawling is sequential to maintain BFS order. Large sites may consume threads/resources.
- **Error Handling:** Robust with tracebacks in logs; handles timeouts and exceptions gracefully.
- **Limitations:** No robots.txt support yet; deep/large sites may timeout or exceed memory if unlimited.
- **Timeouts:** 5s for page fetches, 10s for downloads – tunable in code.
