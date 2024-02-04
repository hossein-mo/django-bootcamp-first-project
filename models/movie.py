from typing import Union

from controllers.exceptions import *
from base_models import Column, BaseModel

class Movie(BaseModel):
    name = "movie"
    id = Column("id", "INT UNSIGNED", primary_key=True, auto_increment=True)
    m_name = Column("name", "VARCHAR(255)")
    duration = Column("duration", "TIME")
    age_rating = Column("age_rating", "SMALLINT UNSIGNED")
    screening_number = Column("screening_number", "SMALLINT UNSIGNED")

    def __init__(
        self,
        name: str,
        duration: int,
        age_rating: int,
        screening_number: int,
        id: Union[int, None] = None,
    ) -> None:
        self.id = id
        self.name = name
        self.duration = duration
        self.age_rating = age_rating
        self.screening_number = screening_number

    def add_movie(self):
        self.insert()

    def edit_movie(self):
        self.update({Movie.m_name : self.name, Movie.duration : self.duration, \
                     Movie.age_rating : self.age_rating, Movie.screening_number : self.screening_number})

    def delete_movie(self):
        self.delete()