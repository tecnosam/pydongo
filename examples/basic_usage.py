import asyncio
from typing import List, Optional
from uuid import UUID, uuid4
from datetime import datetime, date
from pydantic import BaseModel, Field


from pydongo.drivers.sync_mongo import DefaultMongoDBDriver
from pydongo.drivers.async_mongo import AsyncDefaultMongoDBDriver
from pydongo.workers.document import as_document
from pydongo.workers.collection import as_collection


class User(BaseModel):
    name: str
    age: int = 18
    creation_date: date = Field(default_factory=date.today)


class Comment(BaseModel):
    comment_id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    text: str
    replying_to: Optional[UUID] = Field(
        default=None, help="ID of comment you're replying to"
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now())
    n_likes: int


class Post(BaseModel):
    post_id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    caption: str
    image_url: str

    n_likes: int = 0
    comments: List[Comment]
    comment: Comment
    created_at: datetime = Field(default_factory=lambda: datetime.now())


cs = "mongodb+srv://kopal:isaac1023@cluster0.tsyn9.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"


def test_sync():
    driver = DefaultMongoDBDriver(connection_string=cs, database_name="pydongo-test")

    # driver = MockMongoDBDriver(connection_string=cs, database_name="pydongo-test")

    driver.connect()
    p = as_collection(Post, driver=driver)

    u = as_document(User(name="Xy"), driver=driver)

    print(u.creation_date)

    print(u.save())

    for name, age in [("John", 18), ("Smith", 21), ("Sandy", 18)]:
        as_document(User(name=name, age=age), driver=driver).save()

    users = list(as_collection(User, driver=driver).find().all())
    print(list(users))


async def test_async():
    user_id = uuid4()
    post_id = uuid4()

    dbname = "pydongo-async-test"

    async with AsyncDefaultMongoDBDriver(
        connection_string=cs, database_name=dbname
    ) as driver:
        PostCollectionWorker = as_collection(Post, driver=driver)
        post = await PostCollectionWorker.afind_one(
            PostCollectionWorker.post_id == post_id
        )

        print("Check if post exists")
        print(
            await PostCollectionWorker.find(
                PostCollectionWorker.post_id == post_id
            ).exists()
        )

    driver = AsyncDefaultMongoDBDriver(connection_string=cs, database_name=dbname)
    await driver.connect()

    PostCollectionWorker = as_collection(Post, driver=driver)

    print("Get the list of posts made by the user, sort in decending order of likes")
    posts = await PostCollectionWorker.find(
        PostCollectionWorker.user_id == user_id
    ).all()
    print(posts)

    print("Sorting")
    posts = PostCollectionWorker.find().sort(
        [PostCollectionWorker.created_at, -PostCollectionWorker.n_likes]
    )
    print(await posts.all())

    print("Count Documents")
    print(await posts.count())

    print("Get all user's posts and paginate")
    posts = (
        await PostCollectionWorker.find(PostCollectionWorker.user_id == user_id)
        .skip(20)
        .limit(10)
        .all()
    )

    # Create a new Post
    print("Save a new document to the collection")
    post = Post(
        user_id=user_id,
        caption="Hello from Dubai!",
        image_url="http://image.com/image",
        comments=[],
        comment=Comment(
            user_id=user_id,
            text="Hello",
            n_likes=0,
        ),
    )

    post_document = as_document(post, driver=driver)
    print(await post_document.save())

    print("objectID: ", post_document.objectId)

    # Update the Post's like count
    print("Update a document in the collection")
    post_document.pydantic_object.n_likes += 1
    print(await post_document.save())

    print("Delete the post document from the collection using the pydantic model")
    await post_document.delete()


if __name__ == "__main__":
    asyncio.run(test_async())

    # test_sync()
