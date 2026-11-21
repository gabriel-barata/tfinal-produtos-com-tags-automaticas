import random

import pytest

from app.data_structures.hash_set import HashSet


def test_new_set_is_empty():
    s = HashSet()

    assert len(s) == 0
    assert tuple(s) == ()
    assert repr(s) == "HashSet()"


def test_add_and_contains():
    s = HashSet()

    s.add("a")
    s.add("b")

    assert "a" in s
    assert "b" in s
    assert "c" not in s
    assert len(s) == 2


def test_adding_repeated_item_does_not_change_len():
    s = HashSet()
    s.add("a")

    s.add("a")
    s.add("a")

    assert len(s) == 1
    assert tuple(s) == ("a",)


def test_remove_deletes_item():
    s = HashSet()
    s.add("a")
    s.add("b")

    s.remove("a")

    assert "a" not in s
    assert "b" in s
    assert len(s) == 1


def test_remove_missing_item_raises_key_error():
    s = HashSet()

    with pytest.raises(KeyError):
        s.remove("zzz")


def test_discard_is_silent_when_missing():
    s = HashSet()
    s.add("a")

    s.discard("zzz")
    assert len(s) == 1

    s.discard("a")
    assert "a" not in s
    assert len(s) == 0


def test_iter_yields_every_item_once():
    s = HashSet()
    for item in ("a", "b", "c", "a"):
        s.add(item)

    assert sorted(s) == ["a", "b", "c"]


def test_repr_lists_items():
    s = HashSet()
    s.add(1)

    assert repr(s) == "HashSet({1})"


def test_many_items_survive_internal_resize():
    s = HashSet()

    for i in range(500):
        s.add(i)

    assert len(s) == 500
    assert all(i in s for i in range(500))


def test_matches_set_oracle_on_random_operations():
    """5 000 operações aleatórias (seed fixa) aplicadas no HashSet e em um set."""
    rng = random.Random(4321)
    hash_set = HashSet()
    oracle = set()

    for _ in range(5_000):
        item = rng.randrange(200)
        op = rng.choice(("add", "remove", "discard", "contains"))

        if op == "add":
            hash_set.add(item)
            oracle.add(item)
        elif op == "remove":
            if item in oracle:
                hash_set.remove(item)
                oracle.remove(item)
            else:
                with pytest.raises(KeyError):
                    hash_set.remove(item)
        elif op == "discard":
            hash_set.discard(item)
            oracle.discard(item)
        else:
            assert (item in hash_set) == (item in oracle)

        assert len(hash_set) == len(oracle)

    assert set(hash_set) == oracle
