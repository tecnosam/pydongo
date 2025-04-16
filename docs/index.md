# Pydongo

**Pydongo** is a lightweight and expressive ORM for **MongoDB** powered by **Pydantic**.

It brings structure and type safety to your unstructured NoSQL world — giving you clean, Pythonic control over your MongoDB documents.

---

## 🚀 Why Use Pydongo?

- ✅ **Pydantic-first**: Write your models as `BaseModel` classes — just like you're used to
- 🔄 **Sync + Async** support via `pymongo` and `motor`
- 🧠 **Elegant Query DSL**: Express Mongo filters using `==`, `>`, `&`, `|` and more
- 🧪 **Built for Testing**: In-memory mock driver makes unit testing easy
- 🧰 **No boilerplate**: Automatically connects models to collections
- 📦 **Tiny but powerful**: Focused API, zero clutter

---

## 🧱 Example

```python
from pydantic import BaseModel
from pydongo import as_document, as_collection
from pydongo.drivers.sync_mongo import DefaultMongoDBDriver

class User(BaseModel):
    name: str
    age: int
    collection_name = "users"

driver = DefaultMongoDBDriver("mongodb://localhost:27017", "mydb")
driver.connect()

# Insert a document
doc = as_document(User(name="Alice", age=30), driver)
doc.save()

# Query with expressive DSL
collection = as_collection(User, driver)
results = collection.find(collection.age > 25).all()

for user in results:
    print(user.name, user.age)

driver.close()
```

---

## 📚 Learn More

- [Installation](installation.md)
- [Quickstart](quickstart.md)

---

## 💬 Get Involved

Contributions welcome!  
Check out the [contributing guide](https://github.com/samuelabolo/pydongo/blob/main/CONTRIBUTING.md) or open an issue on GitHub.

---

## 🧾 License

Pydongo is open source under the [MIT License](https://github.com/samuelabolo/pydongo/blob/main/LICENSE).
