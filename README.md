# eCF

This is a simple GUI-based Python script that crawls a website starting from a given URL, identifies and downloads files with common downloadable extensions.

## Features

*   **GUI Interface:** Easy to use graphical interface built with Tkinter.
*   **Website Crawling:** Navigates links within the same domain to discover pages and files.
*   **File Identification:** Detects links to files based on common file extensions (PDF, documents, spreadsheets, images, audio, video, archives, executables).
*   **File Downloading:** Downloads the identified files to a specified local folder.
*   **Pause and Stop Functionality:** Allows pausing and stopping the crawling process.
*   **Progress Indicator:** Shows an indeterminate progress bar while crawling.
*   **Logging:** Logs activity and download status to the GUI.
*   **Download Folder Selection:** Allows the user to choose where to save the downloaded files.

## Requirements

*   Python 3.x
*   `requests` library (`pip install requests`)
*   `beautifulsoup4` library (`pip install beautifulsoup4`)
*   `tkinter` (usually included with standard Python installations)

## Installation

1.  **Clone or download the script:** Get the `eCF.py` file.
2.  **Install required libraries:** Open your terminal or command prompt and run:
    ```bash
    pip install requests beautifulsoup4
    ```

## How to Use

1.  **Run the script:** Open your terminal or command prompt, navigate to the directory where you saved the script, and run:
    ```bash
    python eCF.py
    ```
2.  **Enter Start URL:** In the "Start URL" field, enter the full URL of the website you want to start crawling from (e.g., `https://www.example.com`). Make sure it starts with `http` or `https`.
3.  **Select Save Folder (Optional but Recommended):** Click the "Select Save Folder" button to choose the directory where the downloaded files will be saved. By default, files will be saved in the same directory as the script.
4.  **Start Crawl:** Click the "Start Crawl" button to begin the process.
5.  **Monitor Progress:** The progress bar will appear, and the log area will show the URLs being visited and files being downloaded or failed downloads.
6.  **Pause/Resume:** Use the "Pause" button to temporarily halt the crawl. Click it again (which will now say "Resume") to continue.
7.  **Stop Crawl:** Click the "Stop Crawl" button to terminate the crawling process.
8.  **View Results:** The log area will show the activity. Downloaded files will be saved in the selected folder.

## How it Works

The script uses the `requests` library to fetch the HTML content of web pages. It then uses `beautifulsoup4` to parse the HTML and extract all anchor (`<a>`) tags with `href` attributes.

For each extracted link, it checks:

1.  If the crawl has been stopped.
2.  If the crawl is paused (and waits if it is).
3.  If the link is a downloadable file based on its extension. If so, it attempts to download the file.
4.  If the link is within the same domain as the starting URL. If so, it recursively calls the `_crawl` function on that link.

The `visited` set keeps track of visited URLs to avoid infinite loops and redundant requests.

## Customization

You can easily customize the list of downloadable file extensions by modifying the `DOWNLOADABLE_EXTENSIONS` set at the beginning of the script.

```python
DOWNLOADABLE_EXTENSIONS = {'.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
                           '.jpg', '.jpeg', '.png', '.gif', '.mp3', '.mp4', '.zip', '.rar', '.exe', '.apk'}
```

Add or remove extensions as needed.

## Important Notes

*   **Respect Websites:** Use this script responsibly and ethically. Avoid crawling websites without permission, especially those with strict terms of service or robots.txt files. Excessive crawling can put a burden on website servers.
*   **Rate Limiting:** This script does not implement any rate limiting. For large-scale crawling, consider adding delays between requests to avoid overwhelming the target website.
*   **Error Handling:** Basic error handling is included, but for production use, more robust error handling and logging would be beneficial.
*   **Deep Crawls:** Be aware that crawling very large websites can take a significant amount of time and consume considerable resources.
*   **Timeout:** A basic timeout is set for requests (`timeout=5` for page fetches, `timeout=10` for file downloads). You might need to adjust this depending on the website's responsiveness.
