import datetime
from typing import List

from repositories.comment_repo import CommentRepository

class Comment:
    def __init__(self, id, user_id, movie_id, parent_id, text, created_at=datetime.datetime.now()):
        self.id = id
        self.user_id = user_id
        self.movie_id = movie_id
        self.parent_id = parent_id
        self.text = text
        self.created_at = created_at
        self.replies = []
    
    @staticmethod
    def comment(user_id, movie_id, parent_id, text) -> None:
        CommentRepository.insert_comment(Comment(None, user_id, movie_id, parent_id, text))

    @staticmethod
    def get_comments(movie_id) -> List['Comment']:
        result = []
        comments = CommentRepository.get_comments(movie_id)
        for i in range(len(comments)):
            if comments[i].parent_id == 0:
                result.append(comments[i])
            for j in range(i+1, len(comments)):
                if comments[j].parent_id == comments[i].id:
                    comments[i].replies.append(comments[j])
        return result
    
    # def build_comment_tree(parent_id, comments):
    #     tree = []
    #     for comment in comments:
    #         if comment.parent_id == parent_id:
    #             replies = Comment.build_comment_tree(comment.id , comments)
    #             if replies:
    #                 comment.replies = replies
    #             tree.append(comment)
    #     return tree

