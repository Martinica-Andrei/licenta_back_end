class GetBookIdTitleDto:
    def __init__(self, id: int, title :str):
        self.id = id
        self.title = title

    def to_json(self):
        return {
            'id': self.id,
            'title': self.title
        }