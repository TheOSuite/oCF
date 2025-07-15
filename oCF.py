import os
import threading
import requests
import time
import concurrent.futures
import traceback
from urllib.parse import urljoin, urlparse
from tkinter import Tk, Label, Entry, Button, Text, Scrollbar, END, filedialog, ttk

from bs4 import BeautifulSoup

DOWNLOADABLE_EXTENSIONS = {'.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
                           '.jpg', '.jpeg', '.png', '.gif', '.mp3', '.mp4', '.zip', '.rar', '.exe', '.apk'}

class FileCrawlerGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("File Crawler Bot")
        self.master.geometry("700x500")

        Label(master, text="Start URL:").pack()
        self.url_entry = Entry(master, width=80)
        self.url_entry.pack()

        Label(master, text="Max Depth (0 for unlimited):").pack()
        self.max_depth_entry = Entry(master, width=10)
        self.max_depth_entry.pack()

        Label(master, text="Max Pages (0 for unlimited):").pack()
        self.max_pages_entry = Entry(master, width=10)
        self.max_pages_entry.pack()

        self.start_button = Button(master, text="Start Crawl", command=self.start_scan)
        self.start_button.pack(pady=5)

        self.pause_button = Button(master, text="Pause", command=self.toggle_pause, state="disabled")
        self.pause_button.pack(pady=5)

        self.stop_button = Button(master, text="Stop Crawl", command=self.stop_scan, state="disabled")
        self.stop_button.pack(pady=5)

        self.save_button = Button(master, text="Select Save Folder", command=self.choose_save_folder)
        self.save_button.pack(pady=5)

        self.export_button = Button(master, text="Export Logs", command=self.export_logs)
        self.export_button.pack(pady=5)

        self.progress = ttk.Progressbar(master, mode='indeterminate')

        self.result_text = Text(master, height=20, wrap="word")
        self.result_text.pack(padx=10, pady=10, fill="both", expand=True)

        self.scrollbar = Scrollbar(master, command=self.result_text.yview)
        self.result_text.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y")

        self.visited = set()
        self.downloaded_files = []
        self.save_folder = os.getcwd()

        self.stop_flag = threading.Event()
        self.pause_flag = threading.Event()
        self.pause_flag.set()  # allow running initially

    def choose_save_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.save_folder = folder
            self.log(f"Save folder set to: {folder}")

    def export_logs(self):
        filename = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if filename:
            with open(filename, 'w') as f:
                f.write(self.result_text.get(1.0, END))
            self.log(f"Logs exported to {filename}")

    def start_scan(self):
        url = self.url_entry.get().strip()
        if not url.startswith("http"):
            self.log("Please enter a valid URL starting with http or https.")
            return

        try:
            max_depth = int(self.max_depth_entry.get()) if self.max_depth_entry.get() else 0
            max_pages = int(self.max_pages_entry.get()) if self.max_pages_entry.get() else 0
        except ValueError:
            self.log("Invalid input for max depth or max pages. Must be integers.")
            return

        self.result_text.delete(1.0, END)
        self.progress.pack(pady=5)
        self.progress.start()

        self.start_button.config(state="disabled")
        self.pause_button.config(state="normal")
        self.stop_button.config(state="normal")

        self.stop_flag.clear()
        self.pause_flag.set()

        thread = threading.Thread(target=self.crawl_site, args=(url, max_depth, max_pages))
        thread.start()

    def toggle_pause(self):
        if self.pause_flag.is_set():
            self.pause_flag.clear()
            self.pause_button.config(text="Resume")
            self.log("Crawl paused.")
        else:
            self.pause_flag.set()
            self.pause_button.config(text="Pause")
            self.log("Crawl resumed.")

    def stop_scan(self):
        self.log("Stopping crawl...")
        self.stop_flag.set()
        self.pause_flag.set()  # ensure resume doesn't hang
        self.stop_button.config(state="disabled")
        self.pause_button.config(state="disabled")

    def crawl_site(self, start_url, max_depth, max_pages):
        try:
            self.visited.clear()
            self.downloaded_files.clear()
            from collections import deque
            queue = deque([(start_url, 0)])
            headers = {'User-Agent': 'TheoSuiteCrawler/1.0'}

            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                while queue and not self.stop_flag.is_set():
                    self.pause_flag.wait()
                    if max_pages > 0 and len(self.visited) >= max_pages:
                        break
                    url, current_depth = queue.popleft()
                    url = self.normalize_url(url)
                    if url in self.visited:
                        continue
                    self.visited.add(url)
                    try:
                        response = requests.get(url, timeout=5, headers=headers)
                        time.sleep(0.5)  # Rate limit for crawl requests
                        if response.status_code != 200:
                            continue

                        content_type = response.headers.get('Content-Type', '')
                        if 'text/html' not in content_type:
                            if self.is_downloadable(url, response.headers):
                                executor.submit(self.download_file, url)
                            continue  # Skip link extraction for non-HTML

                        for link in self.extract_links(response.text, url):
                            link = self.normalize_url(link)
                            if self.stop_flag.is_set():
                                return
                            if any(link.lower().endswith(ext) for ext in DOWNLOADABLE_EXTENSIONS):
                                executor.submit(self.download_file, link)
                            elif self.is_same_domain(start_url, link) and link not in self.visited:
                                if max_depth == 0 or current_depth + 1 <= max_depth:
                                    queue.append((link, current_depth + 1))
                    except requests.RequestException:
                        pass

        finally:
            self.progress.stop()
            self.progress.pack_forget()
            self.start_button.config(state="normal")
            self.pause_button.config(state="disabled")
            self.stop_button.config(state="disabled")
            self.pause_button.config(text="Pause")
            self.log("\nCrawling completed or stopped.")
            self.log(f"Total files downloaded: {len(self.downloaded_files)}")

    def normalize_url(self, url):
        parsed = urlparse(url)
        return parsed._replace(fragment='').geturl()

    def is_downloadable(self, url, headers):
        ext = os.path.splitext(urlparse(url).path)[1].lower()
        if ext in DOWNLOADABLE_EXTENSIONS:
            return True
        content_type = headers.get('Content-Type', '').lower()
        # Map common MIME types to extensions
        mime_to_ext = {
            'application/pdf': '.pdf',
            'application/msword': '.doc',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
            'application/vnd.ms-excel': '.xls',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': '.xlsx',
            'application/vnd.ms-powerpoint': '.ppt',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation': '.pptx',
            'image/jpeg': '.jpg',
            'image/png': '.png',
            'image/gif': '.gif',
            'audio/mpeg': '.mp3',
            'video/mp4': '.mp4',
            'application/zip': '.zip',
            'application/x-rar-compressed': '.rar',
            'application/octet-stream': '.exe',
            'application/vnd.android.package-archive': '.apk',
            # Add more as needed
        }
        return any(content_type.startswith(mime) for mime in mime_to_ext)

    def extract_links(self, html, base_url):
        try:
            soup = BeautifulSoup(html, "lxml")
        except:
            soup = BeautifulSoup(html, "html.parser")
        links = set()
        for tag in soup.find_all(['a', 'img', 'script', 'link'], href=True):
            links.add(urljoin(base_url, tag['href']))
        for tag in soup.find_all(['img', 'source', 'video', 'audio'], src=True):
            links.add(urljoin(base_url, tag['src']))
        return links

    def is_same_domain(self, base, link):
        return urlparse(base).netloc == urlparse(link).netloc

    def download_file(self, url):
        if self.stop_flag.is_set():
            return
        self.pause_flag.wait()
        headers = {'User-Agent': 'TheoSuiteCrawler/1.0'}
        try:
            local_filename = os.path.join(self.save_folder, os.path.basename(urlparse(url).path))
            if not os.path.exists(local_filename):
                r = requests.get(url, stream=True, timeout=10, headers=headers)
                with open(local_filename, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if self.stop_flag.is_set():
                            return
                        self.pause_flag.wait()
                        f.write(chunk)
                self.downloaded_files.append(url)
                self.log(f"Downloaded: {url}")
        except Exception as e:
            self.log(f"Failed to download {url}: {str(e)}\n{traceback.format_exc()}")

    def log(self, message):
        self.result_text.insert(END, message + "\n")
        self.result_text.see(END)

if __name__ == "__main__":
    root = Tk()
    app = FileCrawlerGUI(root)
    root.mainloop()
