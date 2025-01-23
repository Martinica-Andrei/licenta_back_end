"""seed_books

Revision ID: 882e2b40fcbc
Revises: afa90328bf9b
Create Date: 2024-10-26 15:06:29.580364

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

import pandas as pd
import utils
from pathlib import Path
import os
import kagglehub
import shutil
import numpy as np
import ast
from sklearn.preprocessing import LabelEncoder


# revision identifiers, used by Alembic.
revision: str = '882e2b40fcbc'
down_revision: Union[str, None] = 'afa90328bf9b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:

    path = Path(kagglehub.model_download("mrtinicandreimarian/goodreads-with-features/other/default")) / "training_data"

    os.makedirs(utils.BOOKS_DATA, exist_ok=True)
    for file in os.listdir(path):
        shutil.move(path / file, utils.BOOKS_DATA)

    path = Path(kagglehub.dataset_download("mrtinicandreimarian/book-categories"))

    for file in os.listdir(path):
        shutil.move(path / file, utils.BOOKS_DATA)

    authors = pd.read_csv(utils.BOOKS_AUTHORS).rename(columns={'author_id' : 'id'})
    categories = pd.read_csv(utils.BOOKS_CATEGORIES).rename(columns={'0':'name'})
    categories_encoder = LabelEncoder().fit(categories['name'])
    categories['id'] = categories_encoder.transform(categories['name'])

    connection = op.get_bind()

    authors.to_sql('author', connection, if_exists='append', index=False)
    categories.to_sql('category', connection, if_exists='append', index=False)

    book_df = pd.read_csv(utils.BOOKS_DATA_BOOKS_PROCESSED)
   
    book_authors = book_df['authors'].apply(ast.literal_eval).reset_index()
    book_authors = pd.concat(book_authors.apply(convert_book_authors, axis=1).values, axis=0, ignore_index=True)

    book_categories = book_df['categories'].apply(ast.literal_eval).reset_index()
    book_categories = pd.concat(book_categories.apply(convert_book_categories, axis=1).values, axis=0, ignore_index=True)
    book_categories['category_id'] = categories_encoder.transform(book_categories['category_id'])

    book_df = book_df[['title', 'description', 'url', 'image_url']].copy()
    book_df['description'] = book_df['description'].fillna('')

    no_photo_link = 'https://s.gr-assets.com/assets/nophoto/book/111x148-bcc042a9c91a29c1d680899eff700a03.png'
    book_df['image_url'] = book_df['image_url'].replace({no_photo_link: np.nan})

    base_url = 'https://images.gr-assets.com/books/'
    book_df['image_url'] = book_df['image_url'].str.replace(base_url, '').str.replace('/', '-')

    book_df.rename(columns={"url" : "link", "image_url" : "image_link"}, inplace=True)
    book_df.index.name = 'id'

    book_df.to_sql('book', connection, if_exists='append')
    book_categories.to_sql('book_categories', connection, if_exists='append', index=False)
    book_authors.to_sql('book_authors', connection, if_exists='append', index=False)


def downgrade() -> None:
    pass

def convert_book_categories(x):
    index, categories = x['index'], x['categories']
    categories = [[index] + [v] for v in categories]
    df = pd.DataFrame(categories, columns=['book_id', 'category_id'])
    return df

def convert_book_authors(x):
    index, authors = x['index'], x['authors']
    authors = [[index] + [k, v] for k, v in authors.items()]
    df = pd.DataFrame(authors, columns=['book_id', 'author_id', 'role'])
    df['role'] = df['role'].replace({'': np.nan})
    return df