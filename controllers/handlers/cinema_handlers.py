from datetime import datetime
from models.models import Movie, Theater, Showtime
from controllers.handlers.abstract_handler import AbstractHandler
from utils.exceptions import TheaterNotExist, MovieNotExist, ShowTimeError


class CheckMovieInfo(AbstractHandler):
    """
    Handler for checking if requested movie info are correct or not.

    """

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
    """
    Handler for adding movie to cimena

    """

    def handle(self, data: dict) -> dict | None:
        movie = Movie.create_new(**data)
        data = movie.info()
        if self._next_handler:
            return super().handle(data)
        else:
            return data


class CheckTheaterInfo(AbstractHandler):
    """
    Handler for check if requested theater info are correct or not

    """

    def handle(self, data: dict) -> dict | None:
        selected_keys = ["t_name", "capacity"]
        data = {key: data[key] for key in selected_keys if key in data}
        data["capacity"] = int(data["capacity"])
        if self._next_handler:
            return super().handle(data)
        else:
            return data


class AddTheater(AbstractHandler):
    """
    Handler for adding theater to cinema

    """

    def handle(self, data: dict) -> dict | None:
        theater = Theater.create_new(**data)
        data = theater.info()
        if self._next_handler:
            return super().handle(data)
        else:
            return data


class CheckTheater(AbstractHandler):
    """
    Handler for checking if requested theater exists or not

    """

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
    """
    Handler for checking if requester movie exists or not

    """

    def handle(self, data: dict) -> dict | None:
        movie_id = int(data["movie_id"])
        movie = Movie.fetch_obj(where=f'{Movie.id}="{movie_id}"')
        if not movie:
            raise MovieNotExist
        data["movie"] = movie[0]
        data["movie_id"] = movie_id
        if self._next_handler:
            return super().handle(data)
        else:
            return data


class CheckShowTime(AbstractHandler):
    """
    Handler for checking if a show exists, if its time overlaps with other shows and if show duration is enough for the movie

    """

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
        movie_duration = data["movie"].duration
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
    """
    Handler for adding show to cinema time table

    """

    def handle(self, data: dict) -> dict | None:
        data["price"] = int(data["price"])
        show = Showtime.create_new(**data)
        movie = data["movie"]
        movie.update({Movie.screening_number: movie.screening_number + 1})
        movie.screening_number += 1
        data["movie"] = movie.info()
        data["show"] = show.info()
        if self._next_handler:
            return super().handle(data)
        else:
            return data
