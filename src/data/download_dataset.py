"""
Dataset Downloader for Online Retail II B2B E-Commerce Data.
Source: UCI Machine Learning Repository (Open Access)
"""

import os
import zipfile
import urllib.request
from pathlib import Path
from tqdm import tqdm

DATA_URL = "https://archive.ics.uci.edu/static/public/502/online+retail+ii.zip"
RAW_DIR = Path("data/raw")

class DownloadProgressBar(tqdm):
    def update_to(self, b=1, bsize=1, tsize=None):
        if tsize is not None:
            self.total = tsize
        self.update(b * bsize - self.n)

def download_and_extract():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    zip_path = RAW_DIR / "online_retail_ii.zip"

    # Check if raw excel or csv already exists
    xlsx_files = list(RAW_DIR.glob("*.xlsx"))
    csv_files = list(RAW_DIR.glob("*.csv"))
    if xlsx_files or csv_files:
        print(f"Dataset already found in {RAW_DIR}: {[f.name for f in xlsx_files + csv_files]}")
        return

    print(f"Downloading Online Retail II dataset from {DATA_URL}...")
    headers = {"User-Agent": "Mozilla/5.0"}
    req = urllib.request.Request(DATA_URL, headers=headers)
    with urllib.request.urlopen(req) as response:
        total_size = int(response.info().get('Content-Length', 0))
        with DownloadProgressBar(unit='B', unit_scale=True, miniters=1, desc="online_retail_ii.zip", total=total_size) as t:
            with open(zip_path, 'wb') as out_file:
                while True:
                    buffer = response.read(1024 * 64)
                    if not buffer:
                        break
                    out_file.write(buffer)
                    t.update(len(buffer))

    print(f"Extracting {zip_path}...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(RAW_DIR)
    
    print(f"Extraction complete. Files in {RAW_DIR}:")
    for f in RAW_DIR.iterdir():
        print(f" - {f.name} ({f.stat().st_size / (1024*1024):.2f} MB)")

if __name__ == "__main__":
    download_and_extract()
