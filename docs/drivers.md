# Drivers & Extensibility

Pydongo is built on a **pluggable driver interface**, allowing you to work with MongoDB in both synchronous and asynchronous contexts — or even create your own custom drivers (e.g., in-memory mocks, logging wrappers, or remote API-backed data stores).

---

## 🔌 Driver Design Philosophy

Drivers are thin layers responsible for executing actual MongoDB operations.
They expose a common interface so the higher-level Pydongo logic (documents, queries, filters) remains independent of the connection style.

You can choose between:

- ✅ `DefaultMongoDBDriver` (sync) — wraps PyMongo
- ✅ `DefaultAsyncMongoDBDriver` (async) — wraps Motor
- ✅ `MockMongoDBDriver` — in-memory fake for testing
- ✅ Or build your own

---

## 🧱 Abstract Base Classes

All drivers ultimately inherit from `AbstractMongoDBDriver`.

There are two concrete base interfaces:

### `AbstractSyncMongoDBDriver`

```python
class AbstractSyncMongoDBDriver:
    def connect(self) -> bool: ...
    def close(self) -> None: ...
    def insert_one(self, collection: str, document: dict) -> dict: ...
    def insert_many(self, collection: str, documents: list[dict]) -> dict: ...
    def find_one(self, collection: str, query: dict) -> dict | None: ...
    def find_many(self, collection: str, query: dict, sort_criteria: dict, offset: int, limit: int) -> Iterable[dict]: ...
    def update_one(self, collection: str, query: dict, update: dict, upsert: bool = False) -> dict: ...
    def delete_one(self, collection: str, query: dict) -> dict: ...
    def count(self, collection: str, query: dict) -> int: ...
    def exists(self, collection: str, query: dict) -> bool: ...
```

Each method mirrors a common MongoDB operation and accepts raw query/filter dictionaries.

### `AbstractAsyncMongoDBDriver`

Same as above, but all methods are `async def`.  
Ideal for async frameworks like **FastAPI** or **Quart**.

---

## ✅ Default Drivers

Pydongo includes two ready-to-use drivers:

### `DefaultMongoDBDriver` (Synchronous)

```python
from pydongo.drivers.sync_mongo import DefaultMongoDBDriver

driver = DefaultMongoDBDriver("mongodb://localhost:27017", "mydb")
driver.connect()
```

This driver uses **PyMongo** internally and is safe for CLI apps, scripts, and synchronous APIs.

---

### `DefaultAsyncMongoDBDriver` (Asynchronous)

```python
from pydongo.drivers.async_mongo import DefaultAsyncMongoDBDriver

driver = DefaultAsyncMongoDBDriver("mongodb://localhost:27017", "mydb")
await driver.connect()
```

This driver wraps **Motor** and is ideal for async web servers like **FastAPI**.

---

## 🧪 Mock Driver for Testing

Use `MockMongoDBDriver` or `MockAsyncMongoDBDriver` to test logic **without a real MongoDB instance**.

```python
from pydongo.drivers.mock import MockMongoDBDriver

driver = MockMongoDBDriver()
driver.connect()
```

Useful for unit testing business logic or running Pydongo in CI pipelines.

---

## 🧩 Building a Custom Driver

To plug in a custom database backend, subclass one of the abstract driver classes and implement the required methods.

Example:

```python
from pydongo.drivers.base import AbstractSyncMongoDBDriver

class LoggingDriver(AbstractSyncMongoDBDriver):
    def connect(self) -> bool:
        print("Connecting to dummy backend...")
        return True
    def insert_one(self, collection, doc):
        print(f"Inserting into {collection}:", doc)
        return {"inserted_id": "fake_id"}
    # implement other methods...
```

Then use with:
```python
driver = LoggingDriver()
driver.connect()
```

---

## 🧠 Notes on Design

- Drivers must **implement all abstract methods**
- Sync and Async drivers have **separate base classes**
- Use `driver.connect()` and `driver.close()` in your app lifecycle
- Avoid mixing sync and async in the same flow

---

## ✅ Summary

| Driver | Type | Backed By | Use Case |
|--------|------|-----------|----------|
| `DefaultMongoDBDriver` | Sync | PyMongo | Scripts, CLIs |
| `DefaultAsyncMongoDBDriver` | Async | Motor | FastAPI, async APIs |
| `MockMongoDBDriver` | Sync | In-memory | Unit tests |
| `MockAsyncMongoDBDriver` | Async | In-memory | Async unit tests |
| Custom driver | Sync/Async | Anything | Extend, log, simulate, swap DBs |

Pydongo keeps your application logic flexible and decoupled from the transport layer — exactly how clean MongoDB should feel.