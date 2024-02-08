import os
import sys
import re
from datetime import date
from typing import Any, Dict, Optional, List

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from controllers.handlers.abstract_handler import AbstractHandler
from controllers.exceptions import NotEnoughBalance, InvalidRequest, WrongBankAccCreds
from models.models import User, BankAccount
from utils.utils import hash_password


class UserAccounts(AbstractHandler):
    def handle(self, data: dict) -> dict:
        user = data["user"]
        accounts = BankAccount.fetch_obj(where=f'{BankAccount.user_id} = "{user.id}"')
        data["accounts"] = accounts
        if self._next_handler:
            return super().handle(data)
        else:
            return data


class Objectify(AbstractHandler):
    def handle(self, data: dict) -> dict | None:
        origin = data['origin']
        dest = data['dest']
        user = data['user']
        if isinstance(origin, int):
            origin_acc = BankAccount.fetch_obj(where=f'{BankAccount.id} = "{origin}" AND {BankAccount.user_id} = "{user.id}"')
            if origin_acc:
                data['origin'] = origin_acc[0]
            else:
                raise InvalidRequest
        elif origin == 'user_balance':
            data['origin'] = user
        if isinstance(dest, int):
            dest_acc = BankAccount.fetch_obj(where=f'{BankAccount.id} = "{dest}" AND {BankAccount.user_id} = "{user.id}"')
            if dest_acc:
                data['dest'] =dest_acc[0]
            else:
                raise InvalidRequest
        elif dest =='user_balance':
            data['dest'] = user
        if self._next_handler:
            return super().handle(data)
        else:
            return data


class BalanceCheck(AbstractHandler):
    def handle(self, data: dict) -> dict:
        if data['origin'] == 'deposit':
            amount = data["amount"]
            origin = data["origin"]
        if amount > origin.balance:
            raise NotEnoughBalance
        if self._next_handler:
            return super().handle(data)
        else:
            return data
        
class AccountCredentialsCheck(AbstractHandler):
    def handle(self, data: dict) -> dict:
        if isinstance(data['origin'], BankAccount):
            bk = data['origin']
            password = data['password']
            cvv2 = data['cvv2']
            if hash_password(password) != bk.password or cvv2 != bk.cvv2:
                raise WrongBankAccCreds
        if self._next_handler:
            return super().handle(data)
        else:
            return data

class TransferHandler(AbstractHandler):
    def handle(self, data: dict) -> dict:
        if data['origin'] == 'deposit':
            pass
        elif data['dest'] == 'withdrawal':
            pass
        status = BankAccount.transfer(data['origin'], data['dest'], data['amount'])
        data['status'] = status
        if self._next_handler:
            return super().handle(data)
        else:
            return data