from typing import Union
import mysql.connector

from controllers.exceptions import *
from models.database import DatabaseConnection
from models.base_models import Column, BaseModel

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
        MovieRepo.insert_movie(self)

    def edit_movie(self):
        MovieRepo.update_movie(self)

    def delete_movie(self):
        MovieRepo.delete_movie(self)


class MovieRepo:
    @staticmethod
    def insert_movie(movie: Movie):
        try:
            Movie.insert(movie)
        except mysql.connector.Error as err:
            raise InsertFailed("Some problem occurred while register new movie. Try again!")

    @staticmethod
    def update_movie(movie: Movie):
        try:
            conn = DatabaseConnection().get_connection()
            cursor = conn.cursor()
            query = f'UPDATE {Movie.name} SET {Movie.m_name.name} = %s, {Movie.duration.name} = %s, \
                    {Movie.age_rating.name} = %s, {Movie.screening_number.name} = %s WHERE {Movie.id.name} = %s'
            cursor.execute(query, (movie.name, movie.duration, movie.age_rating, movie.screening_number, movie.id,))
            conn.commit()
        except mysql.connector.Error as err:
            raise UpdateFailed("Some problem occurred while updating subscription. Try again!")
        finally:
            cursor.close()
    
    @staticmethod
    def delete_movie(movie: Movie):
        try:
            conn = DatabaseConnection().get_connection()
            cursor = conn.cursor()
            cursor.execute(f'DELETE FROM {Movie.name} WHERE {Movie.id.name} = {movie.id}')
            conn.commit()
        except mysql.connector.Error as err:
            raise DeleteFailed("Some problem occurred while removing subscription. Try again!")
        finally:
            cursor.close()
