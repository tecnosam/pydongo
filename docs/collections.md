# Working with Collections

The `CollectionWorker` and its response builders provide a powerful yet intuitive API to query, filter, and iterate over documents in a MongoDB collection — all while keeping your data model as a clean Pydantic class.

---

## 📥 Creating a Collection Interface

You don't interact directly with `CollectionWorker`. Instead, use the `as_collection()` helper:

```python
from pydongo import as_collection
from pydantic import BaseModel
from pydongo.drivers.sync_mongo import DefaultMongoDBDriver

class User(BaseModel):
    name: str
    age: int

driver = DefaultMongoDBDriver("mongodb://localhost:27017", "mydb")
driver.connect()

collection = as_collection(User, driver)
```

By default, the collection name is inferred from the model class (`User` → `"user"`).

---

## 🔍 Finding Documents

### `.find_one()` (Sync)

```python
user = collection.find_one(collection.name == "Alice")
if user:
    print(user.pydantic_object.name)
```

### `await afind_one()` (Async)

```python
user = await collection.afind_one(collection.age > 25)
if user:
    print(user.pydantic_object.age)
```

---

## 🔁 Fluent Query Builder (`.find()`)

For multiple documents and advanced queries, use `.find()` to build a query:

```python
results = collection.find(collection.age > 20).sort(collection.name).limit(5).all()

for user in results:
    print(user.name, user.age)
```

Async version:

```python
results = await collection.find(collection.age > 20).sort(-collection.age).limit(10).all()

for user in results:
    print(user.name, user.age)
```

---

## ✨ Other Query Builder Features

| Method | Description |
|--------|-------------|
| `.find(expr)` | Filter query |
| `.sort(field)` | Sort by one or more fields |
| `.limit(n)` | Limit results |
| `.skip(n)` | Offset results |
| `.all()` / `await .all()` | Fetch all documents |
| `.count()` / `await .count()` | Count matching documents |
| `.exists()` / `await .exists()` | Check if any document exists |

---

## 🧠 Notes

- All results returned from `.find()` and `.find_one()` are wrapped in `DocumentWorker` or `AsyncDocumentWorker`
- You can use `doc.pydantic_object` to access or mutate the model
- The query language supports `==`, `!=`, `>`, `>=`, `<`, `<=`, `&`, `|`, and `~`

---

## ✅ Example: Combining Filters

```python
query = (collection.age > 18) & (collection.name != "Bob")
results = collection.find(query).all()

for user in results:
    print(user.name)
```

Or async:

```python
query = (collection.age > 18) & (collection.name != "Bob")
results = await collection.find(query).all()

for user in results:
    print(user.name)
```

---

## ✅ Summary

- Use `as_collection()` to query a MongoDB collection
- Works for both sync and async workflows
- Returns `DocumentWorker`/`AsyncDocumentWorker` instances
- Supports fluent chaining and expressive filter logic

Pydongo gives you clean Mongo-style querying with the structure of Pydantic — no inheritance, no decorators, just Python.