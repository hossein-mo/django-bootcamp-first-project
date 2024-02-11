import os
import sys
import re
from datetime import datetime
from typing import Any, Dict, Optional

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from models.models import Movie, Theater, Showtime
from controllers.handlers.abstract_handler import AbstractHandler
from utils.exceptions import TheaterNotExist, MovieNotExist, ShowTimeError


class CheckMovieInfo(AbstractHandler):
    def handle(self, data: dict) -> dict | None:
        selected_keys = ["m_name", "duration", "age_rating"]
        data = {key: data[key] for key in selected_keys if key in data}
        data["duration"] = int(data["duration"])
        data["age_rating"] = int(data["age_rating"])
        if self._next_handler:
            return super().handle(data)
        else:
            return data


class AddMovie(AbstractHandler):
    def handle(self, data: dict) -> dict | None:
        movie = Movie.create_new(**data)
        data = movie.info()
        if self._next_handler:
            return super().handle(data)
        else:
            return data


class CheckTheaterInfo(AbstractHandler):
    def handle(self, data: dict) -> dict | None:
        selected_keys = ["t_name", "capacity"]
        data = {key: data[key] for key in selected_keys if key in data}
        data["capacity"] = int(data["capacity"])
        if self._next_handler:
            return super().handle(data)
        else:
            return data


class AddTheater(AbstractHandler):
    def handle(self, data: dict) -> dict | None:
        theater = Theater.create_new(**data)
        data = theater.info()
        if self._next_handler:
            return super().handle(data)
        else:
            return data


class CheckTheater(AbstractHandler):
    def handle(self, data: dict) -> dict | None:
        theater_id = int(data["theater_id"])
        theater = Theater.fetch(where=f'{Theater.id}="{theater_id}"')
        if not theater:
            raise TheaterNotExist
        data["theater"] = theater[0]
        data["theater_id"] = theater_id
        if self._next_handler:
            return super().handle(data)
        else:
            return data


class CheckMovie(AbstractHandler):
    def handle(self, data: dict) -> dict | None:
        movie_id = int(data["movie_id"])
        movie = Movie.fetch(where=f'{Movie.id}="{movie_id}"')
        if not movie:
            raise MovieNotExist
        data["movie"] = movie[0]
        data["movie_id"] = movie_id
        if self._next_handler:
            return super().handle(data)
        else:
            return data


class CheckShowTime(AbstractHandler):
    def handle(self, data: dict) -> dict | None:
        start_date = datetime.strptime(data["start_date"], "%Y-%m-%d %H:%M:%S")
        end_date = datetime.strptime(data["end_date"], "%Y-%m-%d %H:%M:%S")
        theater_id = data["theater_id"]
        show = Showtime.fetch(
            where=f'{Showtime.theater_id}="{theater_id}"'
            + f' AND {Showtime.start_date} BETWEEN "{start_date}" AND "{end_date}"'
        )
        if show:
            show = show[0]
            raise ShowTimeError(
                message=f"Show overlaps with existing show, overlaping show id: {show['id']}"
            )
        show = Showtime.fetch(
            where=f'{Showtime.theater_id}="{theater_id}"'
            + f' AND {Showtime.end_date} BETWEEN "{start_date}" AND "{end_date}"'
        )
        if show:
            show = show[0]
            raise ShowTimeError(
                message=f"Show overlaps with existing show, overlaping show id: {show['id']}"
            )
        show_duration = (end_date - start_date).total_seconds() / 60
        movie_duration = data["movie"]["duration"]
        if show_duration < movie_duration:
            raise ShowTimeError(
                message=f"Show duration of {show_duration} minutes "
                + f"less than movie duration of {movie_duration} minutes"
            )
        data["start_date"] = start_date
        data["end_date"] = end_date
        if self._next_handler:
            return super().handle(data)
        else:
            return data


class AddShow(AbstractHandler):
    def handle(self, data: dict) -> dict | None:
        data['price'] = int(data['price'])
        show = Showtime.create_new(**data)
        data["show"] = show.info()
        if self._next_handler:
            return super().handle(data)
        else:
            return data
