# Pydongo

[![PyPI Version](https://img.shields.io/pypi/v/pydongo.svg)](https://pypi.org/project/pydongo/) [![License](https://img.shields.io/pypi/l/pydongo.svg)](https://github.com/tecnosam/pydongo/blob/main/LICENSE) [![Python Versions](https://img.shields.io/pypi/pyversions/pydongo.svg)](https://pypi.org/project/pydongo/)

**Pydongo** is a lightweight, expressive, and testable ORM for MongoDB, built on top of Pydantic. It supports both synchronous (PyMongo) and asynchronous (Motor) MongoDB drivers, allowing you to work with MongoDB in a flexible and intuitive way. Pydongo provides an elegant query expression system (inspired by Django ORM and SQLAlchemy) and an optional document interface for convenient `.save()` and `.delete()` operations on your Pydantic models.

## Installation

You can install Pydongo from PyPI using **pip** or **Poetry**:

**Using pip:**

```bash
pip install pydongo
```

**Using Poetry:**

```bash
poetry add pydongo
```

Pydongo requires Python 3.9+ and will automatically install dependencies like **pymongo** (for sync use) and **motor** (for async use).

## Quickstart

Define your data schema as a Pydantic model, then use Pydongo's driver and query utilities to interact with MongoDB. Below are examples for both synchronous and asynchronous usage:

### Synchronous Example (PyMongo)

```python
from pydantic import BaseModel
from pydongo import DefaultMongoDBDriver, as_collection, as_document

# 1. Create a MongoDB driver (synchronous)
driver = DefaultMongoDBDriver("mongodb://localhost:27017", "mydatabase")
driver.connect()  # Establish connection to MongoDB

# 2. Define a Pydantic model for your data
class User(BaseModel):
    name: str
    age: int

# 3. Insert a new document using the document interface
new_user = User(name="Alice", age=30)
user_doc = as_document(new_user, driver)   # wrap the Pydantic object as a document
result = user_doc.save()                   # save to MongoDB (inserts a new document)
print("Inserted ID:", result.get("inserted_id"))

# 4. Query documents using the expressive DSL
collection = as_collection(User, driver)
# Build a query: e.g., find users named Alice who are over 20
query = (collection.name == "Alice") & (collection.age > 20)
for user in collection.find(query).all():  # retrieve all matching documents
    # Each item is a DocumentWorker wrapping a User model
    print(user.name, user.age)

# 5. Find a single document and update/delete
found = collection.find_one(collection.name == "Alice")
if found:
    print("Found:", found.name)
    found.age = 31       # modify the Pydantic model
    found.save()         # update the existing document in MongoDB
    found.delete()       # or delete the document from MongoDB

driver.close()  # Close the connection when done

```

### Asynchronous Example (Motor)

```python
import asyncio
from pydantic import BaseModel
from pydongo import DefaultAsyncMongoDBDriver, as_collection, as_document

# Define a Pydantic model (same as before)
class Product(BaseModel):
    name: str
    price: float

async def main():
    # 1. Create a MongoDB driver (asynchronous)
    driver = DefaultAsyncMongoDBDriver("mongodb://localhost:27017", "mydatabase")
    await driver.connect()  # Establish async connection

    # 2. Insert a new document using the document interface
    new_product = Product(name="Laptop", price=999.99)
    product_doc = as_document(new_product, driver)  # wraps the Product instance
    await product_doc.save()                        # asynchronously insert into MongoDB

    # 3. Query documents using the DSL (async)
    collection = as_collection(Product, driver)
    # e.g., find products with price less than 1000
    query = collection.price < 1000
    results = await collection.find(query).all()    # asynchronous retrieval
    for product in results:
        # Each result is an AsyncDocumentWorker wrapping a Product model
        print(product.name, product.price)

    # 4. Cleanup
    await driver.close()  # Close the connection

# Run the async main function
asyncio.run(main())

```

## Key Features

- **Expressive Query DSL**: Build MongoDB queries using a Pythonic syntax. Compare fields with operators (==, !=, <, >=, etc.) and combine conditions with & (AND), | (OR), or ~ (NOT) for complex queries. This expression system will compile to proper MongoDB filters behind the scenes, making queries more readable and maintainable (similar to Django QuerySets or SQLAlchemy filter expressions).
- **Document Interface**: In addition to query builder methods, Pydongo lets you treat your Pydantic model instances as active record documents. By wrapping a model with as_document(), you get an object that supports .save() to insert/update itself in the database and .delete() to remove itself. This provides an ORM-like experience where each object knows how to persist itself.
- **Sync and Async Support**: Use Pydongo in both synchronous and asynchronous applications. It offers a DefaultMongoDBDriver for PyMongo (sync) and a DefaultAsyncMongoDBDriver for Motor (async). Both drivers implement a common interface, so you can write code that is agnostic to the driver type. Async support means you can integrate easily with frameworks like FastAPI, while sync support covers traditional scripts and applications.
- **Built on Pydantic**: Pydongo models are Pydantic models, so you get all the benefits of Pydantic's validation, parsing, and serialization. Data going into and coming out of MongoDB will match your schema, with Pydantic ensuring types and constraints. This reduces errors and keeps your data model consistent.
- **Testability with Mock Driver**: Pydongo is designed to be easily testable. It includes an in-memory MockMongoDBDriver (and an async variant) that you can use for unit tests. This means you can run tests without needing a real MongoDB instance, by swapping in the mock driver to simulate database operations. Because the ORM is decoupled from the actual database via the driver interface, you can inject a fake or real driver as needed.

## Documentation

For more detailed usage, advanced features, and API reference, visit the [Pydongo Documentation](https://tecnosam.github.io/pydongo/). The documentation covers additional examples, configuration options, and deeper dives into the query syntax and driver interfaces.

## Contributing

Contributions are welcome! See CONTRIBUTING.md or open an issue or PR.

## License

This project is licensed under the **MIT License**. See the [LICENSE](https://github.com/tecnosam/pydongo/blob/main/LICENSE) file for details.
