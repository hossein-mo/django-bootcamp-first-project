import os
import sys
import re
from datetime import date, datetime, timedelta
from typing import Any, Dict, Optional, List

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from controllers.handlers.abstract_handler import AbstractHandler
from utils.exceptions import NotFound
from models.models import Subscription, UserSubscription, Order, Showtime


class SubCheck(AbstractHandler):
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
    def handle(self, data: dict) -> dict | None:
        user = data["user"]
        subs = data["subs"]
        datetime_now = datetime.now()
        datetime_expire = datetime_now + timedelta(days=subs.duration)
        user_sub = UserSubscription(user.id, subs.id, datetime_now, datetime_expire)
        user_sub.insert()
        user.subs = subs
        user.sub_exp = subs.duration
        data["user_sub"] = user_sub
        if self._next_handler:
            return super().handle(data)
        else:
            return data


class CreateSubInovice(AbstractHandler):
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
