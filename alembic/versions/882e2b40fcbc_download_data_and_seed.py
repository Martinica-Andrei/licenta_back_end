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
import numpy as np
import ast
from sklearn.preprocessing import LabelEncoder
from download_books_data import download_books_data


# revision identifiers, used by Alembic.
revision: str = '882e2b40fcbc'
down_revision: Union[str, None] = 'afa90328bf9b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    connection = op.get_bind()

    download_books_data()
    authors_to_sql(connection)

    categories_encoder = LabelEncoder()  # also maps categories from book_data
    categories_to_sql(connection, categories_encoder)

    book_df = pd.read_csv(utils.BOOKS_DATA_BOOKS_PROCESSED)
    book_authors_to_sql(connection, book_df)
    book_categories_to_sql(connection, book_df, categories_encoder)
    book_to_sql(connection, book_df)


def downgrade() -> None:
    pass


def authors_to_sql(connection) -> None:
    """
    Converts authors to sql.

    Args:
        connection (Connection) : Sql connection.

    Returns:
        None.
    """
    authors = pd.read_csv(utils.BOOKS_AUTHORS).rename(
        columns={'author_id': 'id'})
    authors = authors.loc[:, ["id", "name"]]
    authors.to_sql('author', connection, if_exists='append', index=False)


def categories_to_sql(connection, categories_enc: LabelEncoder) -> None:
    """
    Converts categories to sql.

    Args:
        connection (Connection): Sql connection.
        categories_enc (LabelEncoder): Label encoder encodes categories names.

    Returns:
        None.
    """
    categories = pd.read_csv(utils.BOOKS_CATEGORIES).rename(
        columns={'0': 'name'})
    categories_enc.fit(categories['name'])
    categories['id'] = categories_enc.transform(categories['name'])
    categories.to_sql('category', connection, if_exists='append', index=False)


def book_authors_to_sql(connection, book_df: pd.DataFrame) -> None:
    """
    Converts book authors to sql.

    Args:
        connection (Connection): Sql connection.
        book_df (pd.DataFrame): Dataframe containing 'authors' column.

    Returns:
        None.
    """
    # ast.literal_eval converts to dict from str
    # reset_index to obtain a new column called index containing each row number
    book_authors = book_df['authors'].apply(ast.literal_eval).reset_index()
    # for each row, create a new dataframe mapping each author with each book index
    # and concatenate all dataframes vertically
    book_authors = pd.concat(book_authors.apply(
        convert_book_authors, axis=1).values, axis=0, ignore_index=True)
    print(book_authors)
    book_authors.to_sql('book_authors', connection,
                        if_exists='append', index=False)


def book_categories_to_sql(connection, book_df: pd.DataFrame, categories_enc: LabelEncoder):
    """
    Converts book categories to sql.

    Args:
        connection (Connection): Sql connection.
        book_df (pd.DataFrame): Dataframe containing 'categories' column.

    Returns:
        None.
    """
    # ast.literal_eval converts to array from str
    # reset_index to obtain a new column called index containing each row number
    book_categories = book_df['categories'].apply(
        ast.literal_eval).reset_index()
    # for each row, create a new dataframe mapping each category with each book index
    # and concatenate all dataframes vertically
    book_categories = pd.concat(book_categories.apply(
        convert_book_categories, axis=1).values, axis=0, ignore_index=True)
    # map category names to ids using categories_enc
    book_categories['category_id'] = categories_enc.transform(
        book_categories['category_id'])
    book_categories.to_sql('book_categories', connection,
                           if_exists='append', index=False)


def book_to_sql(connection, book_df: pd.DataFrame):
    """
    Converts book to sql.

    Args:
        connection (Connection): Sql connection.
        book_df (pd.DataFrame): Dataframe to be converted to sql.s

    Returns:
        None.
    """
    book_df = book_df[['title', 'description', 'url', 'image_url']].copy()
    book_df['description'] = book_df['description'].fillna('')

    book_df['image_url'] = utils.replace_no_photo_link(book_df['image_url'])
    book_df['image_url'] = book_df['image_url'].apply(
        utils.process_book_scraped_url)

    book_df.rename(
        columns={"url": "link", "image_url": "image_link"}, inplace=True)
    book_df.index.name = 'id'

    book_df.to_sql('book', connection, if_exists='append')


def convert_book_categories(x):
    # index contains row numbers
    index, categories = x['index'], x['categories']
    # for each category, create a list containing same row number and category
    categories = [[index] + [v] for v in categories]
    df = pd.DataFrame(categories, columns=['book_id', 'category_id'])
    return df


def convert_book_authors(x) -> pd.DataFrame:
    """
    Converts book authors in a single row into a dataframe containing rows for each author and same book_id.
    """
    # index contains row number
    index, authors = x['index'], x['authors']
    # create a new dataframe repeating the same row index for each author
    authors = [[index] + [k, v] for k, v in authors.items()]
    df = pd.DataFrame(authors, columns=['book_id', 'author_id', 'role'])
    df['role'] = df['role'].replace({'': np.nan})
    return df
