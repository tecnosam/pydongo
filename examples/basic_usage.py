from typing import List, Optional
from uuid import UUID, uuid4
from datetime import datetime
from pydantic import BaseModel, Field


from pydongo import AsyncMongoDriver, as_collection, as_document


class Comment(BaseModel):

    comment_id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    text: str
    replying_to: Optional[UUID] = Field(default=None, help="ID of comment you're replying to")
    created_at: datetime = Field(default_factory=lambda: datetime.now())
    n_likes: int


class Post(BaseModel):

    post_id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    caption: str
    image_url: str

    n_likes: int = 0
    comments: List[Comment]
    created_at: datetime = Field(default_factory=lambda: datetime.now())


async def main():

    user_id = uuid4()
    post_id = uuid4()

    async with AsyncMongoDriver():

        PostCollection = as_collection(Post)
        post = await PostCollection.find_one(PostCollection.post_id == post_id)
        
        print("Check if post exists")
        print(await PostCollection.find(PostCollection.post_id == post_id).exists())

    driver = AsyncMongoDriver()

    PostCollection = as_collection(Post, driver=driver)

    print("Get the list of posts made by the user, sort in decending order of likes")
    posts = await PostCollection.find(PostCollection.user_id == user_id).sort(-PostCollection.n_likes).all()
    print(posts)

    print("More Complex querying")
    posts = await PostCollection.find((PostCollection.user_id == user_id) & (PostCollection.n_likes > 5))
    print(posts.all())

    print("Count Documents")
    print(await posts.count())

    print("Get all user's posts and paginate")
    paginated_posts = await PostCollection.find(PostCollection.user_id == user_id).paginate(page_size=10, page_number=1)
    print(next(paginated_posts))
    print("Get all user's posts and paginate manually")
    posts = await PostCollection.find(PostCollection.user_id == user_id).skip(20).limit(10).all()

    # Create a new Post
    print("Save a new document to the collection")
    post = Post(
        user_id=user_id,
        caption="Hello from Dubai!",
        image_url="http://image.com/image",
        comments=[]
    )
    await as_document(post, driver=driver).save()

    # Update the Post's like count
    print("Update a document in the collection")
    post.n_likes += 1
    await as_document(post, driver=driver).save()


    print("Delete the post document from the collection using the pydantic model")
    await as_document(post).delete()
