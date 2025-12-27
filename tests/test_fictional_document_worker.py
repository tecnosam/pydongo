import asyncio
import pytest

import threading

from pydongo.expressions.mutation import MutationExpression

from pydongo.workers.collection import CollectionWorker

from tests.resources import DummyModel


def test_field_expression_setattr_adds_mutation(driver) -> None:
    """Test that setting an attribute on CollectionResponseBuilder adds a mutation."""

    collection = CollectionWorker(
        pydantic_model=DummyModel,
        driver=driver,
        collection_name="dummy_models"
    )
    
    builder = collection.find()

    builder.name = "Alice"
    builder.age = 30

    mutations = builder.get_mutations()

    assert mutations == {
        "$set": {
            "name": "Alice",
            "age": 30,
        }
    }


def test_field_expression_setattr_with_mutation_expression(driver) -> None:
    """Test that setting an attribute with a MutationExpression adds the mutation correctly."""
    collection = CollectionWorker(
        pydantic_model=DummyModel,
        driver=driver,
        collection_name="dummy_models"
    )
    
    builder = collection.find()

    builder.age = MutationExpression(
        field_name="age",
        operation="$inc",
        value=5,
    )

    mutations = builder.get_mutations()

    assert mutations == {
        "$inc": {
            "age": 5,
        }
    }


def test_array_field_expression_setattr_adds_array_mutation(driver) -> None:
    """Test that setting an attribute on CollectionResponseBuilder for an array field adds the correct mutation."""
    collection = CollectionWorker(
        pydantic_model=DummyModel,
        driver=driver,
        collection_name="dummy_models"
    )
    
    builder = collection.find()

    builder.friends = ["friend1", "friend2", "friend3"]

    mutations = builder.get_mutations()

    assert mutations == {
        "$set": {
            "friends": ["friend1", "friend2", "friend3"],
        }
    }

    # Test push, pop
    builder.friends.push("friend4")
    builder.friends.popleft()
    builder.friends.pull("friend2")

    builder.friends.add_to_set("friend5")

    mutations = builder.get_mutations()

    assert mutations == {
        "$set": {
            "friends": ["friend1", "friend2", "friend3"],
        },
        "$push": {
            "friends": "friend4",
        },
        "$pop": {
            "friends": 1,
        },
        "$pull": {
            "friends": "friend2",
        },
        "$addToSet": {
            "friends": "friend5",
        },
    }


def test_numerical_operations_adds_numeric_mutations(driver) -> None:
    """Test that numerical operations on CollectionResponseBuilder add the correct mutations."""
    collection = CollectionWorker(
        pydantic_model=DummyModel,
        driver=driver,
        collection_name="dummy_models"
    )
    
    builder = collection.find()

    builder.age += 5

    assert builder.get_mutations() == {
        "$inc": {
            "age": 5,
        }
    }

    builder.age -= 2
    mutations = builder.get_mutations()

    # Overwrite behaviour: the last operation should be the one present

    assert mutations == {
        "$inc": {
            "age": -2,
        }
    }

    builder.age *= 3
    mutations = builder.get_mutations()
    assert mutations == {
        "$inc": {
            "age": -2,
        },
        "$mul": {
            "age": 3,
        },
    }
    builder.age /= 4
    mutations = builder.get_mutations()
    assert mutations == {
        "$inc": {
            "age": -2,
        },
        "$mul": {
            "age": 0.25,
        },
    }


def test_mutation_expression_context_thread_safe(driver) -> None:
    collection = CollectionWorker(
        pydantic_model=DummyModel,
        driver=driver,
        collection_name="dummy_models",
    )

    results: dict[str, dict] = {}

    def worker(name: str, delta: int) -> None:
        builder = collection.find()
        builder.age += delta
        results[name] = builder.get_mutations()

    t1 = threading.Thread(target=worker, args=("a", 5))
    t2 = threading.Thread(target=worker, args=("b", -7))

    t1.start()
    t2.start()
    t1.join()
    t2.join()

    assert results["a"] == {
        "$inc": {"age": 5},
    }

    assert results["b"] == {
        "$inc": {"age": -7},
    }


def test_mutate_resets_context_and_flushes_old_mutations(driver) -> None:
    collection = CollectionWorker(
        pydantic_model=DummyModel,
        driver=driver,
        collection_name="dummy_models",
    )

    builder = collection.find()

    # First batch of mutations
    builder.age += 10
    builder.name = "Alice"

    assert builder.get_mutations() == {
        "$inc": {"age": 10},
        "$set": {"name": "Alice"},
    }

    # Execute mutation (this should flush/reset context)
    builder.mutate()

    # Context must be clean
    assert builder.get_mutations() == {}

    # New mutations should NOT include old ones
    builder.age += 3

    assert builder.get_mutations() == {
        "$inc": {"age": 3},
    }


@pytest.mark.asyncio
async def test_mutation_context_is_async_safe(driver) -> None:
    collection = CollectionWorker(
        pydantic_model=DummyModel,
        driver=driver,
        collection_name="dummy_models",
    )

    async def worker(delta: int) -> dict:
        builder = collection.find()
        builder.age += delta

        # Yield control to force context switching
        await asyncio.sleep(0.5)

        return builder.get_mutations()

    result_a, result_b = await asyncio.gather(
        worker(5),
        worker(-7),
    )

    assert result_a == {
        "$inc": {"age": 5},
    }

    assert result_b == {
        "$inc": {"age": -7},
    }

