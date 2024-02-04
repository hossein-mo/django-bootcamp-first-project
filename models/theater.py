from typing import Union
from controllers.exceptions import *
from models.database import DatabaseConnection
from models.base_models import Column, BaseModel


class Theater(BaseModel):
    name = "theater"
    id = Column("id", "INT UNSIGNED", primary_key=True, auto_increment=True)
    tname = Column("name", "VARCHAR(255)")
    Capacity = Column("Capacity", "INT UNSIGNED")


    def __init__(
        self,
        name: str,
        Capacity: int,
        id: Union[int, None] = None,
    ) -> None:
        self.id = id
        self.name = name
        self.Capacity = Capacity

    def add_Theater(self):
        Theater.insert(self)

    def edit_Theater(self):
        Theater.update(self)

    def delete_Theater(self):
        Theater.delet(self)
