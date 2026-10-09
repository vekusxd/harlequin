"""Geometry for resizing the main panels.

Two dividers can be moved: the right edge of the Data Catalog, and the border
between the Query Editor and the Results Viewer (the Run Query Bar sits between
them and moves with it).
"""

from __future__ import annotations

from typing import Literal

from textual.geometry import Region

ResizeTarget = Literal["sidebar", "split"]

SIDEBAR_MIN_WIDTH = 12
"""The narrowest the Data Catalog can be made, in cells."""
SIDEBAR_MIN_REMAINING = 30
"""Cells that must stay available to the editor and the results."""
SPLIT_MIN = 10.0
SPLIT_MAX = 90.0
"""Bounds of the Query Editor's share of the split, in percent."""
SPLIT_DEFAULT = 50.0


def clamp_sidebar_width(width: int, total_width: int) -> int:
    """Keep the Data Catalog between its minimum and what the screen can spare."""
    maximum = max(SIDEBAR_MIN_WIDTH, total_width - SIDEBAR_MIN_REMAINING)
    return max(SIDEBAR_MIN_WIDTH, min(width, maximum))


def clamp_split(percent: float) -> float:
    return max(SPLIT_MIN, min(percent, SPLIT_MAX))


def sidebar_width_at(x: int, sidebar: Region) -> int:
    """The Data Catalog width that puts its right border under the pointer at `x`."""
    return x - sidebar.x + 1


def split_at(y: int, editor: Region, results: Region) -> float:
    """The Query Editor's share of the split, in percent, for a pointer at row `y`.

    The editor's bottom border follows the pointer.
    """
    total = editor.height + results.height
    if total <= 0:
        return SPLIT_DEFAULT
    return (y - editor.y + 1) / total * 100


def on_sidebar_edge(x: int, y: int, sidebar: Region) -> bool:
    """Whether the pointer is on the Data Catalog's right border, or the border
    of the panel next to it."""
    if not sidebar.y <= y < sidebar.bottom:
        return False
    return x in (sidebar.right - 1, sidebar.right)


def on_split_edge(x: int, y: int, editor: Region, results: Region) -> bool:
    """Whether the pointer is on the editor's bottom border or the results' top
    border."""
    if not editor.x <= x < editor.right:
        return False
    return y in (editor.bottom - 1, results.y)
