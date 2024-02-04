from mysql.connector import dbError

from controllers.exceptions import *
from base_models import Column, BaseModel
from subscription import Subscription
from user import User

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
        queries = []
        duration = Subscription.fetch(select=f'{Subscription.duration.name}', where=f'{Subscription.id.name}={subscription.id}')
        duration - duration[0][Subscription.duration.name]
        price = Subscription.fetch(select=f'{Subscription.price.name}', where=f'{Subscription.id.name}={subscription.id}')
        price = price[0][Subscription.price.name]
        if user.subscription is not None:
                queries.append(f'UPDATE {UserSubscription.name} SET {UserSubscription.expire_date.name} = now() WHERE \
                               {UserSubscription.id.name} = (SELECT {UserSubscription.id.name} from {UserSubscription.name} WHERE \
                                    {UserSubscription.user_id.name} = {user.id} AND {UserSubscription.expire_date.name}>now())')
                
        queries.append(f'UPDATE {User.name} SET {User.wallet.name}={User.wallet.name} - {price} WHERE {User.id.name} = {user.id}')
        queries.append(f'INSERT INTO {UserSubscription.name} VALUES ({user.id}, {subscription.id}, NOW(), DATE_ADD(NOW(), INTERVAL {duration} DAY))')
        
        try:
            UserSubscription.db_obj.transaction(queries)
        except dbError as err:
            # print(f'Error while updating rows in "{self.name}".')
            print(f"Error description: {err}")

