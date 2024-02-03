import datetime
import mysql.connector
from typing import Union

from controllers.exceptions import *
from models.database import DatabaseConnection
from models.base_models import Column, BaseModel
from models.movie import Movie
from models.user import User

class Comment(BaseModel):
    name = "comment"
    id = Column("id", "INT UNSIGNED", primary_key=True, auto_increment=True)
    user_id = Column("user_id", "INT UNSIGNED", foreign_key=User.id.name, reference=User.name)
    movie_id = Column("movie_id", "INT UNSIGNED", foreign_key=Movie.id.name, reference=Movie.name)
    parent_id = Column("parent_id", "INT UNSIGNED", foreign_key=id.name, reference=name)
    text = Column("text", "TEXT")
    created_at = Column("created_at", "DATE")

    def __init__(self, user_id, movie_id, parent_id, text, created_at=datetime.datetime.now(), id: Union[int, None] = None):
        self.id = id
        self.user_id = user_id
        self.movie_id = movie_id
        self.parent_id = parent_id
        self.text = text
        self.created_at = created_at
        self.replies = []
    
    @staticmethod
    def comment(user_id, movie_id, parent_id, text) -> None:
        CommentRepo.insert_comment(Comment(None, user_id, movie_id, parent_id, text))

    @staticmethod
    def get_comments(movie_id) -> list['Comment']:
        result = []
        comments = CommentRepo.get_comments(movie_id)
        for i in range(len(comments)):
            if comments[i].parent_id == 0:
                result.append(comments[i])
            for j in range(i+1, len(comments)):
                if comments[j].parent_id == comments[i].id:
                    comments[i].replies.append(comments[j])
        return result


class CommentRepo:

    @staticmethod
    def insert_comment(comment: Comment):
        try:
            Comment.insert(comment)
        except mysql.connector.Error as err:
            raise InsertFailed("Some problem occurred while register your comment. Try again!")

    @staticmethod
    def get_comments(movie_id) -> list[Comment]:
        conn = DatabaseConnection().get_connection()
        cursor = conn.cursor()
        query = f'SELECT * FROM {Comment.name} WHERE {Comment.movie_id.name}={movie_id}'
        cursor.execute(query)
        rows = cursor.fetchall()
        comments = [Comment(row[0], row[1], row[2], row[3], row[4]) for row in rows]
        return comments
  