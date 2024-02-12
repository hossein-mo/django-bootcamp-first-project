import os
import sys
import re
from datetime import date
from typing import Any, Dict, Optional, List
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from controllers.handlers.abstract_handler import AbstractHandler
from utils.exceptions import NotEnoughBalance, InvalidRequest, WrongBankAccCreds
from models.models import User, BankAccount
from utils.utils import hash_password

class AddAccount(AbstractHandler):
    def handle(self, data: dict) -> dict:
        user = data['user']
        card_info = data['card_info']
        card_number = card_info['card_number']
        if len(card_number) != 16:
            raise InvalidRequest("Card number should be 16 digits.")
        duplicated_acc = BankAccount.fetch_obj(where=f'{BankAccount.card_number} = "{card_number}" AND {BankAccount.user_id} = "{user.id}"')
        if not duplicated_acc:
            card_info['balance'] = 0
            card_info['user_id'] = user.id
            b_account = BankAccount.create_new(**card_info)
            data['card_info'] = b_account.info()
            user.accounts[b_account.id] = b_account
        else:
            raise InvalidRequest("Duplicated card number, please add another card.")
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

class BalanceCheck(AbstractHandler):
    def handle(self, data: dict) -> dict:
        if data['origin'] != 'deposit':
            amount = data["amount"]
            origin = data["origin"]
            if amount > origin.balance:
                raise NotEnoughBalance
        if self._next_handler:
            return super().handle(data)
        else:
            return data
        
class TransferHandler(AbstractHandler):
    def handle(self, data: dict) -> dict:
        if data['origin'] == 'deposit':
            status = BankAccount.deposit(data['dest'], data['amount'])
        elif data['dest'] == 'withdraw':
            status = BankAccount.withdraw(data['origin'], data['amount'])
        else:
            status = BankAccount.transfer(data['origin'], data['dest'], data['amount'])
        data['status'] = status
        if self._next_handler:
            return super().handle(data)
        else:
            return data