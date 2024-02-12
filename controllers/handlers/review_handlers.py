import os
import sys
import re
from datetime import datetime
from typing import Any, Dict, Optional

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from models.models import MovieRate, TheaterRate, Comment
from controllers.handlers.abstract_handler import AbstractHandler
from utils.exceptions import UnvalidRate

class SubmitMovieRate(AbstractHandler):
    def handle(self, data: dict) -> dict | None:
        data['rate'] = int(data['rate'])
        data['movie_id'] = int(data['movie_id'])
        mrate = MovieRate.fetch_obj(where=f"{MovieRate.movie_id}={data['movie_id']} AND {MovieRate.user_id} = {data['user'].id}")
        if data['rate'] > 5 or data['rate'] < 1:
            raise UnvalidRate
        if mrate:
            mrate = mrate[0]
            mrate.update({MovieRate.rate: data['rate']})
        else:
            mrate = MovieRate(data['user'].id, data['movie_id'], data['rate'])
            mrate.insert()
        if self._next_handler:
            return super().handle(data)
        else:
            return data
        
class SubmitTheaterRate(AbstractHandler):
    def handle(self, data: dict) -> dict | None:
        data['rate'] = int(data['rate'])
        data['theater_id'] = int(data['theater_id'])
        trate = TheaterRate.fetch_obj(where=f"{TheaterRate.theater_id}={data['theater_id']} AND {TheaterRate.user_id} = {data['user'].id}")
        if data['rate'] > 5 or data['rate'] < 1:
            raise UnvalidRate
        if trate:
            trate = trate[0]
            trate.update({TheaterRate.rate: data['rate']})
        else:
            mrate = TheaterRate(data['user'].id, data['theater_id'], data['rate'])
            mrate.insert()
        if self._next_handler:
            return super().handle(data)
        else:
            return data
        
class WriteComment(AbstractHandler):
    def handle(self, data: dict) -> dict | None:
        data['movie_id'] = int(data['movie_id'])
        user = data['user']
        if 'parent_id' not in data:
            data['parent_id'] = None
        else:
            data['parent_id'] = int(data['parent_id'])
        if data['parent_id'] == 0:
            data['parent_id'] = None
        comm = Comment.create_new(user.id, data['movie_id'], data['parent_id'], data['text'])
        print(comm.info())
        data['comment'] = comm
        if self._next_handler:
            return super().handle(data)
        else:
            return data