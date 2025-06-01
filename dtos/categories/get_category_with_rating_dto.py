class GetCategoryWithRatingDto:
    def __init__(self, id: int, name: str, liked: str):
        self.id = id
        self.name = name
        self.liked = liked

    def to_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'liked': self.liked
        }
