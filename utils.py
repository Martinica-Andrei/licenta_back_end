import re
from hashlib import sha256
from pathlib import Path


def convert_for_word_search(x : str):
    x = re.sub(r'[^A-Za-z0-9_]', ' ', x)
    x = x.strip()
    x = re.split(r'\s+', x)
    x_str = [f'+{v}*' for v in x]
    x_str = ' '.join(x_str)
    return (x_str, x)

DATASETS_AMAZON_IMAGES_PATH = Path('datasets/amazon/images')
DATASETS_AMAZON_STATIC_IMAGES_PATH = Path('datasets/amazon/static_images')

def convert_str_to_datasets_amazon_images_path(x):
    x = sha256(x.encode()).hexdigest()
    x = x + '.jpg'
    x = DATASETS_AMAZON_IMAGES_PATH / x
    return x

def string_list_to_list(x): 
    return [item.strip(' \'"') for item in x.strip('[]').split(',')]
