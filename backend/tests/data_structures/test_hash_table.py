import random

import pytest

from app.data_structures.hash_table import HashTable


class CollidingKey:
    """Chave de teste com hash constante: força todas as chaves no mesmo bucket."""

    def __init__(self, name: str) -> None:
        self.name = name

    def __hash__(self) -> int:
        return 42

    def __eq__(self, other: object) -> bool:
        return isinstance(other, CollidingKey) and self.name == other.name

    def __repr__(self) -> str:
        return f"CollidingKey({self.name!r})"


def test_new_table_is_empty_with_default_capacity():
    table = HashTable()

    assert len(table) == 0
    assert table.capacity == 8
    assert table.load_factor == 0
    assert tuple(table.keys()) == ()


@pytest.mark.parametrize("capacity", [0, -1, -100])
def test_initial_capacity_below_one_raises_value_error(capacity):
    with pytest.raises(ValueError):
        HashTable(initial_capacity=capacity)


def test_custom_initial_capacity():
    assert HashTable(initial_capacity=1).capacity == 1
    assert HashTable(initial_capacity=32).capacity == 32


def test_put_and_get():
    table = HashTable()

    table.put("a", 1)
    table.put("b", 2)

    assert table.get("a") == 1
    assert table.get("b") == 2
    assert len(table) == 2


def test_overwriting_existing_key_keeps_len_and_updates_value():
    table = HashTable()
    table.put("a", 1)

    table.put("a", 99)

    assert len(table) == 1
    assert table.get("a") == 99


def test_get_missing_key_returns_default():
    table = HashTable()

    assert table.get("zzz") is None
    assert table.get("zzz", 7) == 7


def test_get_does_not_return_default_when_value_is_none():
    table = HashTable()
    table.put("a", None)

    assert table.get("a", "default") is None


def test_remove_returns_value_and_decrements_len():
    table = HashTable()
    table.put("a", 1)
    table.put("b", 2)

    assert table.remove("a") == 1

    assert len(table) == 1
    assert "a" not in table
    assert table.get("b") == 2


def test_remove_missing_key_raises_key_error():
    table = HashTable()

    with pytest.raises(KeyError):
        table.remove("zzz")


def test_contains():
    table = HashTable()
    table.put("a", 1)

    assert table.contains("a")
    assert not table.contains("b")
    assert "a" in table
    assert "b" not in table


def test_dict_like_dunders():
    table = HashTable()

    table["a"] = 1
    assert table["a"] == 1

    del table["a"]
    assert "a" not in table
    assert len(table) == 0


def test_getitem_missing_key_raises_key_error():
    with pytest.raises(KeyError):
        HashTable()["zzz"]


def test_delitem_missing_key_raises_key_error():
    with pytest.raises(KeyError):
        del HashTable()["zzz"]


def test_keys_values_items_and_iter_cover_all_entries():
    table = HashTable()
    expected = {"a": 1, "b": 2, "c": 3, "d": 4}
    for key, value in expected.items():
        table[key] = value

    assert set(table.keys()) == set(expected)
    assert sorted(table.values()) == sorted(expected.values())
    assert dict(table.items()) == expected
    assert set(table) == set(expected)


def test_int_and_tuple_keys_are_supported():
    table = HashTable()
    table[1] = "um"
    table[(1, 2)] = "par"

    assert table[1] == "um"
    assert table[(1, 2)] == "par"


def test_repr_lists_entries():
    table = HashTable()
    assert repr(table) == "HashTable({})"

    table["a"] = 1
    assert repr(table) == "HashTable({'a': 1})"


def test_load_factor_is_len_over_capacity():
    table = HashTable()
    table["a"] = 1
    table["b"] = 2

    assert table.load_factor == 2 / 8


def test_resize_only_when_load_factor_exceeds_limit():
    table = HashTable()

    for i in range(6):
        table[i] = i
    # 6 / 8 = 0.75: não passa do limite, não redimensiona
    assert table.capacity == 8

    table[6] = 6
    # 7 / 8 > 0.75: dobra
    assert table.capacity == 16
    assert table.load_factor == 7 / 16


def test_overwrite_never_triggers_resize():
    table = HashTable()
    for i in range(6):
        table[i] = i

    for _ in range(50):
        table[0] = "novo"

    assert table.capacity == 8


def test_resize_keeps_every_item():
    table = HashTable()

    for i in range(1000):
        table[i] = i * 2

    assert len(table) == 1000
    assert table.capacity > 8
    assert all(table[i] == i * 2 for i in range(1000))


def test_capacity_does_not_shrink_after_removals():
    table = HashTable()
    for i in range(100):
        table[i] = i
    grown = table.capacity

    for i in range(100):
        del table[i]

    assert len(table) == 0
    assert table.capacity == grown


def test_small_initial_capacity_grows():
    table = HashTable(initial_capacity=1)

    for i in range(20):
        table[i] = i

    assert len(table) == 20
    assert all(table[i] == i for i in range(20))


def test_colliding_keys_all_work_in_a_single_bucket():
    table = HashTable()
    keys = [CollidingKey(f"k{i}") for i in range(30)]

    for i, key in enumerate(keys):
        table[key] = i

    assert len(table) == 30
    assert all(table[key] == i for i, key in enumerate(keys))
    assert CollidingKey("nao-existe") not in table
    assert table.get(CollidingKey("nao-existe"), "x") == "x"


def test_colliding_keys_overwrite_and_remove():
    table = HashTable()
    keys = [CollidingKey(f"k{i}") for i in range(10)]
    for i, key in enumerate(keys):
        table[key] = i

    table[keys[3]] = "novo"
    assert len(table) == 10
    assert table[keys[3]] == "novo"

    # remove cabeça, meio e cauda da cadeia
    for key in (keys[9], keys[5], keys[0]):
        table.remove(key)

    assert len(table) == 7
    for key in (keys[9], keys[5], keys[0]):
        assert key not in table
    assert table[keys[1]] == 1
    with pytest.raises(KeyError):
        table.remove(CollidingKey("nao-existe"))


def test_colliding_keys_survive_resize():
    table = HashTable()
    keys = [CollidingKey(f"k{i}") for i in range(50)]

    for i, key in enumerate(keys):
        table[key] = i

    assert table.capacity > 8
    assert all(table[key] == i for i, key in enumerate(keys))


def test_matches_dict_oracle_on_random_operations():
    """10 000 operações aleatórias (seed fixa) aplicadas na HashTable e em um dict."""
    rng = random.Random(1234)
    table = HashTable()
    oracle = {}

    for step in range(10_000):
        key = rng.randrange(300)  # poucas chaves: força sobrescrita, remoção e colisão
        op = rng.choice(("put", "get", "remove", "contains"))

        if op == "put":
            table.put(key, step)
            oracle[key] = step
        elif op == "get":
            assert table.get(key, "ausente") == oracle.get(key, "ausente")
        elif op == "remove":
            if key in oracle:
                assert table.remove(key) == oracle.pop(key)
            else:
                with pytest.raises(KeyError):
                    table.remove(key)
        else:
            assert table.contains(key) == (key in oracle)

        assert len(table) == len(oracle)

    assert dict(table.items()) == oracle
    assert set(table.keys()) == set(oracle)
    assert sorted(table.values()) == sorted(oracle.values())


def test_matches_dict_oracle_with_colliding_keys():
    rng = random.Random(99)
    table = HashTable()
    oracle = {}
    pool = [CollidingKey(f"k{i}") for i in range(40)]

    for step in range(3_000):
        key = rng.choice(pool)
        if rng.random() < 0.6:
            table.put(key, step)
            oracle[key] = step
        elif key in oracle:
            assert table.remove(key) == oracle.pop(key)
        else:
            assert key not in table

        assert len(table) == len(oracle)

    assert dict(table.items()) == oracle
