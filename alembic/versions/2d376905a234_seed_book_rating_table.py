"""seed_book_rating_table

Revision ID: 2d376905a234
Revises: 2b510bc4e1aa
Create Date: 2024-11-09 12:51:39.722658

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import utils
from scipy.sparse import load_npz
import numpy as np
import pandas as pd


# revision identifiers, used by Alembic.
revision: str = '2d376905a234'
down_revision: Union[str, None] = '2b510bc4e1aa'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    y = load_npz(utils.BOOKS_DATA_Y)
    r, c = y.nonzero()
    data = np.full_like(r, 'Like', dtype='<U4')
    df = pd.DataFrame({'book_id' : c, 'rating' : data})

    connection = op.get_bind()
    df.to_sql('book_rating', connection, if_exists='append', index=False)


def downgrade() -> None:
    pass
