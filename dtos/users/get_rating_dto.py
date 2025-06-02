class GetRatingDto:
    def __init__(self,
                 book_id: str,
                 title: str,
                 rating: str,
                 image: str,
                 link: str,
                 nr_likes: int,
                 nr_dislikes: int):
        self.book_id = book_id
        self.title = title
        self.rating = rating
        self.image = image
        self.link = link
        self.nr_likes = nr_likes
        self.nr_dislikes = nr_dislikes

    def to_json(self):
        return {
            "id": self.book_id,
            "title": self.title,
            "rating": self.rating,
            "image": self.image,
            "link": self.link,
            "nr_likes": self.nr_likes,
            "nr_dislikes": self.nr_dislikes
        }
