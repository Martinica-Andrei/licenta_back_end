class GetBookDto:
    def __init__(self,
                 id: int,
                 title: str,
                 description: str,
                 link: str,
                 image: str,
                 nr_likes: int,
                 nr_dislikes: int,
                 categories: list[str],
                 authors: dict[str, str],
                 rating: None | str):
        self.id = id
        self.title = title
        self.description = description
        self.link = link
        self.image = image
        self.nr_likes = nr_likes
        self.nr_dislikes = nr_dislikes
        self.categories = categories
        self.authors = authors
        self.rating = rating

    def to_json(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "link": self.link,
            "image": self.image,
            "nr_likes": self.nr_likes,
            "nr_dislikes": self.nr_dislikes,
            "categories": self.categories,
            "authors": self.authors,
            "rating": self.rating
        }
