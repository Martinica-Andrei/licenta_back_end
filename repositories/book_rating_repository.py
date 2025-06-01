from sqlalchemy.orm.scoping import scoped_session


class BookRatingRepository:
    def __init__(self, scoped_session: scoped_session):
        self.scoped_session = scoped_session

