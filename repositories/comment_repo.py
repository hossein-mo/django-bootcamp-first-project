from typing import List

from models.comment import Comment

class CommentRepository:

    @staticmethod
    def insert_comment(comment: Comment):
        #try:
        # conn= ?
        # query = 'INSERT INTO Comment Values (%s, %s, %s, %s, %s)'
        # cursor = conn.cursor()
        # cursor.execute(query, (comment.user_id, comment.movie_id, comment.parent_id, comment.text, comment.created_at))
        # except mysql.connector.Error as err:
        #     raise InsertFailed("Some problem occured while register your comment. Try again!")
        pass

    @staticmethod
    def get_comments(movie_id) -> List[Comment]:
        # conn= ?
        # query = 'SELECT * FROM Comment WHERE movie_id=%s'
        # cursor = conn.cursor()
        # cursor.execute(query, (movie_id,))
        # rows = cursor.fetchall()
        # comments = [Comment(row[0], row[1], row[2], row[3], row[4]} for row in rows]
        # return comments
        pass