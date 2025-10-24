# Working with Documents

The `DocumentWorker` class in Pydongo provides a convenient interface to perform CRUD operations on a single document, while preserving your original Pydantic model structure.

This is one of the core patterns of Pydongo — it enables persistence **without requiring your models to inherit from any base class**.

---

## 🧱 How It Works

To work with a document, you wrap a Pydantic model using `as_document()`:

```python
from pydantic import BaseModel
from pydongo import as_document
from pydongo.drivers.sync_mongo import PyMongoDriver

class User(BaseModel):
    name: str
    age: int

driver = PyMongoDriver("mongodb://localhost:27017", "mydb")
driver.connect()

user = User(name="Alice", age=30)
doc = as_document(user, driver)

doc.save()  # inserts into the 'user' collection
```

By default, Pydongo will infer the collection name from the model class name (`User` → `"user"`).

---

## ✅ Supported Operations

### `.save()`

- If the document does not exist in the database, it will be **inserted**
- If it already exists (i.e. `objectId` is set), it will be **updated**

```python
doc.pydantic_object.age = 31
doc.save()  # Updates the document
```

### `.delete()`

- Deletes the document from the database based on `objectId`

```python
doc.delete()
```

---


## 🔁 Accessing Data from the Document

Every `DocumentWorker` exposes the original Pydantic model via `.pydantic_object`:

```python
assert isinstance(doc.pydantic_object, User)
print(doc.pydantic_object.name)
```

This is useful when you need to:
- re-serialize the model (`.model_dump()`)
- re-validate or transform the data
- pass the object to other parts of your app

---

### 🧾 Field Access Shortcut

You can also directly access **read-only fields** of the underlying model:

```python
print(doc.name, doc.age)
assert isinstance(doc.name, str)
```

This is purely for convenience and **read-only access**.  
To mutate data, modify `doc.pydantic_object` directly:

```python
doc.pydantic_object.age += 1
doc.save()
```

---

## ✅ Summary

| Method | Description |
|--------|-------------|
| `.save()` | Insert or update the document |
| `.delete()` | Remove from database |
| `.pydantic_object` | Access the underlying Pydantic model |

The `DocumentWorker` is a clean abstraction for managing the lifecycle of a single document — designed for devs who prefer **explicit control and clean models**.
---

## 🌐 Using AsyncDocumentWorker

Pydongo also supports asynchronous workflows using `AsyncDocumentWorker`, which behaves similarly to the sync version but with `async` methods.

You don’t need to construct it manually — Pydongo will automatically return an `AsyncDocumentWorker` when used with an async driver:

```python
from pydantic import BaseModel
from pydongo import as_document
from pydongo.drivers.async_mongo import PyMongoAsyncDriver

class User(BaseModel):
    name: str
    age: int

driver = PyMongoAsyncDriver("mongodb://localhost:27017", "mydb")
await driver.connect()

user = User(name="Bob", age=28)
doc = as_document(user, driver)

await doc.save()  # Insert
await doc.delete()  # Delete
```

### Key differences:
- Methods like `.save()` and `.delete()` are `async`
- Can be used inside `FastAPI`, `asyncio`, and other async frameworks
- You access `.pydantic_object` and read-only fields the same way as the sync version

```python
print(doc.name, doc.age)
doc.pydantic_object.age += 1
await doc.save()
```

---

### ✅ Summary (Async)

| Method | Description |
|--------|-------------|
| `await .save()` | Insert or update the document |
| `await .delete()` | Remove from database |
| `.pydantic_object` | Access the underlying Pydantic model |

The `AsyncDocumentWorker` is your go-to for async MongoDB workflows — with the same structure and ergonomics as the sync API.