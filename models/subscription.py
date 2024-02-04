from typing import Union

from controllers.exceptions import *
from base_models import Column, BaseModel

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
        self.insert()

    def edit_subscription(self):
        self.update({Subscription.s_name : self.name, Subscription.discount : self.discount, \
                     Subscription.duration : self.duration, Subscription.order_number : self.order_number})

    def delete_subscription(self):
        self.delete()


  
