import re

def escape_fts(str):
    return re.sub(r'[\'\"]', '', str)