from app.models.domain import Comment

class CommentRepository:
    def __init__(self) -> None:
        self._comments: dict[int, Comment] = {}
        self._counter: int = 1

    def create(self, body: str, author_name: str, post_id: int) -> Comment:
        comment = Comment(
            id=self._counter,
            body=body,
            author_name=author_name,
            post_id=post_id
        )

        self._comments[self._counter] = comment
        self._counter += 1

        return comment

    def get_by_post(self, post_id: int) -> list[Comment]:
        comments = [comment for comment in self._comments.values() if comment.post_id == post_id]
        return comments

    def delete(self, comment_id: int) -> bool:
        if comment_id in self._comments:
            del self._comments[comment_id]
            return True

        return False
