import asyncio
import uuid
from typing import Optional, List

from pydantic import BaseModel, Field

from pydongo import as_collection, as_document
from pydongo.drivers.async_mongo import PyMongoAsyncDriver


# =========================
# Models
# =========================

class Post(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content: str
    likes: int = 0


class User(BaseModel):
    username: str
    email: str
    bio: Optional[str] = ""
    followers: int = 0

    posts: List[Post] = Field(default_factory=list)
    pinned_post: Optional[Post] = None


# =========================
# Database setup
# =========================

driver = PyMongoAsyncDriver(
    connection_string="mongodb://localhost:27017",
    database_name="social_app_async",
)

users = as_collection(User, driver)


# =========================
# Async CRUD operations
# =========================

async def create_user(username: str, email: str, bio: str = "") -> User:
    user = User(
        username=username,
        email=email,
        bio=bio,
        pinned_post=Post(content="Welcome to my profile"),
    )
    doc = as_document(user, driver)
    await doc.save()
    return doc


async def make_post(username: str, content: str) -> Optional[Post]:
    user = await users.afind_one(users.username == username)
    if not user:
        return None

    post = Post(content=content)
    user.posts.append(post)
    await user.save()
    return post


async def like_post(username: str, post_id: str) -> bool:
    user = await users.afind_one(users.username == username)
    if not user:
        return False

    for post in user.posts:
        if post.id == post_id:
            post.likes += 1
            await user.save()
            return True

    return False


# =========================
# Mutation-based updates
# =========================

async def reward_active_users(bonus: int) -> None:
    """
    Perform mutation-based updates on users with fewer than 50 followers.
    Demonstrates:
      - numeric mutation ($inc)
      - nested field mutation
      - array mutation ($addToSet)
    """
    query = users.find(users.followers < 50)

    # Numeric mutation
    query.followers += bonus

    # Nested field mutation
    if query.pinned_post is not None:
        query.pinned_post.likes += bonus

    # Array mutation
    query.posts.add_to_set(Post(content="Thanks for being active!"))

    result = await query.amutate()

    print("Mutation result:", result)
    print("Applied mutations:", query.get_mutations())


# =========================
# Demo flow
# =========================

async def main() -> None:
    await driver.connect()

    # Create users
    alice = await create_user("alice", "alice@example.com", bio="Loves async")
    bob = await create_user("bob", "bob@example.com", bio="Async explorer")

    # Make posts
    await make_post("alice", "Hello Async World!")
    await make_post("bob", "Python + Mongo + Async Rocks!")

    # Like posts
    for user in [alice, bob]:
        for post in await get_all_posts(user.username):
            await like_post(user.username, post.id)

    # List users before mutation
    print("\nUsers before mutation:")
    for user in await users.find().all():
        print(f"- {user.username}: {user.followers} followers, pinned_post likes: {user.pinned_post.likes}")

    # Run mutation-based update
    await reward_active_users(bonus=5)

    # List users after mutation
    print("\nUsers after mutation:")
    for user in await users.find().all():
        print(f"- {user.username}: {user.followers} followers, pinned_post likes: {user.pinned_post.likes}")
        print(f"  Posts: {[p.content for p in user.posts]}")

    await driver.close()


async def get_all_posts(username: Optional[str] = None) -> List[Post]:
    if username:
        user = await users.afind_one(users.username == username)
        return user.posts if user else []

    all_posts: list[Post] = []
    for user in await users.find().all():
        all_posts.extend(user.posts)
    return all_posts


if __name__ == "__main__":
    asyncio.run(main())
