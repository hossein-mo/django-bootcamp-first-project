import os
import sys
import unittest
from datetime import datetime, date

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), "models"))

from models.models import User
from models.models import Column, BaseModel


class TestDivarScraper(unittest.TestCase):
    def test_column_call(self):
        c = Column("test", "VARCHAR(255)", null=True, auto_increment=True)
        self.assertEqual(c(), "test VARCHAR(255) DEFAULT NULL AUTO_INCREMENT,")

    def test_custom_table(self):
        class Table(BaseModel):
            name = "table"
            id = Column("id", "INT UNSIGNED", primary_key=True)
            id2 = Column("id2", "INT UNSIGNED", primary_key=True)
            test_column = Column("test_column", "VARCHAR(255)", null=True)

        query = Table.create_table()
        self.assertEqual(
            query,
            "CREATE TABLE table (\nid INT UNSIGNED NOT NULL,\nid2 INT UNSIGNED NOT NULL,\ntest_column VARCHAR(255) DEFAULT NULL,\nPRIMARY KEY (id, id2)\n);",
        )

    def test_custom_table(self):
        class Table(BaseModel):
            name = "table"
            id = Column("id", "INT UNSIGNED", primary_key=True)
            id2 = Column("id2", "INT UNSIGNED", primary_key=True)
            test_column = Column("test_column", "VARCHAR(255)", null=True)

            def __init__(self, id, id2, test_column):
                self.id = id
                self.id2 = id2
                self.test_column = test_column

        tab = Table(1, 2, "hi")
        query = tab.insert()
        self.assertEqual(
            query,
            'INSERT INTO table (id, id2, test_column)\nVALUES ("1","2","hi");',
        )

    def test_user_model_create_table(self):
        query = User.create_table()
        self.assertEqual(
            query,
            "CREATE TABLE user (\n\
id INT UNSIGNED NOT NULL AUTO_INCREMENT,\n\
username VARCHAR(255) NOT NULL,\n\
password CHAR(64) NOT NULL,\n\
email VARCHAR(255) NOT NULL,\n\
phone_number VARCHAR(255) DEFAULT NULL,\n\
wallet INT UNSIGNED NOT NULL,\n\
role ENUM('admin', 'staff', 'user') NOT NULL DEFAULT 'user',\n\
birth_date DATE NOT NULL,\n\
register_date DATETIME NOT NULL,\n\
last_login DATETIME NOT NULL,\n\
PRIMARY KEY (id)\n\
);",
        )

    def test_user_model_insert(self):
        d = date.today()
        dt = datetime.now()
        user = User(
            "ali",
            "securepass",
            "email@unchained.com",
            "09123456789",
            500000,
            "admin",
            d,
            dt,
            dt,
        )
        query = user.insert()
        self.assertEqual(
            query,
            f'INSERT INTO user (username, password, email, phone_number, wallet, role, birth_date, register_date, last_login)\nVALUES ("ali","securepass","email@unchained.com","09123456789","500000","admin","{d}","{dt}","{dt}");',
        )


if __name__ == "__main__":
    unittest.main()
