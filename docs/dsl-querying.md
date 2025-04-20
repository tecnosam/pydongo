# Using the Query DSL

Pydongo's query engine is built on top of Python-native expressions, making MongoDB queries feel natural and type-safe using your Pydantic models.

This page covers how to use `FieldExpression` and `CollectionFilterExpression` to write expressive, composable queries — without writing raw MongoDB dictionaries.

---

## 📐 Field Expressions

Every field on your model becomes a `FieldExpression` in a collection:

```python
collection = as_collection(User, driver)
collection.age  # FieldExpression
```

This enables query expressions like:

```python
collection.age > 25
collection.name == "Alice"
collection.age <= 60
```

You can use these in `.find()` or `.find_one()`:

```python
collection.find(collection.age > 30)
collection.find_one((collection.age > 20) & (collection.name != "Bob"))
```

---

## 🔁 Logical Composition

All field expressions produce a `CollectionFilterExpression`, which can be composed:

| Operator | Description |
|----------|-------------|
| `&` | Logical AND |
| `|` | Logical OR |
| `~` | Logical NOT |

```python
expr = (collection.age > 18) & (collection.name != "Bob")
collection.find(expr)
```

---

## 📌 Array Field Expressions

Array fields get additional operators via `ArrayFieldExpression`.

```python
class User(BaseModel):
    name: str
    tags: List[str]

collection = as_collection(User, driver)
collection.tags.contains("admin")
collection.tags.excludes("guest")
collection.tags.matches(["admin", "moderator"])
collection.tags.size() > 2
```

Supported:
- `contains(value)` → `$in`
- `excludes(value)` → `$nin`
- `matches(list)` → `$all` or exact match
- `size() > 2` → `$expr: {$gt: [{$size: "$tags"}, 2]}`

---

## ⚙️ Nested Fields

You can access subfields using dot notation automatically:

```python
class Address(BaseModel):
    city: str

class User(BaseModel):
    name: str
    address: Address

collection = as_collection(User, driver)
collection.address.city == "Lagos"
```

This will generate:
```json
{"address.city": {"$eq": "Lagos"}}
```

---

## 📤 Serialization

All expressions can be turned into MongoDB queries via `.serialize()`:

```python
expr = (collection.age > 18) & (collection.name == "Alice")
query = expr.serialize()
# { "$and": [{"age": {"$gt": 18}}, {"name": {"$eq": "Alice"}}] }
```

---

## ✅ Summary

- Use Python syntax for building MongoDB queries
- Supports scalar fields, arrays, and nested structures
- Output is always a valid MongoDB filter object
- Integrates seamlessly with `collection.find()`, `find_one()`, and `.count()`

Pydongo’s DSL gives you clean, powerful Mongo filters — without ever writing a manual `$and`, `$gt`, or `$in`.