"""seed_books

Revision ID: 882e2b40fcbc
Revises: afa90328bf9b
Create Date: 2024-10-26 15:06:29.580364

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '882e2b40fcbc'
down_revision: Union[str, None] = 'afa90328bf9b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
