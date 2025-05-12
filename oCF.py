import os
import threading
import requests
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

        self.start_button = Button(master, text="Start Crawl", command=self.start_scan)
        self.start_button.pack(pady=5)

        self.pause_button = Button(master, text="Pause", command=self.toggle_pause, state="disabled")
        self.pause_button.pack(pady=5)

        self.stop_button = Button(master, text="Stop Crawl", command=self.stop_scan, state="disabled")
        self.stop_button.pack(pady=5)

        self.save_button = Button(master, text="Select Save Folder", command=self.choose_save_folder)
        self.save_button.pack(pady=5)

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

    def start_scan(self):
        url = self.url_entry.get().strip()
        if not url.startswith("http"):
            self.log("Please enter a valid URL starting with http or https.")
            return

        self.result_text.delete(1.0, END)
        self.progress.pack(pady=5)
        self.progress.start()

        self.start_button.config(state="disabled")
        self.pause_button.config(state="normal")
        self.stop_button.config(state="normal")

        self.stop_flag.clear()
        self.pause_flag.set()

        thread = threading.Thread(target=self.crawl_site, args=(url,))
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

    def crawl_site(self, start_url):
        try:
            self.visited.clear()
            self.downloaded_files.clear()
            self._crawl(start_url)
        finally:
            self.progress.stop()
            self.progress.pack_forget()
            self.start_button.config(state="normal")
            self.pause_button.config(state="disabled")
            self.stop_button.config(state="disabled")
            self.pause_button.config(text="Pause")
            self.log("\nCrawling completed or stopped.")
            self.log(f"Total files downloaded: {len(self.downloaded_files)}")

    def _crawl(self, url):
        if self.stop_flag.is_set() or url in self.visited or not url.startswith("http"):
            return

        self.pause_flag.wait()

        self.visited.add(url)
        try:
            response = requests.get(url, timeout=5)
        except requests.RequestException:
            return

        if response.status_code != 200:
            return

        for link in self.extract_links(response.text, url):
            if self.stop_flag.is_set():
                return
            self.pause_flag.wait()
            if any(link.lower().endswith(ext) for ext in DOWNLOADABLE_EXTENSIONS):
                self.download_file(link)
            elif self.is_same_domain(url, link):
                self._crawl(link)

    def extract_links(self, html, base_url):
        soup = BeautifulSoup(html, "html.parser")
        return {urljoin(base_url, tag.get("href")) for tag in soup.find_all("a", href=True)}

    def is_same_domain(self, base, link):
        return urlparse(base).netloc == urlparse(link).netloc

    def download_file(self, url):
        if self.stop_flag.is_set():
            return
        self.pause_flag.wait()
        try:
            local_filename = os.path.join(self.save_folder, os.path.basename(urlparse(url).path))
            if not os.path.exists(local_filename):
                r = requests.get(url, stream=True, timeout=10)
                with open(local_filename, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if self.stop_flag.is_set():
                            return
                        self.pause_flag.wait()
                        f.write(chunk)
                self.downloaded_files.append(url)
                self.log(f"Downloaded: {url}")
        except Exception as e:
            self.log(f"Failed to download {url}: {str(e)}")

    def log(self, message):
        self.result_text.insert(END, message + "\n")
        self.result_text.see(END)

if __name__ == "__main__":
    root = Tk()
    app = FileCrawlerGUI(root)
    root.mainloop()
