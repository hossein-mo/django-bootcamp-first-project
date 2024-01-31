import datetime

from repositories.subscription_repo import SubscriptionRepository

class Subscription:
    def __init__(self, name, discount, durattion=datetime.timedelta(days=30).total_seconds(), order_number=0):
        self.name = name
        self.discount = discount
        self.durattion = durattion
        self.order_number = order_number
    
    def set_new_subscription(self):
        SubscriptionRepository.insert_subscription(self)

    def update_subscription(self):
        SubscriptionRepository.update_subscription(self)

    def delete_subscription(self):
        SubscriptionRepository.delete_subscription(self)
    
    
    @staticmethod
    def set_user_subscription(user, subscription):
        SubscriptionRepository.set_user_subscription(user.id, subscription.id)

    
    # @staticmethod
    # def check_user_subscription(user) -> 'Subscription':
    #     return SubscriptionRepository.check_user_subscription(user.id)
    # @staticmethod
    # def get_user_discount(user):
    #     discount = SubscriptionRepository.get_user_discount(user.id)
    #     return discount if discount is not None else 0