## Quickstart

This guide walks you through creating and interacting with MongoDB documents using `Pydongo` — covering both Document and Collection workers.

---

### 🧱 Step 1: Define a Pydantic Model

```python
from pydantic import BaseModel

class User(BaseModel):
    name: str
    age: int

```

---

### 🔌 Step 2: Connect to MongoDB

```python
from pydongo.drivers.sync_mongo import DefaultMongoDBDriver

driver = DefaultMongoDBDriver("mongodb://localhost:27017", "mydb")
driver.connect()
```

---

### 📄 Step 3: Use the Document Worker (create, update, delete)

```python
from pydongo import as_document

# Create and save a new user
user = User(name="Alice", age=30)
doc = as_document(user, driver)
doc.save()

# Update user and save again
doc.age = 31
doc.save()

# Delete user
doc.delete()
```

---

### 📦 Step 4: Use the Collection Worker (query, read)

```python
from pydongo import as_collection

collection = as_collection(User, driver)

# Insert multiple users
users = [
    User(name="Bob", age=25),
    User(name="Charlie", age=35),
    User(name="Diana", age=40),
]
for user in users:
    as_document(user, driver).save()

# Query users older than 30
results = collection.find(collection.age > 30).all()
for result in results:
    print(f"{result.name} - {result.age}")

# Find one
bob = collection.find_one(collection.name == "Bob")
if bob:
    print("Found Bob:", bob.age)

# Delete via result
if bob:
    bob.delete()
```

---

### ✅ Step 5: Close the driver

```python
driver.close()
```

---

This covers **basic CRUD** using:
- `as_document()` for direct document operations
- `as_collection()` for querying multiple documents

Now you're ready to model complex documents, build queries, and wrap async flows too.
