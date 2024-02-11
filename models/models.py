import os
import sys
from datetime import datetime, date
from mysql.connector import Error as dbError
from typing import Union, Dict, List
from abc import ABC, abstractmethod

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from utils.utils import hash_password
from models.base_models import Column, UserRole, BaseModel
from utils.exceptions import WrongCredentials, DuplicatedEntry, DatabaseError


class User(BaseModel):
    name = "user"
    id = Column("id", "INT UNSIGNED", primary_key=True, auto_increment=True)
    username = Column("username", "VARCHAR(255)", unique=True)
    password = Column("password", "CHAR(64)")
    email = Column("email", "VARCHAR(255)", unique=True)
    phone_number = Column("phone_number", "VARCHAR(255)", null=True)
    balance = Column("balance", "INT UNSIGNED")
    role = Column(
        "role", f"ENUM({UserRole.get_comma_seperated()})", default=UserRole.USER.value
    )
    birth_date = Column("birth_date", "DATE")
    register_date = Column("register_date", "DATETIME")
    last_login = Column("last_login", "DATETIME")

    def __init__(
        self,
        username: str,
        password: str,
        email: str,
        phone_number: str,
        balance: int,
        role: Union[str, UserRole],
        birth_date: date,
        register_date: datetime,
        last_login: datetime,
        id: Union[int, None] = None,
        accounts: Union[list, None] = None,
        subs: Union["Subscription", None] = None,
        sub_exp: Union[int, str] = None,
    ) -> None:
        """Constructor for user model

        Args:
            username (str): username
            password (str): user password
            email (str): user email
            phone_number (str): user phone_number
            balance (int): user wallet balance
            role (Union[str, UserRole]): user role
            birth_date (date): user birth_date
            register_date (datetime): user register_date
            last_login (datetime): user last_login
            id (Union[int, None], optional): user id generated by db when inserting. Defaults to None.
        """
        self.id = id
        self.username = username
        self.password = password
        self.email = email
        self.role = UserRole(role)
        self.birth_date = birth_date
        self.register_date = register_date
        self.last_login = last_login
        self.phone_number = phone_number
        self.balance = balance
        self.accounts = accounts
        self.subs = subs
        self.sub_exp = sub_exp

    def info(self) -> dict:
        return {
            "username": self.username,
            "email": self.email,
            "phone_number": self.phone_number,
            "birth_date": self.birth_date,
            "last_login": self.last_login,
            "register_date": self.register_date,
            "subs": self.subs.s_name,
            "subs_expires_in": self.sub_exp,
            "balance": self.balance,
            "role": self.role.value,
        }

    def update_last_login(self) -> None:
        """Updated the last login time of the user in database to now"""
        self.last_login = datetime.now()
        self.update({User.last_login: self.last_login})

    @staticmethod
    def authenticate(usercred: Dict[str, str]) -> "User":
        """_summary_

        Args:
            username (str): username
            password (str): password

        Raises:
            UserNotExist: if user with input username dosen't exist in database
            WrongCredentials: if input password doesn't match the user password

        Returns:
            User: authenticate user
        """
        password = hash_password(usercred["password"])
        if "username" in usercred:
            login_with = "username"
            cred = usercred["username"]
            user = User.fetch_obj(where=f'{User.username} = "{usercred["username"]}"')
        else:
            login_with = "email"
            cred = usercred["email"]
            user = User.fetch_obj(where=f'{User.email} = "{usercred["email"]}"')
        if not user:
            err = WrongCredentials()
            User.loging.log_action(f"{err.message} {login_with} = {cred}")
            raise err
        else:
            user = user[0]
            if user.password != password:
                err = WrongCredentials()
                User.loging.log_action(f"{err.message} {login_with} = {cred}")
                raise err
            User.loging.log_action(
                f"User logged in with user id = {user.id} username = {user.username} and email = {user.email}"
            )
            accounts = BankAccount.fetch_obj(where=f"{BankAccount.user_id}={user.id}")
            user.accounts = {}
            if accounts:
                for acc in accounts:
                    user.accounts[acc.id] = acc
            user_sub = UserSubscription.fetch_obj(
                where=f"{UserSubscription.user_id}={user.id} AND {UserSubscription.expire_date} > NOW()"
            )
            if user_sub:
                user_sub = user_sub[0]
                subs = Subscription.fetch_obj(
                    where=f"{Subscription.id} = {user_sub.subscription_id}"
                )
                sub_exp = (user_sub.expire_date - datetime.now()).days
            else:
                sub_exp = "unlimited"
                subs = Subscription("Bronze", 0, duration="unlimited")
            user.subs = subs[0]
            user.sub_exp = sub_exp
            return user

    @classmethod
    def create_new(
        cls,
        username: str,
        password: str,
        email: str,
        phone_number: str,
        role: Union[str, UserRole],
        birth_date: Dict[str, int],
    ) -> "User":
        """_summary_

        Args:
            username (str): username
            password (str): user password
            email (str): user email
            phone_number (str): user phone_number
            role (Union[str, UserRole]): user role
            birth_date (date): user birth_date

        Returns:
            User: return a User instance with specified inputs with \
                wallet balance set to zero and hashed password.
        """
        password = hash_password(password)
        rightnow = datetime.now()
        sub_exp = "unlimited"
        subs = Subscription("Bronze", 0, duration=sub_exp)
        user = cls(
            username,
            password,
            email,
            phone_number,
            0,
            role,
            birth_date,
            rightnow,
            rightnow,
            subs=subs,
            sub_exp=sub_exp,
        )
        user.insert()
        User.loging.log_action(f"New user registerd. userinfo: {user.info()}")
        return user


class BankAccount(BaseModel):
    name = "bank_account"
    id = Column("id", "INT UNSIGNED", primary_key=True, auto_increment=True)
    card_number = Column("card_number", "CHAR(16)")
    cvv2 = Column("cvv2", "varchar(255)")
    password = Column("password", "CHAR(64)")
    balance = Column("balance", "INT UNSIGNED")
    user_id = Column(
        "user_id", "INT UNSIGNED", foreign_key=User.id.name, reference=User.name
    )

    def __init__(
        self,
        card_number: str,
        cvv2: str,
        password: str,
        balance: int,
        user_id: int,
        id: Union[None, int] = None,
    ) -> None:
        """Constructor for bank account model

        Args:
            card_number (str): card number
            cvv2 (str): cvv2
            password (str): card password
            balance (int): account balance
            user_id (int): account owner user id
            id (Union[None, str], optional): bank account id. Defaults to None.
        """
        self.id = id
        self.card_number = card_number
        self.cvv2 = cvv2
        self.password = password
        self.balance = balance
        self.user_id = user_id

    def info(self) -> dict:
        return {
            "id": self.id,
            "card_number": self.card_number,
            "balance": self.balance,
        }

    def update(self):
        self.update(
            {
                BankAccount.card_number: self.card_number,
                BankAccount.cvv2: self.cvv2,
                BankAccount.password: self.password,
            }
        )

    @staticmethod
    def deposit(account: Union[User, "BankAccount"], amount: int) -> None:
        """Add amount to user's balance and update database.

        Args:
            amount (int): amount to deposit
        """
        acc_cls = account.__class__
        account.update({acc_cls.balance: account.balance + amount})
        account.balance += amount
        return True

    @staticmethod
    def withdraw(account: Union[User, "BankAccount"], amount: int) -> None:
        acc_cls = account.__class__
        account.update({acc_cls.balance: account.balance - amount})
        account.balance -= amount
        return True

    @staticmethod
    def transfer(
        origin: Union[User, "BankAccount"],
        dest: Union[User, "BankAccount"],
        amount: int,
    ) -> bool:
        """Transfer amount from instance balance to destination instance balance.

        Args:
            other (BankAccount): destination account
            amount (int): amount of transfer
        """
        origin_cls = origin.__class__
        dest_cls = dest.__class__
        query1 = origin.update_query({origin_cls.balance: origin.balance - amount})
        query2 = dest.update_query({dest_cls.balance: dest.balance + amount})
        origin_cls.db_obj.transaction([query1, query2])
        origin.balance -= amount
        dest.balance += amount
        return True

    @classmethod
    def create_new(
        cls, card_number: str, cvv2: str, password: str, balance: int, user_id: int
    ) -> "BankAccount":
        """_summary_

        Args:
            card_number (str): card number
            cvv2 (str): cvv2
            password (str): card password
            balance (int): account balance
            user_id (int): account owner user id

        Returns:
            BankAccount: return an instance of BankAccount with hashed password
        """
        password = hash_password(password)
        account = cls(card_number, cvv2, password, balance, user_id)
        account.insert()
        User.loging.log_action(
            f"New bank account added. card_number: {account.card_number}, user_id: {account.user_id}"
        )
        return account


class Subscription(BaseModel):
    name = "subscription"
    id = Column("id", "INT UNSIGNED", primary_key=True, auto_increment=True)
    s_name = Column("s_name", "VARCHAR(255)")
    discount = Column("discount", "SMALLINT UNSIGNED")
    duration = Column("duration", "SMALLINT UNSIGNED")
    order_number = Column("order_number", "VARCHAR(255)", null=True)

    def __init__(
        self,
        s_name: str,
        discount: int,
        duration=30,
        order_number=0,
        id: Union[int, None] = None,
    ):
        self.id = id
        self.s_name = s_name
        self.discount = discount
        self.duration = duration
        self.order_number = order_number

    def set_new_subscription(self):
        self.insert()

    def update_subscription(self):
        self.update(
            {
                Subscription.s_name: self.s_name,
                Subscription.discount: self.discount,
                Subscription.duration: self.duration,
                Subscription.order_number: self.order_number,
            }
        )

    def delete_subscription(self):
        self.delete()


class Movie(BaseModel):
    name = "movie"
    id = Column("id", "INT UNSIGNED", primary_key=True, auto_increment=True)
    m_name = Column("m_name", "VARCHAR(255)")
    duration = Column("duration", "SMALLINT UNSIGNED")
    age_rating = Column("age_rating", "SMALLINT UNSIGNED")
    screening_number = Column("screening_number", "SMALLINT UNSIGNED")

    def __init__(
        self,
        m_name: str,
        duration: int,
        age_rating: int,
        screening_number: int = 0,
        id: Union[int, None] = None,
        rate=0,
    ) -> None:
        self.id = id
        self.m_name = m_name
        self.duration = duration
        self.age_rating = age_rating
        self.screening_number = screening_number
        self.rate = rate

    @classmethod
    def get_movies_list(cls) -> list["Movie"]:
        query = f"SELECT {Movie.name}.*, {MovieRate.rate} from {Movie.name} \
                  LEFT JOIN (SELECT {MovieRate.movie_id.name}, \
                  SUM({MovieRate.rate.name})/COUNT({MovieRate.rate.name}) as {MovieRate.rate} from {MovieRate.name} \
                  GROUP BY {MovieRate.movie_id.name}) rt ON {Movie.name}.{Movie.id.name}=rt.{MovieRate.movie_id.name}"
        results = cls.db_obj.fetch(query)
        return results


class MovieRate(BaseModel):
    name = "movie_rate"
    user_id = Column(
        "user_id",
        "INT UNSIGNED",
        primary_key=True,
        foreign_key=User.id.name,
        reference=User.name,
    )
    movie_id = Column(
        "movie_id",
        "INT UNSIGNED",
        primary_key=True,
        foreign_key=Movie.id.name,
        reference=Movie.name,
    )
    rate = Column("rate", "INT UNSIGNED")

    def __init__(
        self,
        user_id,
        movie_id,
        name: str,
        rate: int,
        id: Union[int, None] = None,
    ) -> None:
        self.id = id
        self.name = name
        self.rate = rate
        self.user_id = user_id
        self.movie_id = movie_id


class Comment(BaseModel):
    name = "comment"
    id = Column("id", "INT UNSIGNED", primary_key=True, auto_increment=True)
    user_id = Column(
        "user_id", "INT UNSIGNED", foreign_key=User.id.name, reference=User.name
    )
    movie_id = Column(
        "movie_id", "INT UNSIGNED", foreign_key=Movie.id.name, reference=Movie.name
    )
    parent_id = Column("parent_id", "INT UNSIGNED", foreign_key=id.name, reference=name)
    text = Column("text", "TEXT")
    created_at = Column("created_at", "DATE")

    def __init__(
        self,
        user_id,
        movie_id,
        parent_id,
        text,
        created_at=datetime.now(),
        id: Union[int, None] = None,
    ):
        self.id = id
        self.user_id = user_id
        self.movie_id = movie_id
        self.parent_id = parent_id
        self.text = text
        self.created_at = created_at
        self.replies = []

    @staticmethod
    def comment(user_id, movie_id, parent_id, text) -> None:
        Comment(None, user_id, movie_id, parent_id, text).insert()

    @staticmethod
    def get_comments(movie_id) -> list["Comment"]:
        result = []
        comments = Comment.fetch_obj(f"{Comment.movie_id} = {movie_id}")
        for i in range(len(comments)):
            if comments[i].parent_id == 0:
                result.append(comments[i])
            for j in range(i + 1, len(comments)):
                if comments[j].parent_id == comments[i].id:
                    comments[i].replies.append(comments[j])
        return result


class UserSubscription(BaseModel):
    name = "user_subscription"
    id = Column("id", "INT UNSIGNED", primary_key=True, auto_increment=True)
    user_id = Column(
        "user_id", "INT UNSIGNED", foreign_key=User.id.name, reference=User.name
    )
    subscription_id = Column(
        "subscription_id",
        "INT UNSIGNED",
        foreign_key=Subscription.id.name,
        reference=Subscription.name,
    )
    buy_date = Column("buy_date", "DATETIME")
    expire_date = Column("expire_date", "DATETIME")

    def __init__(
        self,
        user_id: int,
        subscription_id: int,
        buy_date: datetime,
        expire_date: datetime,
        id: int = None,
    ) -> None:
        self.id = id
        self.user_id = user_id
        self.subscription_id = subscription_id
        self.buy_date = buy_date
        self.expire_date = expire_date

    @staticmethod
    def set_user_subscription(user, subscription):
        queries = []
        duration = Subscription.fetch(
            select=f"{Subscription.duration.name}",
            where=f"{Subscription.id.name}={subscription.id}",
        )
        duration - duration[0][Subscription.duration.name]
        price = Subscription.fetch(
            select=f"{Subscription.price.name}",
            where=f"{Subscription.id.name}={subscription.id}",
        )
        price = price[0][Subscription.price.name]
        if user.subscription is not None:
            queries.append(
                f"UPDATE {UserSubscription.name} SET {UserSubscription.expire_date.name} = now() WHERE \
                               {UserSubscription.id.name} = (SELECT {UserSubscription.id.name} from {UserSubscription.name} WHERE \
                                    {UserSubscription.user_id.name} = {user.id} AND {UserSubscription.expire_date.name}>now())"
            )

        queries.append(
            f"UPDATE {User.name} SET {User.balance.name}={User.balance.name} - {price} WHERE {User.id.name} = {user.id}"
        )
        queries.append(
            f"INSERT INTO {UserSubscription.name} VALUES ({user.id}, {subscription.id}, NOW(), DATE_ADD(NOW(), INTERVAL {duration} DAY))"
        )

        try:
            UserSubscription.db_obj.transaction(queries)
        except dbError as err:
            # print(f'Error while updating rows in "{self.name}".')
            print(f"Error description: {err}")


class Theater(BaseModel):
    name = "theater"
    id = Column("id", "INT UNSIGNED", primary_key=True, auto_increment=True)
    t_name = Column("t_name", "VARCHAR(255)")
    capacity = Column("capacity", "INT UNSIGNED")

    def __init__(
        self, t_name: str, capacity: int, id: Union[int, None] = None, rate: int = 0
    ) -> None:
        self.id = id
        self.t_name = t_name
        self.capacity = capacity
        self.rate = rate

    @classmethod
    def get_theater_list(cls) -> list[dict]:
        query = f"SELECT {Theater.name}.*, {TheaterRate.rate} from {Theater.name} \
                  LEFT JOIN (SELECT {TheaterRate.theater_id}, \
                  SUM({TheaterRate.rate})/COUNT({TheaterRate.rate}) as {TheaterRate.rate} from {TheaterRate.name} \
                  GROUP BY {TheaterRate.theater_id}) rt ON {Theater.name}.{Theater.id}= rt.{TheaterRate.theater_id}"
        results = cls.db_obj.fetch(query)
        return results


class TheaterRate(BaseModel):
    name = "theater_rate"
    user_id = Column(
        "user_id",
        "INT UNSIGNED",
        primary_key=True,
        foreign_key=User.id.name,
        reference=User.name,
    )
    theater_id = Column(
        "theater_id",
        "INT UNSIGNED",
        primary_key=True,
        foreign_key=Theater.id.name,
        reference=Theater.name,
    )
    rate = Column("rate", "INT UNSIGNED")

    def __init__(
        self,
        user_id,
        theater_id,
        name: str,
        rate: int,
        id: Union[int, None] = None,
    ) -> None:
        self.id = id
        self.name = name
        self.rate = rate
        self.user_id = user_id
        self.theater_id = theater_id


class Showtime(BaseModel):
    name = "showtime"
    id = Column("id", "INT UNSIGNED", primary_key=True, auto_increment=True)
    movie_id = Column(
        "movie_id", "INT UNSIGNED", foreign_key=Movie.id.name, reference=Movie.name
    )
    theater_id = Column(
        "theater_id",
        "INT UNSIGNED",
        foreign_key=Theater.id.name,
        reference=Theater.name,
    )
    start_date = Column("start_date", "DATETIME")
    end_date = Column("end_date", "DATETIME")
    price = Column("price", "INT UNSIGNED")

    def __init__(
        self,
        movie_id,
        theater_id,
        start_date,
        end_date,
        price,
        id: Union[int, None] = None,
        movie: Movie = None,
        theater: Theater = None,
    ):
        self.id = id
        self.movie_id = movie_id
        self.theater_id = theater_id
        self.start_date = start_date
        self.end_date = end_date
        self.price = price
        self.movie = movie
        self.theater = theater

    def info(self) -> dict:
        return {
            "id": self.id,
            "movie_id": self.movie_id,
            "theater_id": self.theater_id,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "price": self.price,
        }

    def update_showtime(self):
        self.update(
            {
                Showtime.movie_id: self.movie_id,
                Showtime.theater_id: self.theater_id,
                Showtime.start_date: self.start_date,
                Showtime.end_date: self.end_date,
                Showtime.price: self.price,
            }
        )

    def get_reserved_seat(self) -> list[int]:
        """Returns reserved seat numbers of given show

        Returns:
            list: List of reserved seat number
        """
        results = Showtime.fetch(
            select=Order.seat_number.name,
            where=f"{Order.showtime_id.name} = {self.id} AND {Order.cancel_date.name} IS NULL",
        )
        return [d[Order.seat_number.name] for d in results]

    def get_showtime_capacity(self) -> int:
        """Returns the number of reserved seats"""
        reserved_seats = "reserved_seats"
        results = Showtime.fetch(
            select=f"COUNT(*) as reserved_seats",
            where=f"{Order.showtime_id.name} = {self.id} AND {Order.cancel_date.name} IS NULL",
        )
        return results[0][reserved_seats]

    @classmethod
    def get_shows_list(cls) -> list["Movie"]:
        """Returns list of shows along with related movie (also it's rate) and theater objects.

        Returns:
            list: List of Movies
        """
        showtime_id, movie_id, theater_id, rate = "s_id", "m_id", "t_id", "rate"
        sub_query = f"SELECT m.*, rate from {Movie.name} m \
                        LEFT JOIN (SELECT {MovieRate.movie_id.name}, \
                        SUM({MovieRate.rate.name})/COUNT({MovieRate.rate.name}) as {rate} from {MovieRate.name} \
                        GROUP BY {MovieRate.movie_id.name}) rt ON m.{Movie.id.name}=rt.{MovieRate.movie_id.name}"
        sub_query2 = f"SELECT {Theater.name}.*, {Theater.name}_{TheaterRate.rate} from {Theater.name} \
                  LEFT JOIN (SELECT {TheaterRate.theater_id}, \
                  SUM({TheaterRate.rate})/COUNT({TheaterRate.rate}) as {Theater.name}_{TheaterRate.rate} from {TheaterRate.name} \
                  GROUP BY {TheaterRate.theater_id}) rt ON {Theater.name}.{Theater.id}= rt.{TheaterRate.theater_id}"
        query = f"SELECT s.*, s.id as {showtime_id}, m.*, m.id as {movie_id}, th.*, th.id as {theater_id} \
                    FROM {Showtime.name} s \
                    JOIN ({sub_query}) m ON s.{Showtime.movie_id.name} = m.{Movie.id.name} \
                    JOIN ({sub_query2}) th ON s.{Showtime.theater_id.name} = th.{Theater.id.name} \
                    WHERE s.{Showtime.start_date.name} > now()"
        results = cls.db_obj.fetch(query)
        result_list = []
        for item in results:
            show_obj = cls(
                item[Showtime.movie_id.name],
                item[Showtime.theater_id.name],
                item[Showtime.start_date.name],
                item[Showtime.end_date.name],
                item[Showtime.price.name],
                item[showtime_id],
            )
            show_obj.movie = Movie(
                item[Movie.m_name.name],
                item[Movie.duration.name],
                item[Movie.age_rating.name],
                item[Movie.screening_number.name],
                item[movie_id],
                item[MovieRate.rate.name],
            ).info()
            show_obj.theater = Theater(
                item[Theater.t_name.name],
                item[Theater.capacity.name],
                item[theater_id],
                item[f"{Theater.name}_{TheaterRate.rate.name}"],
            ).info()
            result_list.append(show_obj.__dict__)
        return result_list


class Order(BaseModel):
    name = "order"
    id = Column("id", "INT UNSIGNED", primary_key=True, auto_increment=True)
    user_id = Column(
        "user_id", "INT UNSIGNED", foreign_key=User.id.name, reference=User.name
    )
    showtime_id = Column(
        "showtime_id",
        "INT UNSIGNED",
        foreign_key=Showtime.id.name,
        reference=Showtime.name,
    )
    seat_number = Column("seat_number", "SMALLINT UNSIGNED")
    discount = Column("discount", "SMALLINT UNSIGNED")
    create_date = Column("create_date", "DATETIME")
    cancel_date = Column("cancel_date", "DATETIME", null=True)

    def __init__(
        self,
        user_id,
        showtime_id,
        seat_number,
        discount,
        create_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        cancel_date: Union[str, None] = None,
        id: Union[int, None] = None,
    ):
        self.id = id
        self.user_id = user_id
        self.showtime_id = showtime_id
        self.seat_number = seat_number
        self.discount = discount
        self.create_date = create_date
        self.cancel_date = cancel_date

    def reserve(self):
        self.insert()

    def cancel_order(self, user: User, fine: int) -> None:
        """updates 'user' table set 'balance' ->  increase the balance equal to ticket price minus the fine
        and 'order' table set 'cancel_date' -> now.

        Args:
            user (User): logged in user
            fine (int): based on the time remaining until the start of the show

        Returns:
            None
        """
        showtime_price = Showtime.fetch(
            select=f"{Showtime.price}", where=f"{Showtime.id} = {self.showtime_id}"
        )[0][Showtime.price.name]
        current_date = datetime.now()
        formatted_date = current_date.strftime("%Y-%m-%d %H:%M:%S")
        query1 = user.update_query(
            {User.balance: user.balance + showtime_price * ((100 - fine) / 100)}
        )
        query2 = self.update_query({Order.cancel_date: formatted_date})
        try:
            self.db_obj.transaction([query1, query2])
        except dbError as err:
            print(f'Error while updating rows in "{self.name}" or "{user.name}.')
            print(f"Error description: {err}")

    @classmethod
    def get_user_orders(cls, user):
        results = Order.fetch_obj(
            where=f"{Order.user_id.name} = {user.id}",
            order_by={Order.create_date.name},
            descending=True,
        )
        return results
