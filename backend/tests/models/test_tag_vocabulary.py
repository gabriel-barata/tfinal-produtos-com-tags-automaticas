import pytest

from app.models.tag_vocabulary import BASE_VOCABULARY, GROUP_CARDINALITY, TagGroup, group_of


def all_base_tags() -> tuple[str, ...]:
    return tuple(tag for values in BASE_VOCABULARY.values() for tag in values)


def test_vocabulary_has_31_tags():
    assert len(all_base_tags()) == 31


def test_no_tag_repeats_across_groups():
    tags = all_base_tags()

    assert len(set(tags)) == len(tags)  # set só como oráculo de teste


def test_vocabulary_has_only_closed_groups():
    assert set(BASE_VOCABULARY) == {
        TagGroup.DEPARTMENT,
        TagGroup.SPORTS,
        TagGroup.AUDIENCE,
        TagGroup.COLORS,
    }


def test_raquete_is_a_sport_and_tenis_is_not_in_vocabulary():
    assert "raquete" in BASE_VOCABULARY[TagGroup.SPORTS]
    assert "tenis" not in all_base_tags()


@pytest.mark.parametrize(
    ("tag", "group"),
    [
        ("calcado", TagGroup.DEPARTMENT),
        ("corrida", TagGroup.SPORTS),
        ("raquete", TagGroup.SPORTS),
        ("unissex", TagGroup.AUDIENCE),
        ("azul", TagGroup.COLORS),
        ("tenis", TagGroup.FREE),
        ("qualquercoisa", TagGroup.FREE),
    ],
)
def test_group_of(tag, group):
    assert group_of(tag) == group


def test_every_group_has_a_valid_cardinality():
    assert set(GROUP_CARDINALITY) == set(TagGroup)
    for low, high in GROUP_CARDINALITY.values():
        assert 0 <= low <= high


def test_cardinality_matches_spec():
    assert GROUP_CARDINALITY[TagGroup.DEPARTMENT] == (1, 1)
    assert GROUP_CARDINALITY[TagGroup.SPORTS] == (1, 2)
    assert GROUP_CARDINALITY[TagGroup.AUDIENCE] == (1, 1)
    assert GROUP_CARDINALITY[TagGroup.COLORS] == (0, 2)
    assert GROUP_CARDINALITY[TagGroup.FREE] == (1, 4)


def test_vocabulary_is_read_only():
    with pytest.raises(TypeError):
        BASE_VOCABULARY[TagGroup.FREE] = ()  # type: ignore[index]
