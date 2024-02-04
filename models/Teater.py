from typing import Union
import mysql.connector

from controllers.exceptions import *
from models.database import DatabaseConnection
from models.base_models import Column, BaseModel


class Teater(BaseModel):
    name = "teater"
    id = Column("id", "INT UNSIGNED", primary_key=True, auto_increment=True)
    tname = Column("name", "VARCHAR(255)")
    Capacity = Column("Capacity", "INT UNSIGNED")
    age_rating = Column("age_rating", "SMALLINT UNSIGNED")
    screening_number = Column("screening_number", "SMALLINT UNSIGNED")

    def __init__(
        self,
        name: str,
        Capacity: int,
        screening_number: int,
        age_rating: int,
        id: Union[int, None] = None,
    ) -> None:
        self.id = id
        self.name = name
        self.Capacity = Capacity
        self.age_rating= age_rating
        self.screening_number = screening_number

    def add_Teater(self):
        TeaterRepo.insert_teater(self)

    def edit_Teater(self):
        TeaterRepo.update_teater(self)

    def delete_Teater(self):
        TeaterRepo.delete_teater(self)


class TeaterRepo:
    @staticmethod
    def insert_teater(teater: Teater):
        try:
            teater.insert(Teater)
        except mysql.connector.Error as err:
            raise InsertFailed("Some problem occurred while register new movie. Try again!")

    @staticmethod
    def update_teater(teater: Teater):
        try:
            conn = DatabaseConnection().get_connection()
            cursor = conn.cursor()
            query = f'UPDATE {teater.name} SET {teater.tname.name} = %s, {teater.Capacity.name} = %s, \
                     {teater.age_rating.name} = %s,{teater.screening_number.name} = %s WHERE {teater.id.name} = %s'
            cursor.execute(query, (teater.name, teater.Capacity,teater.age_rating, teater.screening_number, teater.id,))
            conn.commit()
        except mysql.connector.Error as err:
            raise UpdateFailed("Some problem occurred while updating subscription. Try again!")
        finally:
            cursor.close()
    
    @staticmethod
    def delete_teater(teater: Teater):
        try:
            conn = DatabaseConnection().get_connection()
            cursor = conn.cursor()
            cursor.execute(f'DELETE FROM {teater.name} WHERE {teater.id.name} = {teater.id}')
            conn.commit()
        except mysql.connector.Error as err:
            raise DeleteFailed("Some problem occurred while removing subscription. Try again!")
        finally:
            cursor.close()
