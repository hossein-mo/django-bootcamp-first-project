from typing import Union
import mysql.connector

from controllers.exceptions import *
from models.database import DatabaseConnection
from models.base_models import Column, BaseModel

class Subscription(BaseModel):
    name = "subscription"
    id = Column("id", "INT UNSIGNED", primary_key=True, auto_increment=True)
    s_name = Column("name", "VARCHAR(255)")
    discount = Column("discount", "SMALLINT UNSIGNED")
    duration = Column("duration", "SMALLINT UNSIGNED")
    order_number = Column("order_number", "VARCHAR(255)", null=True)


    def __init__(self, name, discount, duration= 30, order_number=0, id: Union[int, None] = None):
        self.id = id
        self.name = name
        self.discount = discount
        self.duration = duration
        self.order_number = order_number
    
    def set_new_subscription(self):
        SubscriptionRepo.insert_subscription(self)

    def edit_subscription(self):
        SubscriptionRepo.update_subscription(self)

    def delete_subscription(self):
        SubscriptionRepo.delete_subscription(self)

    
    # @staticmethod
    # def check_user_subscription(user) -> 'Subscription':
    #     return SubscriptionRepository.check_user_subscription(user.id)
    # @staticmethod
    # def get_user_discount(user):
    #     discount = SubscriptionRepository.get_user_discount(user.id)
    #     return discount if discount is not None else 0
  

class SubscriptionRepo:
    @staticmethod
    def insert_subscription(subscription: Subscription):
        try:
            Subscription.insert(subscription)
        except mysql.connector.Error as err:
            raise InsertFailed("Some problem occurred while register new subscription. Try again!")

    @staticmethod
    def update_subscription(subscription: Subscription):
        try:
            conn = DatabaseConnection().get_connection()
            cursor = conn.cursor()
            query = f'UPDATE {Subscription.name} SET {Subscription.s_name.name} = %s, {Subscription.discount.name} = %s, \
                        {Subscription.duration.name} = %s, {Subscription.order_number.name} = %s WHERE {Subscription.id.name} = %s'
            cursor.execute(query, (subscription.name, subscription.discount, subscription.duration, subscription.order_number, subscription.id,))
            conn.commit()
        except mysql.connector.Error as err:
            raise UpdateFailed("Some problem occurred while updating subscription. Try again!")
        finally:
            cursor.close()
    
    @staticmethod
    def delete_subscription(subscription: Subscription):
        try:
            conn = DatabaseConnection().get_connection()
            cursor = conn.cursor()
            cursor.execute(f'DELETE FROM {Subscription.name} WHERE {Subscription.id.name} = {subscription.id}')
            conn.commit()
        except mysql.connector.Error as err:
            raise DeleteFailed("Some problem occurred while removing subscription. Try again!")
        finally:
            cursor.close()
  
