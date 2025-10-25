import asyncio
import uuid
from typing import Union

from pydantic import BaseModel
from pydantic import Field

from pydongo import as_collection
from pydongo import as_document
from pydongo.drivers.async_mongo import PyMongoAsyncDriver

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

driver = PyMongoAsyncDriver("mongodb://localhost:27017", "social_app_async")


# === OPERATIONS ===


async def create_user(username: str, email: str, bio: str = "") -> User:
    user = User(username=username, email=email, bio=bio)
    doc = as_document(user, driver)
    await doc.save()
    return doc


async def make_post(username: str, content: str) -> Union[Post, None]:
    users = as_collection(User, driver)
    user_doc = await users.find_one(users.username == username)
    if not user_doc:
        return None

    post = Post(content=content)
    user_doc.posts.append(post)
    await user_doc.save()
    return post


async def like_post(username: str, post_id: str) -> bool:
    users = as_collection(User, driver)
    user_doc = await users.find_one(users.username == username)
    if not user_doc:
        return False

    for post in user_doc.posts:
        if post.id == post_id:
            post.likes += 1
            await user_doc.save()
            return True
    return False


async def get_all_posts(username: Union[str, None] = None) -> list[Post]:
    users = as_collection(User, driver)

    if username:
        user_doc = await users.find_one(users.username == username)
        return user_doc.posts if user_doc else []

    all_users = await users.find().all()
    all_posts = []
    for user in all_users:
        all_posts.extend(user.posts)
    return all_posts


# === DEMO FLOW ===


async def main() -> None:
    await driver.connect()

    # Create a user
    sam = await create_user("samdev", "sam@example.com", bio="Async all the way!")
    print("Created user:", sam.username)

    # Make a post
    post = await make_post("samdev", "Async + Mongo + Pydongo 😎")
    print("Posted:", post.content)

    # Like the post
    liked = await like_post("samdev", post.id)
    print("Liked post:", "✅" if liked else "❌")

    # Get all posts
    print("All posts:")
    for p in await get_all_posts():
        print("-", p.content, f"({p.likes} likes)")

    await driver.close()


if __name__ == "__main__":
    asyncio.run(main())
