# Indexing in Pydongo

Pydongo supports expressive and declarative indexing to help you build performant MongoDB queries effortlessly. You can register single-field or compound indexes using a fluent builder-style API, or define them directly from your model's fields.

---

## 🚀 Basic Usage

To define and register indexes for your model:

```python
collection = as_collection(User, driver)

# Defining a simple index on the field
collection.use_index(collection.email.to_index())

# Defining a unique index
index = collection.email.as_index().use_unique().build_index()
collection.use_index(index)
```

This creates a **unique index** on the `email` field.


---

## 🧱 Compound Indexes

You can also create compound indexes by passing a tuple of `IndexExpression`s:

```python
index1 = collection.name.as_index().use_sort_order(IndexSortOrder.ASCENDING).build_index()
index2 = collection.email.as_index().use_sort_order(IndexSortOrder.DESCENDING).build_index()

collection.use_index((index1, index2))
```

This defines a compound index on `(name ASC, email DESC)`.


---

## 🔍 Supported Index Types

- `ASCENDING` and `DESCENDING` (default if no type is set)
- `TEXT` (automatically inferred for string fields)
- `HASHED`
- `2d` (for legacy geospatial indexing)
- `2dsphere` (for modern geospatial indexing)

You can explicitly set index type:

```python
collection.bio.as_index().use_index_type(IndexType.TEXT).build_index()
```


---

## ⚙️ Index Options

Pydongo supports the following MongoDB index options:

| Option            | Method                      |
|-------------------|------------------------------|
| `unique`          | `.use_unique()`              |
| `sparse`          | `.use_sparse()`              |
| `ttl`             | `.use_ttl(seconds)`          |
| `collation`       | `.use_collation(locale, strength)` |
| `hidden`          | `.use_hidden()`              |
| `partial index`   | `.use_partial_expression()`  |
| `custom name`     | `.use_index_name("my_index")` |

**Example:**

```python
collection.email.as_index()
    .use_unique()
    .use_ttl(3600)
    .use_collation("en", CollationStrength.SECONDARY)
    .build_index()
```

Note: TTL is not supported for `TEXT` and `HASHED` indexes.


---

## 🪄 Automatic Index Type Inference

When you call `.as_index()` on a field:
- If the field is a `str`, it automatically uses `TEXT` index
- Otherwise defaults to `ASCENDING`

You can override the default by calling `.use_index_type()` explicitly.


---

## 🧪 Testing Indexes

To verify indexes are correctly registered, you can:

- Assert against `collection._indexes`
- Check the contents of `driver.indexes[collection_name]`

Example:
```python
assert len(collection._indexes) == 1
assert (index,) in driver.indexes[collection.collection_name]
```

---

## 🛠 Index Creation Timing

Indexes are lazily created when you call any terminal query method like:
- `.count()`
- `.exists()`
- `.all()`

This ensures indexes are only created if actually used.


---

## ✅ Summary

Pydongo gives you expressive control over MongoDB indexes with:
- A fluent API
- Full support for compound and special index types
- Integration into both sync and async query flows

Define them once, and they’ll be created just in time.

