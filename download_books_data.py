import kagglehub
from pathlib import Path
import os
import shutil
import utils

def download_books_data():
    path = Path(kagglehub.model_download("mrtinicandreimarian/goodreads-with-features/other/default"))
    os.makedirs(utils.BOOKS_DATA, exist_ok=True)
    for file in os.listdir(path):
        shutil.move(path / file, utils.BOOKS_DATA)

    path = Path(kagglehub.dataset_download("mrtinicandreimarian/book-categories"))

    for file in os.listdir(path):
        shutil.move(path / file, utils.BOOKS_DATA)