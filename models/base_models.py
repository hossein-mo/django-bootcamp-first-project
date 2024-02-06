import os
import sys
from enum import Enum
from typing import Union, Any, List, Dict
from mysql.connector import Error as dbError
from mysql.connector import IntegrityError

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from models.database import DatabaseConnection
from models.model_exceptions import DuplicatedEntry


class Column:
    def __init__(
        self,
        name: str,
        type: str,
        primary_key: bool = False,
        unique: bool = False,
        null: bool = False,
        auto_increment: bool = False,
        foreign_key: Union[None, str] = None,
        reference: Union[None, str] = None,
        default: Any = None,
        as_string: bool = True,
    ) -> None:
        """Instances of Column class can be mapped to SQL table columns.

        Args:
            name (str): Name of the column
            type (str): Data type of the column in database.
            primary_key (bool, optional): Whether this column is primary key or not. Defaults to False.
            unique (bool, optional): Whether values in this column should be unique or not. \
                This will create a unique key constraint in table. It has to be False for primary keys. \
                    Defaults to False.
            null (bool, optional): Whether the column is nullable or not. Defaults to False.
            auto_increment (bool, optional): Sets the auto increment feature for column. Mainly used for id columns.\
                 When set to True the equivalent attribute to this column will not be inserted into database.  \
                    Defaults to False.
            foreign_key (Union[None, str], optional): None for no foreign key \
                or the name of the referenced column. Defaults to False.
            reference (Union[None, str], optional): None for no foreign key \
                or the name of the referenced table. Defaults to False.
            default (Any, optional): Default value of the column or None for no default value. Defaults to None.
            as_string (bool, optional): If set to True values of this column will be passed to \
                database without double quotations. This is use full when we want to use MySQL functions \
                    like UUID(). Defaults to True.
        """
        self.name = name
        self.type = type
        self.primary_key = primary_key
        self.unique = unique
        self.null = null
        self.auto_increment = auto_increment
        self.foreign_key = foreign_key
        self.reference = reference
        self.default = default
        self.as_string = as_string

    def __call__(self) -> str:
        """Creates the column definition in SQL syntax.

        Returns:
            str: Column definition in SQL syntax.
        """
        column_str = f"{self.name} {self.type}"
        if self.null:
            column_str = f"{column_str} DEFAULT NULL"
        else:
            column_str = f"{column_str} NOT NULL"
            if self.default:
                column_str = f"{column_str} DEFAULT '{self.default}'"
        if self.auto_increment:
            column_str = f"{column_str} AUTO_INCREMENT"
        return f"{column_str},"

    def __str__(self) -> str:
        """String value of the column

        Returns:
            str: Name of the column
        """
        return self.name

    def __hash__(self) -> hash:
        return hash(self.name)


class BaseModel:
    name: str
    db_obj = DatabaseConnection()

    @classmethod
    def create_new(cls, **kwargs):
        return cls(**kwargs)

    @classmethod
    def get_columns(cls) -> List[Column]:
        """Create a list of class attributes that are instances of Column class.

        Returns:
            List[Column]: List of column instances.
        """
        columns = []
        for _, column in vars(cls).items():
            if isinstance(column, Column):
                columns.append(column)
        return columns

    @classmethod
    def get_primary_keys(cls) -> List[Column]:
        """Return list of primary key columns

        Returns:
            List[Column]: list of primary keys
        """
        columns = cls.get_columns()
        pk = []
        for column in columns:
            if column.primary_key:
                pk.append(column)
        return pk

    @classmethod
    def create_table_query(cls) -> str:
        """Creates the SQL query to create the database table of the model.

        Returns:
            str: Create table query.
        """
        query = f"CREATE TABLE {cls.name} (\n"
        primary_keys = []
        unique_keys = []
        foreign_keys = {}
        columns = cls.get_columns()
        for column in columns:
            query = f"{query}{column()}\n"
            if column.primary_key:
                primary_keys.append(column.name)
            elif column.foreign_key:
                foreign_keys[column.name] = [
                    column.reference,
                    column.foreign_key,
                ]
            if column.unique:
                unique_keys.append(column.name)

        keys = ", ".join(tuple(primary_keys))
        keys = f"PRIMARY KEY ({keys})"
        if unique_keys:
            for key in unique_keys:
                keys = f"{keys},\nUNIQUE KEY {cls.name}_unique_{key} ({key})"
        if foreign_keys:
            for key in foreign_keys:
                keys = (
                    f"{keys},\nCONSTRAINT {cls.name}_{foreign_keys[key][0]}_{foreign_keys[key][1]}_FK "
                    f"FOREIGN KEY ({key}) REFERENCES {foreign_keys[key][0]} ({foreign_keys[key][1]})"
                )

        query = f"{query}{keys}\n);"
        return query

    @classmethod
    def create_table(cls) -> None:
        """Creates the model table in database"""
        query = cls.create_table_query()
        try:
            cls.db_obj.execute(query)
        except dbError as err:
            print(f'Error while creating "{cls.name}" table.')
            print(f"Error description: {err}")

    @classmethod
    def fetch(
        cls,
        select: str = "*",
        where: str = None,
        order_by: str = None,
        descending: bool = False,
        limit: int = None,
        offset: int = None,
    ) -> List[dict]:
        """Executes select query in the table of model instance.

        Returns:
            dict: List of fetched rows as dictionary of selected columns
        """
        query = f'SELECT {",".join(select)} FROM {cls.name}'
        if where:
            query = f"{query} WHERE {where}"
        if order_by:
            query = f"{query} ORDER BY {order_by}"
            if descending:
                query = f"{query} DESC"
        if limit:
            query = f"{query} LIMIT {limit}"
        if offset:
            query = f"{query} OFFSET {offset}"
        try:
            results = cls.db_obj.fetch(query)
        except dbError as err:
            print(f'Error while fetching from "{cls.name}".')
            print(f"Error description: {err}")
            return []
        else:
            return results

    @classmethod
    def fetch_obj(
        cls,
        where: str = None,
        order_by: str = None,
        descending: bool = False,
        limit: int = None,
        offset: int = None,
    ) -> List["BaseModel"]:
        """Executes select query in the table of model instance.

        Returns:
            "BaseModel": List of fetched rows as instances of the class
        """
        results = cls.fetch(
            select="*",
            where=where,
            order_by=order_by,
            descending=descending,
            limit=limit,
            offset=offset,
        )
        if results:
            return [cls(**item) for item in results]
        else:
            return results

    def get_comma_seperated(self, columns: List[Column]) -> str:
        """Get value of instance attributes as a comma seperated string

        Args:
            columns (List[Column]): list of column o return their values

        Returns:
            str: comma seperated string
        """
        obj_dict = self.__dict__
        values = ""
        for column in columns:
            if isinstance(obj_dict[column.name], Enum):
                v = obj_dict[column.name].value
            else:
                v = obj_dict[column.name]
            if column.as_string:
                values = f'{values}"{v}",'
            else:
                values = f"{values}{v},"
        return values

    def insert(self) -> None:
        """Executes insert in the table of model instance.

        Returns:
            None
        """
        cls = self.__class__
        columns = []
        set_from_db = None
        for column in cls.get_columns():
            if not column.auto_increment:
                columns.append(column)
            else:
                set_from_db = column
        columns = [column for column in columns if not column.auto_increment]
        column_names = [column.name for column in columns]
        clm = ", ".join(tuple(column_names))
        values = self.get_comma_seperated(columns)
        query = f"INSERT INTO {cls.name} ({clm})\nVALUES ({values[:-1]});"
        try:
            _, rowid = self.db_obj.execute(query)
        except IntegrityError as err:
            print(f'Error while inserting new row into "{cls.name}".')
            print(f"Error description: {err}")
            raise DuplicatedEntry(err.msg)
        except dbError as err:
            print(f'Error while inserting new row into "{cls.name}".')
            print(f"Error description: {err}")
        else:
            if set_from_db:
                self.__dict__[set_from_db.name] = rowid

    def update_query(self, colval: Dict[Column, Any], where: str = "default") -> str:
        """Generates the query for updating with specified inputs

        Args:
            colval (Dict[Column, Any]): A dictionary where keys are Column to update and \
                its value is the new value of the column.
            where (str, optional): Condition for updating if equal to 'default' \
                it will generate update query based on primary keys. Defaults to "default".

        Returns:
            str: query for updating
        """
        query = f"UPDATE {self.name} SET"
        for column in colval:
            query = f'{query} {column.name} = "{colval[column]}",'
        query = f"{query[:-1]} WHERE"
        if where == "default":
            cls = self.__class__
            obj_dict = self.__dict__
            pks = cls.get_primary_keys()
            for pk in pks:
                query = f'{query} {pk.name}="{obj_dict[pk.name]}" AND'
            query = f"{query[:-4]};"
            return query
        else:
            query = f"{query} {where}"
            return query

    def update(self, colval: Dict[Column, Any], where: str = "default") -> int:
        """Update row(s) with specified inputs

        Args:
            colval (Dict[Column, Any]): A dictionary where keys are Column to update and \
                its value is the new value of the column.
            where (str, optional): Condition for updating if equal to 'default' \
                it will generate update query based on primary keys. Defaults to "default".

        Returns:
            int: number of rows affected.
        """
        query = self.update_query(colval, where)
        try:
            rowcount, _ = self.db_obj.execute(query)
        except IntegrityError as err:
            print(f'Error while inserting new row into "{self.name}".')
            print(f"Error description: {err}")
            raise DuplicatedEntry(err.msg)
        except dbError as err:
            print(f'Error updating "{self.name}".')
            print(f"Error description: {err}")
            return 0
        else:
            for column in colval:
                self.__dict__[column.name] = colval[column]
            return rowcount

    def delete(self, where: str = "default") -> int:
        pass


class UserRole(Enum):
    ADMIN = "admin"
    STAFF = "staff"
    USER = "user"

    @classmethod
    def get_comma_seperated(cls) -> str:
        """Returns a comma seperated string of the Enum class values.

        Returns:
            str: comma seperated string
        """
        return ", ".join([f"'{role.value}'" for role in cls])
