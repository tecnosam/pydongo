import uuid
from typing import Union

from pydantic import BaseModel
from pydantic import Field

from pydongo import as_collection
from pydongo import as_document
from pydongo.drivers.sync_mongo import PyMongoDriver

# === MODELS ===


class Post(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content: str
    likes: int = 0


class User(BaseModel):
    username: str
    email: str
    bio: Union[str, None] = ""
    posts: list[Post] = []


# === DB SETUP ===

driver = PyMongoDriver("mongodb://localhost:27017", "social_app")
driver.connect()
users = as_collection(User, driver)


# === OPERATIONS ===


def create_user(username: str, email: str, bio: str = "") -> User:
    user = User(username=username, email=email, bio=bio)
    doc = as_document(user, driver)
    doc.save()
    return doc


def make_post(username: str, content: str) -> Union[Post, None]:
    user_doc = users.find_one(users.username == username)
    if not user_doc:
        return None

    post = Post(content=content)
    user_doc.posts.append(post)
    user_doc.save()
    return post


def like_post(username: str, post_id: str) -> bool:
    user_doc = users.find_one(users.username == username)
    if not user_doc:
        return False

    for post in user_doc.posts:
        if post.id == post_id:
            post.likes += 1
            user_doc.save()
            return True
    return False


def get_all_posts(username: Union[str, None] = None) -> list[Post]:
    if username:
        user_doc = users.find_one(users.username == username)
        return user_doc.posts if user_doc else []

    all_users = users.find().all()
    all_posts = []
    for user in all_users:
        all_posts.extend(user.posts)
    return all_posts


# === DEMO FLOW ===

if __name__ == "__main__":
    # Create a user
    sam = create_user("samdev", "sam@example.com", bio="Builder of things")
    print("Created user:", sam.username)

    # Make a post
    post = make_post("samdev", "Excited to launch Pydongo!")
    print("Posted:", post.content)

    # Like the post
    liked = like_post("samdev", post.id)
    print("Liked post:", liked)

    # Get all posts
    print("All posts:")
    for p in get_all_posts():
        print("-", p.content, f"({p.likes} likes)")

    driver.close()
