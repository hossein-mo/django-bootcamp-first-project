from enum import Enum
from typing import Union, Any, List, Tuple
import mysql.connector

from models.database import DatabaseConnection


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
            foreign_key (Union[None, &quot;Column&quot;], optional): None for no foreign key \
                or the name of the referenced column. Defaults to False.
            reference (Union[None, &quot;BaseModel&quot;], optional): None for no foreign key \
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


class BaseModel:
    name: str

    @classmethod
    def get_columns(cls) -> list:
        """Create a list of class attributes that are instances of Column class.

        Returns:
            list: List of column instances.
        """
        columns = []
        for _, column in vars(cls).items():
            if isinstance(column, Column):
                columns.append(column)
        return columns

    # right now create_table() return the query in string, this will be edited later on to execute query on database using database object.
    @classmethod
    def create_table(cls) -> None:
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
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()
        cursor.execute(query)

    def get_comma_seperated(self, columns: List[Column]) -> str:
        """Get the value of model as a comma seperated string

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

    # right now insert() return the query in string, this will be edited later on to execute query on database using database object.
    def insert(self) -> None:
        """Executes insert in the table of model instance.

        Returns:
            None
        """
        cls = self.__class__
        columns = cls.get_columns()
        columns = [column for column in columns if not column.auto_increment]
        column_names = [column.name for column in columns]
        clm = ", ".join(tuple(column_names))
        values = self.get_comma_seperated(columns)
        query = f"INSERT INTO {cls.name} ({clm})\nVALUES ({values[:-1]});"
        conn = DatabaseConnection.get_connection()
        conn.cursor().execute(query)
        conn.commit()

    @classmethod
    def fetch(
        cls,
        select: Tuple[str] = ("*",),
        where: str = None,
        order_by: List[Tuple[str, bool]] = None,
        limit: int = None,
        offset: int = None,
    ) -> List[Tuple]:
        """Executes select query in the table of model instance.

        Returns:
            list: List of fetched rows as tuple of selected columns
        """
        query = f'SELECT {",".join(select)} FROM {cls.name}'
        if where:
            query = f"{query} WHERE {where}"
        if order_by:
            orders = ",".join(
                [f'{order[0]} {"ASC" if order[1] else "DESC"}' for order in order_by]
            )
            query = f"{query} ORDER BY {orders}"
        if limit:
            query = f"{query} LIMIT {limit}"
        if offset:
            query = f"{query} OFFSET {offset}"
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        print(cursor.rowcount)
        if select[0] == "*":
            columns = [column[0] for column in cursor.description]
            results = [dict(zip(columns, row)) for row in rows]
            return [cls(**item) for item in results]
        return rows


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
