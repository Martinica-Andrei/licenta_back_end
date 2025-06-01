from sqlalchemy.orm.scoping import scoped_session


class BookRepository:
    def __init__(self, scoped_session: scoped_session):
        self.scoped_session = scoped_session
