from datetime import datetime
import mysql.connector

from controllers.exceptions import *
from models.database import DatabaseConnection
from models.base_models import Column, BaseModel
from models.subscription import Subscription
from models.user import User

class UserSubscription(BaseModel):
    name = "user_subscription"
    id = Column("id", "INT UNSIGNED", primary_key=True, auto_increment=True)
    user_id = Column(
        "user_id", "INT UNSIGNED", foreign_key=User.id.name, reference=User.name
    )
    subscription_id = Column(
        "subscription_id", "INT UNSIGNED", foreign_key=Subscription.id.name, reference=Subscription.name
    )
    buy_date = Column("buy_date", "DATETIME")
    expire_date = Column("expire_date", "DATETIME")

    
    @staticmethod
    def set_user_subscription(user, subscription):
        UserSubscriptionRepo.set_user_subscription(user, subscription.id)


class UserSubscriptionRepo:

    @staticmethod
    def set_user_subscription(user, subscription_id):
        conn = DatabaseConnection().get_connection()
        cursor = conn.cursor()
        query = ""
        try:
            cursor.execute("START TRANSACTION")
            if user.subscription is not None:
                query = f'UPDATE {UserSubscription.name} SET {UserSubscription.expiry_date.name} = now() WHERE \
                               {UserSubscription.user_id.name} = %s AND expire_date=(SELECT expire_date from {UserSubscription.name} WHERE \
                                    {UserSubscription.user_id.name} = %s AND {UserSubscription.expire_date.name}>now())'
                cursor.execute(query, (user.id, user.id,))
            query = f'UPDATE {User.name} SET {User.wallet.name}={User.wallet.name} - (SELECT {Subscription.price.name} \
                           from {Subscription.name} WHERE {Subscription.id.name}=%s) WHERE {User.id.name} = %s'
            cursor.execute(query, (subscription_id, user.id,))
            query = f'INSERT INTO {UserSubscription.name} VALUES (%s, %s, now(), now()+(SELECT {Subscription.duration.name} \
                        from {Subscription.name} WHERE {Subscription.id.name}=%s))'
            cursor.execute(query, (user.id, subscription_id, subscription_id,))
            conn.commit()
        except mysql.connector.Error as err:
            conn.rollback()
            raise InsertFailed("Some problem occurred while register subscription. Try again!")
        finally:
            cursor.close()
