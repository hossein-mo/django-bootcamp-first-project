from getpass import getpass
from .utils import create_request, clear_screen, Response, Page
from tcp_client import TCPClient


class Movie:
    def __init__(self, title, year, id=None, comments=[]):
        self.title = title
        self.year = year
        self.id = id
        self.comments = comments


class Comment:
    def __init__(self, text, user_name):
        self.text = text
        self.user_name = user_name


class MovieListPage(Page):
    movie_list = []

    def display(self):
        clear_screen()
        client = TCPClient()
        request = create_request(type="movie", subtype="list")
        client.send(request)
        response = client.recive()
        response = Response(**response)
        if response.status:
            movie_list = response.data["movies"]
            for movie in movie_list:
                print(f'{movie["id"]}. {movie["title"]} ({movie["year"]})')
            print(f"\nEnter a movie ID to see details, or press Zero to go back...")
            self.handle_input(input())
        else:
            print("Connection Error! Try again...")
            input("Press any key to go back... ")
            self.handle_input("0")

    def handle_input(self, user_input):
        if user_input == "0":
            self.app.navigate_back()
        else:
            self.app.navigate_to_page(MovieDetailPage(self.app, user_input))


class MovieDetailPage(Page):
    def __init__(self, app, movie_id):
        super().__init__(app)
        self.movie_id = movie_id

    def display(self):
        clear_screen()
        client = TCPClient()
        request = create_request(
            type="movie", subtype="detail", data={"movie_id": self.movie_id}
        )
        client.send(request)
        response = client.recive()
        if response is not None:
            response = Response(**response)
            movie = Movie(**response.data)
            print(f"Title: {movie.title}\nYear: {movie.year}\nComments:")
            for comment in movie.comments:
                print(f' - {comment["user_name"]}: {comment["text"]}')
            print("\n1. Add comment\n0. Go back")
            self.handle_input(input())
        else:
            print("Connection Error! Try again...")
            input("Press any key to go back... ")
            self.display()

    def handle_input(self, user_input):
        if user_input == "1":
            self.app.navigate_to_page(AddCommentPage(self.app, self.movie_id))
        else:
            self.app.navigate_back()


class AddCommentPage(Page):
    def __init__(self, app, movie_id):
        super().__init__(app)
        self.movie_id = movie_id

    def display(self):
        clear_screen()
        comment_text = input("Enter your comment:\n")
        user_name = input("Enter your name: ")
        # Here you would send the comment to the server
        client = TCPClient()
        request = create_request(
            type="movie",
            subtype="add_comment",
            data={
                "movie_id": self.movie_id,
                "comment": {"text": comment_text, "user_name": user_name},
            },
        )
        client.send(request)
        response = client.recive()
        if response is not None:
            response = Response(**response)
            print(response.message)
        else:
            print("Failed to add comment. Try again...")
        input("Press any key to go back... ")
        self.app.navigate_back()
