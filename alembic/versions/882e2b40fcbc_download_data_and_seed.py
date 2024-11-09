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


# revision identifiers, used by Alembic.
revision: str = '882e2b40fcbc'
down_revision: Union[str, None] = 'afa90328bf9b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    path = Path(kagglehub.model_download("mrtinicandreimarian/goodreads_no_features/other/default"))

    os.makedirs(utils.BOOKS_DATA, exist_ok=True)
    for file in os.listdir(path):
        shutil.move(path / file, utils.BOOKS_DATA)

    book_df = pd.read_csv(utils.BOOKS_DATA_BOOKS_PROCESSED)
    book_df = book_df[['title', 'description', 'url', 'image_url']].copy()
    book_df['description'] = book_df['description'].fillna('')

    no_photo_link = 'https://s.gr-assets.com/assets/nophoto/book/111x148-bcc042a9c91a29c1d680899eff700a03.png'
    book_df['image_url'] = book_df['image_url'].replace({no_photo_link: np.nan})

    base_url = 'https://images.gr-assets.com/books/'
    book_df['image_url'] = book_df['image_url'].str.replace(base_url, '').str.replace('/', '-')

    book_df.rename(columns={"url" : "link", "image_url" : "image_link"}, inplace=True)
    book_df.index.name = 'id'

    connection = op.get_bind()
    book_df.to_sql('book', connection, if_exists='append')


def downgrade() -> None:
    pass
