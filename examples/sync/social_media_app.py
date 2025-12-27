import uuid
from typing import Optional, List

from pydantic import BaseModel, Field

from pydongo import as_collection, as_document
from pydongo.drivers.sync_mongo import PyMongoDriver


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

driver = PyMongoDriver("mongodb://localhost:27017", "social_app")
driver.connect()

users = as_collection(User, driver)


# =========================
# CRUD-style operations
# =========================

def create_user(username: str, email: str, bio: str = "") -> User:
    """
    Create and persist a new user document.
    """
    user = User(
        username=username,
        email=email,
        bio=bio,
        pinned_post=Post(content="Welcome to my profile"),
    )

    doc = as_document(user, driver)
    doc.save()
    return doc


def make_post(username: str, content: str) -> Optional[Post]:
    """
    Append a post to a user's post list and persist.
    """
    user = users.find_one(users.username == username)
    if not user:
        return None

    post = Post(content=content)
    user.posts.append(post)
    user.save()

    return post


def like_post(username: str, post_id: str) -> bool:
    """
    Increment the like counter on a specific post.
    """
    user = users.find_one(users.username == username)
    if not user:
        return False

    for post in user.posts:
        if post.id == post_id:
            post.likes += 1
            user.save()
            return True

    return False


def get_all_users() -> List[User]:
    return users.find().all()


def get_all_posts(username: Optional[str] = None) -> List[Post]:
    """
    Retrieve posts for a single user or all users.
    """
    if username:
        user = users.find_one(users.username == username)
        return user.posts if user else []

    all_posts: list[Post] = []
    for user in users.find().all():
        all_posts.extend(user.posts)

    return all_posts


# =========================
# Mutation-based updates
# =========================

def reward_active_users(bonus: int) -> None:
    """
    Perform an atomic mutation on all users with fewer than 50 followers.

    Demonstrates:
    - numeric mutations
    - nested field mutations
    - array mutations
    """
    query = users.find(users.followers < 50)

    # Numeric mutation
    query.followers += bonus

    # Nested document mutation
    query.pinned_post.likes += bonus

    # Array mutation
    query.posts.add_to_set(Post(content="Thanks for being active!"))

    result = query.mutate()

    print("Mutation result:", result)
    print("Applied mutations:", query.get_mutations())


# =========================
# Demo flow
# =========================

if __name__ == "__main__":
    # Create user
    sam = create_user(
        username="samdev",
        email="sam@example.com",
        bio="Builder of things",
    )
    print("Created user:", sam.username)

    # Create post
    post = make_post("samdev", "Excited to launch Pydongo!")
    print("New post:", post.content)

    # Like post
    success = like_post("samdev", post.id)
    print("Post liked:", success)

    # List users
    print("\nUsers before mutation:")
    for user in get_all_users():
        print(f"- {user.username} ({user.followers} followers)")

    # Run mutation
    reward_active_users(bonus=10)

    # List users again
    print("\nUsers after mutation:")
    for user in get_all_users():
        print(f"- {user.username} ({user.followers} followers)")

    driver.close()
