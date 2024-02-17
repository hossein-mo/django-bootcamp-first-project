from datetime import date, datetime, timedelta
from typing import Any
from controllers.handlers.abstract_handler import AbstractHandler
from utils.exceptions import NotFound
from models.models import Subscription, UserSubscription, Order, Showtime


class SubCheck(AbstractHandler):
    """
    Handler for checking if the requested sub exists or not

    """

    def handle(self, data: dict) -> dict | None:
        sub_id = int(data["subs_id"])
        subs = Subscription.fetch_obj(where=f"{Subscription.id} = {sub_id}")
        if not subs:
            raise NotFound("Requested subscription not found!")
        subs = subs[0]
        data["subs"] = subs
        data["amount"] = subs.price
        if self._next_handler:
            return super().handle(data)
        else:
            return data


class BuySub(AbstractHandler):
    """
    Handler for buying subscription

    """

    def handle(self, data: dict) -> dict | None:
        user = data["user"]
        subs = data["subs"]
        UserSubscription.set_user_subscription(user, subs)
        user_sub = UserSubscription.fetch_obj(
            where=f"{UserSubscription.user_id}={user.id} AND {UserSubscription.expire_date} > NOW()"
        )
        if user_sub:
            user_sub = user_sub[-1]
        user.subs = subs
        user.sub_exp = subs.duration
        user.user_sub = user_sub
        data["user_sub"] = user_sub
        if self._next_handler:
            return super().handle(data)
        else:
            return data


class CreateSubInovice(AbstractHandler):
    """
    Handler for generating sunscription invoice

    """

    def handle(self, data: dict) -> dict | None:
        subs = data["subs"]
        user_sub = data["user_sub"]
        data["inovice"] = {
            "subs_name": subs.s_name,
            "buy_date": user_sub.buy_date,
            "duration": subs.duration,
            "expire_date": user_sub.expire_date,
            "price": data["amount"],
        }
        if self._next_handler:
            return super().handle(data)
        else:
            return data


class ShowtimeCheck(AbstractHandler):
    """
    Handler for checking if requested show time has passed or not
    """

    def handle(self, data: dict) -> dict | None:
        show_id = int(data["show_id"])
        data["show_id"] = show_id
        show = Showtime.fetch_obj(
            where=f'{Showtime.id} = "{show_id}" AND {Showtime.start_date} > NOW()'
        )
        if not show:
            raise NotFound("Show doesn't exist or its time has passed")
        show = show[0]
        data["show"] = show
        if self._next_handler:
            return super().handle(data)
        else:
            return data


class CalculateDiscountedPrice(AbstractHandler):
    """
    Handler for calculating disounted price if exists

    """

    def handle(self, data: dict) -> dict | None:
        user = data["user"]
        show = data["show"]
        today = date.today()
        if today.month == user.birth_date.month and today.dat == user.birth_date.day:
            discount = 50
        elif user.user_sub:
            if user.user_sub.expire_date > datetime.now():
                if user.subs.order_number:
                    orders_with_discount = Order.fetch(
                        where=f'{Order.user_id} = "{user.id}" AND '
                        + f'{Order.create_date} > "{user.user_sub.buy_date}" '
                        + f'AND {Order.discount} = "{user.subs.discount}"'
                    )
                    if len(orders_with_discount) >= user.subs.order_number:
                        discount = 0
                    else:
                        discount = user.subs.discount
                else:
                    discount = user.subs.discount
        price = int(show.price * (1 - (discount / 100)))
        data["amount"] = price
        data["price"] = price
        data["discount"] = discount
        data["pre_invoice"] = {"price": price, "discount": discount}
        if self._next_handler:
            return super().handle(data)
        else:
            return data


class SeatCheck(AbstractHandler):
    """
    Handler for checking for seat avalibility

    """

    def handle(self, data: dict) -> dict | None:
        show_id = data["show_id"]
        seat_number = int(data["seat_number"])
        data["seat_number"] = seat_number
        capacity = Showtime.get_showtime_capacity(show_id)
        if seat_number > capacity:
            raise NotFound("Requested seat doesn't exist.")
        check_seat = Order.fetch(
            where=f'{Order.showtime_id} = "{show_id}" '
            + f'AND {Order.seat_number} = "{seat_number}"'
        )
        if check_seat:
            raise NotFound("Requested seat is already reserved by someone else.")
        if self._next_handler:
            return super().handle(data)
        else:
            return data


class ReserveSeat(AbstractHandler):
    """
    Handler for reserving seat

    """

    def handle(self, data: dict) -> dict | None:
        user = data["user"]
        order = Order(user.id, data["show_id"], data["seat_number"], data["discount"])
        order.insert()
        data["order"] = order
        if self._next_handler:
            return super().handle(data)
        else:
            return data


class CreateOrderInovice(AbstractHandler):
    """
    Handler for generating seat reservation invoice

    """

    def handle(self, data: dict) -> dict | None:
        order = data["order"]
        data["inovice"] = {
            "order_id": order.id,
            "show_id": order.showtime_id,
            "seat_number": order.seat_number,
            "discount": order.discount,
            "price": data["price"],
        }
        if self._next_handler:
            return super().handle(data)
        else:
            return data


class CalculateCancelationFine(AbstractHandler):
    """
    Handler for calculating cancelation fine

    """

    def handle(self, data: dict) -> dict | None:
        order_id = int(data["order_id"])
        user = data["user"]
        order = Order.fetch_obj(
            where=f'{Order.id} = "{order_id}" AND {Order.user_id} = "{user.id}"'
        )
        if not order:
            raise NotFound("Order not found!")
        order = order[0]
        if order.cancel_date:
            raise NotFound("Order already canceled!")
        show = Showtime.fetch_obj(where=f'{Showtime.id}="{order.showtime_id}"')[0]
        data["show"] = show
        data["order"] = order
        time_now = datetime.now()
        if time_now >= show.start_date:
            fine = 100
        elif (show.start_date - time_now).total_seconds() < 3600:
            fine = 18
        else:
            fine = 0
        data["fine"] = fine
        if self._next_handler:
            return super().handle(data)
        else:
            return data


class CancelOrder(AbstractHandler):
    """
    Handler for canceling reservation

    """

    def handle(self, data: dict) -> dict | None:
        user = data["user"]
        fine = data["fine"]
        order = data["order"]
        refund = order.cancel_order(user, fine)
        data["refund"] = refund
        if self._next_handler:
            return super().handle(data)
        else:
            return data


class CancelInvoice(AbstractHandler):
    """
    Handler for generating cancelation invoice

    """

    def handle(self, data: dict) -> dict | None:
        user = data["user"]
        fine = data["fine"]
        order = data["order"]
        refund = data["refund"]
        data["inovice"] = {
            "order_id": order.id,
            "show_id": order.showtime_id,
            "fine": fine,
            "refund_amount": refund["refund_amount"],
            "paid_price": refund["paid_price"],
        }
        if self._next_handler:
            return super().handle(data)
        else:
            return data
