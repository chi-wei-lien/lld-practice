import abc
from typing import List, Optional
import threading

"""
assumptions:
- username is unique
- cannot comment on commemnt
- upvote will increment reputation by 1
- downvote will decrement repuation by 1
"""


class User:
    def __init__(self, username: str):
        self.username = username
        self.reputation = 0


class Tag:
    def __init__(self, tag_str):
        self.tag_str = tag_str


class Comment:
    def __init__(self, comment_str: str, author: User):
        self.comment_str = comment_str
        self.author = author

    def render(self, indent: int):
        print("\t" * indent, end="")
        print(f"'{self.comment_str}' by {self.author.username}")


class Post:
    def __init__(self, author: User):
        self.author = author
        self.up_vote = 0
        self.down_vote = 0
        self.up_vote_users = set()
        self.down_vote_users = set()
        self.comments = []

    def vote_up(self, user: User):
        if user.username in self.down_vote_users:
            raise Exception("User cannot up vote because they have already down vote")
        self.up_vote_users.add(user.username)
        self.author.reputation += 1
        self.up_vote += 1

    def vote_down(self, user: User):
        if user.username in self.up_vote_users:
            raise Exception("User cannot down vote because they have already up vote")
        self.down_vote_users.add(user.username)
        self.author.reputation -= 1
        self.down_vote += 1

    def comment(self, comment: Comment):
        self.comments.append(comment)

    @abc.abstractmethod
    def render(self):
        pass


class Answer(Post):
    def __init__(self, author: User, answer_str: str):
        super().__init__(author)
        self.answer_str = answer_str

    def render(self, indent: int):
        print("\t" * indent, end="")
        print(
            f"[answer] '{self.answer_str}' by {self.author.username} | up: {self.up_vote}, down: {self.down_vote}"
        )
        for comment in self.comments:
            comment.render(indent=indent)


class Question(Post):
    def __init__(self, title: str, desc: str, author: User, tags: List[Tag]):
        super().__init__(author)
        self.tags = set(tags)
        self.title = title
        self.desc = desc
        self.answers = set()

    def add_answer(self, answer: Answer):
        self.answers.add(answer)

    def render(self):
        print(
            f"[post] '{self.desc}' by {self.author.username} | up: {self.up_vote}, down: {self.down_vote}"
        )
        print(f"tags: {', '.join([t.tag_str for t in self.tags])}")
        for comment in self.comments:
            comment.render(indent=0)
        for answer in self.answers:
            answer.render(indent=1)


class StackOverflow:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        raise RuntimeError("please use initialize method")

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance.initialize()
        return cls._instance

    def initialize(self):
        self.users = []
        self.str_to_tag = {}
        self.questions = []

    def register(self, username: str):
        user = User(username)
        self.users.append(user)
        return user

    def create_question(self, user: User, title: str, desc: str, tag_strs: List[str]):
        tag_list = []
        for tag_str in tag_strs:
            if tag_str not in self.str_to_tag:
                tag = Tag(tag_str)
                self.str_to_tag[tag_str] = tag
            else:
                tag = self.str_to_tag[tag_str]
            tag_list.append(tag)

        new_question = Question(title, desc, user, tag_list)
        self.questions.append(new_question)
        return new_question

    def create_answer(self, question: Question, user: User, answer_str: str):
        answer = Answer(user, answer_str)
        question.add_answer(answer)
        return answer

    def create_comment(self, post: Post, comment_str: str, user: User):
        comment = Comment(comment_str, user)
        post.comment(comment)
        return comment

    def vote_up(self, post: Post, user: User):
        post.vote_up(user)

    def vote_down(self, post: Post, user: User):
        post.vote_down(user)

    def search_question(
        self,
        keyword: Optional[str],
        tag_strs: Optional[List[str]],
        user: Optional[User],
    ):
        result = []
        for question in self.questions:
            select = True
            if keyword:
                if keyword not in question.title:
                    select = False
            if not select:
                continue
            if tag_strs:
                for tag_str in tag_strs:
                    found_tag = False
                    for tag in question.tags:
                        if tag.tag_str == tag_str:
                            found_tag = True
                    if not found_tag:
                        select = False
                        break
            if not select:
                continue
            if user:
                if question.author != user:
                    select = False
            if select:
                result.append(question)
        return result

    def render(self):
        for question in self.questions:
            question.render()


if __name__ == "__main__":
    stack_overflow = StackOverflow.get_instance()
    userA = stack_overflow.register("userA")
    userB = stack_overflow.register("userB")
    userC = stack_overflow.register("userC")
    question1 = stack_overflow.create_question(
        userA,
        "why use python?",
        "heard python is good is it?",
        ["beginner", "python", "coding"],
    )
    answer1 = stack_overflow.create_answer(
        question1, userB, "becuase it is a good language"
    )
    comment1 = stack_overflow.create_comment(
        question1, "i think this is a good question", userC
    )
    comment2 = stack_overflow.create_comment(question1, "i don't think it is", userB)
    comment2 = stack_overflow.create_comment(
        answer1, "i think this is a good answer", userB
    )
    stack_overflow.vote_down(question1, userA)
    stack_overflow.vote_down(question1, userB)
    stack_overflow.vote_up(question1, userC)
    stack_overflow.vote_down(answer1, userC)

    stack_overflow.render()

    result = stack_overflow.search_question(
        keyword="use python", tag_strs=["beginner"], user=userA
    )

    print("search result:")
    for question in result:
        print(question.title)

    for user in stack_overflow.users:
        print(f"{user.username}, rep: {user.reputation}")
