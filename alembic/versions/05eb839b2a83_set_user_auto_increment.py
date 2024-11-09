"""set_user_auto_increment

Revision ID: 05eb839b2a83
Revises: 2d376905a234
Create Date: 2024-11-09 14:55:57.320036

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from scipy.sparse import load_npz
import utils


# revision identifiers, used by Alembic.
revision: str = '05eb839b2a83'
down_revision: Union[str, None] = '2d376905a234'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    y_ratings = load_npz(utils.BOOKS_DATA_Y)
    op.execute(f'ALTER TABLE user AUTO_INCREMENT = {y_ratings.shape[0]}')


def downgrade() -> None:
    pass
