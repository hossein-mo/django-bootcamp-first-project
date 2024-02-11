import os
import sys
import re
from datetime import date
from typing import Any, Dict, Optional

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from models.models import Movie
from controllers.handlers.abstract_handler import AbstractHandler

class CheckMovieInfo(AbstractHandler):
    def handle(self, data: dict) -> dict | None:
        selected_keys = ['m_name', 'duration', 'age_rating']
        data = {key: data[key] for key in selected_keys if key in data}
        data['duration'] = int(data['duration'])
        data['age_rating'] = int(data['age_rating'])
        if self._next_handler:
            return super().handle(data)
        else:
            return data

class AddMovie(AbstractHandler):
    def handle(self, data: Any) -> Any | None:
        movie = Movie.create_new(**data)
        data = movie.info()
        if self._next_handler:
            return super().handle(data)
        else:
            return data