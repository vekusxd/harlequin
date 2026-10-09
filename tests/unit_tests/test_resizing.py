from textual.geometry import Region

from harlequin.resizing import (
    SIDEBAR_MIN_WIDTH,
    SPLIT_MAX,
    SPLIT_MIN,
    clamp_sidebar_width,
    clamp_split,
    on_sidebar_edge,
    on_split_edge,
    sidebar_width_at,
    split_at,
)


def test_sidebar_width_is_clamped() -> None:
    assert clamp_sidebar_width(4, total_width=120) == SIDEBAR_MIN_WIDTH
    assert clamp_sidebar_width(50, total_width=120) == 50
    assert clamp_sidebar_width(200, total_width=120) == 90


def test_split_is_clamped() -> None:
    assert clamp_split(0) == SPLIT_MIN
    assert clamp_split(60) == 60
    assert clamp_split(100) == SPLIT_MAX


def test_sidebar_width_follows_the_pointer() -> None:
    assert sidebar_width_at(41, Region(0, 0, 30, 38)) == 42


def test_split_follows_the_pointer() -> None:
    editor, results = Region(30, 0, 90, 19), Region(30, 20, 90, 19)
    assert split_at(18, editor, results) == 50
    assert round(split_at(26, editor, results)) == 71


def test_edges_are_detected() -> None:
    sidebar = Region(0, 0, 30, 38)
    assert on_sidebar_edge(29, 10, sidebar)
    assert on_sidebar_edge(30, 10, sidebar)
    assert not on_sidebar_edge(28, 10, sidebar)
    assert not on_sidebar_edge(29, 38, sidebar)

    editor, results = Region(30, 0, 90, 19), Region(30, 20, 90, 19)
    assert on_split_edge(50, 18, editor, results)
    assert on_split_edge(50, 20, editor, results)
    assert not on_split_edge(50, 19, editor, results)
    assert not on_split_edge(10, 18, editor, results)
