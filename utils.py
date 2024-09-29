import re
from hashlib import sha256
from pathlib import Path


def escape_fts(str):
    return re.sub(r'[\'\"]', '', str)

DATASETS_AMAZON_IMAGES_PATH = Path('datasets/amazon/images')

def convert_str_to_datasets_amazon_images_path(x):
    x = sha256(x.encode()).hexdigest()
    x = x + '.jpg'
    x = DATASETS_AMAZON_IMAGES_PATH / x
    return x