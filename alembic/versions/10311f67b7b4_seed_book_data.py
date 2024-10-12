"""seed_book_data

Revision ID: 10311f67b7b4
Revises: 6bf2e9b15bde
Create Date: 2024-10-12 20:42:03.166850

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

import pandas as pd
from pathlib import Path


# revision identifiers, used by Alembic.
revision: str = '10311f67b7b4'
down_revision: Union[str, None] = '6bf2e9b15bde'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    df = pd.read_csv(Path('datasets/amazon/books_data_reordered.csv'))
    print(df)


def downgrade() -> None:
    pass