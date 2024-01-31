
from controllers.exceptions import InsertFailed, UpdateFailed
from models.subscription import Subscription

class SubscriptionRepository:
    @staticmethod
    def insert_subscription(subscription: Subscription):
        #try:
        #INSERT INTO Subscription Values (subscription.name, subscription.discount, subscription.duration, subscription.order_number)
        #except mysql.connector.Error as err:
        #     raise InsertFailed("Some problem occured while register new subscription. Try again!")
        pass

    @staticmethod
    def update_subscription(subscription: Subscription):
        # UPDATE Subscription SET name = subscription.name, discount = subscription.discount, duration = subscription.duration, \
        #order_number= subscription.order_number WHERE id = subscription.id"
        pass
    
    @staticmethod
    def delete_subscription(subscription: Subscription):
        # DELETE Subscription WHERE id = subscription.id
        pass

    # mitoonam user begiram va haminja check konam eshterak dare ya na   
    @staticmethod
    def set_user_subscription(user_id, subscription_id):
        # cursor = conn.cursor()
        # try:
        #     cursor.execute("START TRANSACTION")
        #     cursor.execute("UPDATE User_Subscription SET expiry_date = now() WHERE user_id = ? AND \
        #                    expire_date=(SELECT expire_date from User_Subscription WHERE user_id = ? AND expire_date>now())")
        #     cursor.execute("UPDATE User SET wallet=wellet - (SELECT price from Subscription WHERE id=?) WHERE user_id = ?")
        #     cursor.execute("INSERT INTO User_Subscription VALUES (user_id, subscription_id, now(), now()+(SELECT duration from Subscription WHERE id=?))")
        #     # Commit the transaction if all updates are successful
        #     conn.commit()
        # except mysql.connector.Error as err:
        #     # Rollback the transaction if any of the updates fail
        #     conn.rollback()
        #     print("Transaction rolled back: {}".format(err))
        #     raise InsertFailed("Some problem occured while register subscription. Try again!")
        # finally:
        #     cursor.close()
        #     conn.close()
        pass
            
    # @staticmethod
    # def check_user_subscription(user_id) -> Subscription:
    #     #SELECT * from User_Subscription where user_id=? AND expiry_date > now()
    #     pass

    # @staticmethod
    # def get_user_discount(user_id):
    #     # SELECT discount from Subscription WHERE id = (SELECT subscription_id from User_Subscription WHERE user_id = ? AND expire_date > now())
    #     pass