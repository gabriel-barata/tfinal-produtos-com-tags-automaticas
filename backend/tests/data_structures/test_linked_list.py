import pytest

from app.data_structures.linked_list import LinkedList, Node


def build(*pairs: tuple[str, int]) -> LinkedList:
    """Monta uma lista inserindo na ordem dada (o último par vira a cabeça)."""
    lst = LinkedList()
    for key, value in pairs:
        lst.insert_front(key, value)
    return lst


def keys_in_order(lst: LinkedList) -> tuple:
    return tuple(node.key for node in lst)


def test_node_stores_key_value_and_next():
    tail = Node("b", 2)
    node = Node("a", 1, tail)

    assert (node.key, node.value, node.next) == ("a", 1, tail)
    assert Node("x", 0).next is None


def test_new_list_is_empty():
    lst = LinkedList()

    assert len(lst) == 0
    assert not lst
    assert lst.head is None
    assert tuple(lst) == ()


def test_insert_front_puts_new_node_at_head():
    lst = build(("a", 1), ("b", 2), ("c", 3))

    assert keys_in_order(lst) == ("c", "b", "a")
    assert lst.head.key == "c"
    assert len(lst) == 3
    assert lst


def test_find_node_returns_node_or_none():
    lst = build(("a", 1), ("b", 2), ("c", 3))

    node = lst.find_node("b")
    assert node is not None
    assert node.value == 2
    assert lst.find_node("zzz") is None
    assert LinkedList().find_node("a") is None


def test_find_node_allows_updating_value_in_place():
    lst = build(("a", 1))

    lst.find_node("a").value = 99

    assert lst.find_node("a").value == 99
    assert len(lst) == 1


def test_remove_head():
    lst = build(("a", 1), ("b", 2), ("c", 3))  # c -> b -> a

    assert lst.remove("c") == 3
    assert keys_in_order(lst) == ("b", "a")
    assert len(lst) == 2


def test_remove_middle():
    lst = build(("a", 1), ("b", 2), ("c", 3))

    assert lst.remove("b") == 2
    assert keys_in_order(lst) == ("c", "a")
    assert len(lst) == 2


def test_remove_tail():
    lst = build(("a", 1), ("b", 2), ("c", 3))

    assert lst.remove("a") == 1
    assert keys_in_order(lst) == ("c", "b")
    assert len(lst) == 2


def test_remove_single_element_leaves_empty_list():
    lst = build(("a", 1))

    assert lst.remove("a") == 1
    assert lst.head is None
    assert len(lst) == 0
    assert not lst


def test_remove_missing_key_raises_key_error_and_keeps_list():
    lst = build(("a", 1), ("b", 2))

    with pytest.raises(KeyError):
        lst.remove("zzz")

    assert keys_in_order(lst) == ("b", "a")
    assert len(lst) == 2


def test_remove_from_empty_list_raises_key_error():
    with pytest.raises(KeyError):
        LinkedList().remove("a")


def test_remove_then_insert_again():
    lst = build(("a", 1), ("b", 2))

    lst.remove("a")
    lst.insert_front("a", 10)

    assert keys_in_order(lst) == ("a", "b")
    assert lst.find_node("a").value == 10


def test_iteration_yields_nodes_and_is_repeatable():
    lst = build(("a", 1), ("b", 2))

    first = tuple((n.key, n.value) for n in lst)
    second = tuple((n.key, n.value) for n in lst)

    assert first == (("b", 2), ("a", 1))
    assert first == second
    assert all(isinstance(n, Node) for n in lst)


def test_len_is_correct_after_mixed_operations():
    lst = LinkedList()
    expected = 0
    for i in range(10):
        lst.insert_front(f"k{i}", i)
        expected += 1
    for i in (0, 9, 4, 5):  # cauda, cabeça, meio, meio
        lst.remove(f"k{i}")
        expected -= 1
        assert len(lst) == expected
    with pytest.raises(KeyError):
        lst.remove("k0")  # já removida: len não muda
    assert len(lst) == expected == sum(1 for _ in lst)


def test_repr_shows_pairs_in_order():
    assert repr(LinkedList()) == "LinkedList()"
    assert repr(build(("a", 1), ("b", 2))) == "LinkedList(('b', 2) -> ('a', 1))"
