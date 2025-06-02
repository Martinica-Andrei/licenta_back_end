from dtos.users.get_rating_dto import GetRatingDto


class GetUserWithBookRatingDto:
    def __init__(self, username: str, rating_dtos : list[GetRatingDto]):
        self.username = username
        self.rating_dtos = rating_dtos

    def to_json(self):
        return {
            "name" : self.username,
            "ratings" : [dto.to_json() for dto in self.rating_dtos]
        }