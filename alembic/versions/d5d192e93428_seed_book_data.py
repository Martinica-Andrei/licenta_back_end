"""seed_book_data

Revision ID: d5d192e93428
Revises: 203f86093b3b
Create Date: 2024-10-13 11:34:59.140791

"""
from typing import Sequence, Union

from alembic import context

from alembic import op
import sqlalchemy as sa

import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine


# revision identifiers, used by Alembic.
revision: str = 'd5d192e93428'
down_revision: Union[str, None] = '203f86093b3b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    df = pd.read_csv(Path('datasets/amazon/books_data_reordered.csv'))
    df.columns = df.columns.str.lower()
    df.index.name = 'id'
    columns = ['title','description','authors','previewlink','infolink','categories']

    config = context.config
    database_url = config.get_main_option("sqlalchemy.url")
    
    engine = create_engine(database_url)
    with engine.connect() as connection:
        df[columns].to_sql('book_data', connection, if_exists='append')


def downgrade() -> None:
    pass
