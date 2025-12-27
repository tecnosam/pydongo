# Pydongo Mutation System Guide

## Updates from Mutations

Pydongo's mutation system allows you to perform atomic MongoDB updates on large numbers of documents without loading them into memory.

Instead of fetching documents, modifying them in Python, and saving them one by one (which becomes slow and memory-intensive for thousands or millions of records), you can compose MongoDB update operations directly using familiar Python syntax.

This is the primary intended use case of the Mutation DSL.

## Core Idea

* **Write Python-like syntax -> Generate efficient MongoDB bulk/atomic updates**
* **No documents are loaded into memory when using collection-level mutations**

### Example

```python
# Efficient: updates 10,000+ documents in one MongoDB operation
query = users.find(users.followers < 50)
query.followers += 10
query.posts.add_to_set(Post(content="Thanks for being active!"))
query.mutate()               # Single updateMany() call
```

## How to Create and Apply Mutations

Mutations are collected automatically inside a context created when you call `.find()`.

### Recommended Bulk Update Pattern

```python
query = collection.find(collection.age > 30)

# These statements build mutations in the shared context
query.status = "active"                    # $set
query.score += 100                         # $inc
query.tags.add_to_set("vip")               # $addToSet
query.profile.views.setmax(1000)           # $max
query.bio.unset()                          # $unset

# Execute the bulk update (updateMany)
result = query.mutate()                    # or await query.amutate()
```

You can always inspect the generated update document:

```python
print(query.get_mutations())
# {
#   "$set": {"status": "active"},
#   "$inc": {"score": 100},
#   "$addToSet": {"tags": "vip"},
#   "$max": {"profile.views": 1000},
#   "$unset": {"bio": ""}
# }
```

### Important Warning: Shared Mutation Context

The mutation context is thread-local / event-loop-local and shared across all `.find()` calls in the same execution context.

#### Danger Example

```python
# DANGER - same context is reused!
q1 = users.find(users.country == "FR")
q1.followers += 5

q2 = users.find(users.country == "DE")     # ← same mutation context!
q2.followers += 10

q1.mutate()   # Will apply BOTH +5 and +10 to French users!
```

### Recommended Safe Patterns

**Pattern 1: Short-lived query builder**

```python
with users.find(users.age > 65) as elderly:
    elderly.status = "retired"
    elderly.pension += 200
    elderly.mutate()
```

**Pattern 2: Explicit reset**

```python
query = users.find(users.active == True)
query.last_seen = datetime.utcnow()
query.mutate()
MutationExpressionContext.clear()          # Reset for next query
```

> In most real applications, prefer short-lived query builders.

## Supported Mutation Operations

| Python Syntax               | MongoDB Operator | Example / Notes                |
| --------------------------- | ---------------- | ------------------------------ |
| field = value               | $set             | user.name = "Alice"            |
| field.unset()               | $unset           | Removes field completely       |
| numeric += n / numeric -= n | $inc             | followers += 10, balance -= 50 |
| numeric *= n                | $mul             | score *= 1.5                   |
| numeric /= n                | $mul (1/n)       | price /= 2                     |
| field.setmax(value)         | $max             | Keeps greater value            |
| field.setmin(value)         | $min             | Keeps smaller value            |
| array.push(value)           | $push            | Append value                   |
| array.add_to_set(value)     | $addToSet        | Add only if not present        |
| array.pull(value)           | $pull            | Remove matching values         |
| array.popleft()             | $pop: 1          | Remove first element           |
| array.popright()            | $pop: -1         | Remove last element            |
| nested.field = value        | dot notation     | user.address.city = "Paris"    |

## Single Document Updates (less common use case)

When you already have a document loaded (`find_one` / `afind_one`), you can still use mutation syntax, but the traditional approach is usually simpler:

```python
user = await users.afind_one(users.username == "alice")

user.bio = "Loves async Python"
user.followers += 1
user.posts.push(Post(content="New post!"))

await user.save()  # Applies mutations + full document save
```

> For single documents, modifying the Python object and calling `.save()` is usually more readable.

The real power of the Mutation DSL appears when performing bulk updates without fetching documents.

## When to Use Which Approach

| Goal                                   | Recommended Approach           | Memory Usage | Speed (large N) |
| -------------------------------------- | ------------------------------ | ------------ | --------------- |
| Update 1 document (already loaded)     | Modify object -> .save()       | Low          | -               |
| Update 1 document (without loading)    | .find_one(...).mutate()        | None         | Fast            |
| Update hundreds / thousands / millions | .find(...).mutate()            | None         | Very fast       |
| Complex per-document logic             | Load -> process -> save (loop) | High         | Slow            |

Pydongo's Mutation DSL lets you harness MongoDB's atomic `updateMany` power using clean, type-safe Python syntax.

Perfect for bulk maintenance tasks, counter updates, user rewards, data cleanups, and migrations.

See the `social_media_app.py` example for a complete demonstration of rewarding many users in a single operation.
