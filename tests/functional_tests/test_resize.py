from typing import Awaitable, Callable

import pytest

from harlequin import Harlequin
from harlequin.components import KeysPanel
from harlequin.resizing import SIDEBAR_MIN_REMAINING, SPLIT_DEFAULT
from tests.functional_tests.helpers import wait_for_editor

SIZE = (120, 40)


@pytest.mark.asyncio
async def test_resize_mode_moves_the_sidebar_edge(
    app: Harlequin,
    wait_for_workers: Callable[[Harlequin], Awaitable[None]],
) -> None:
    async with app.run_test(size=SIZE) as pilot:
        await wait_for_workers(app)
        await wait_for_editor(pilot, app)
        catalog = app.data_catalog
        catalog.focus()
        await pilot.pause()
        before = catalog.outer_size.width
        await pilot.press("ctrl+shift+r", "l", "l", "L")
        await pilot.pause()
        assert app.resize_mode
        assert app.resize_target == "sidebar"
        assert catalog.has_class("-resize-target")
        assert catalog.outer_size.width == before + 14
        await pilot.press("h")
        await pilot.pause()
        assert catalog.outer_size.width == before + 12
        await pilot.press("equals_sign")
        await pilot.pause()
        assert catalog.outer_size.width == before


@pytest.mark.asyncio
async def test_resize_mode_moves_the_editor_results_split(
    app: Harlequin,
    wait_for_workers: Callable[[Harlequin], Awaitable[None]],
) -> None:
    async with app.run_test(size=SIZE) as pilot:
        await wait_for_workers(app)
        editor = await wait_for_editor(pilot, app)
        editor.focus()
        await pilot.press("ctrl+shift+r")
        await pilot.pause()
        assert app.resize_target == "split"
        assert app.editor_collection.has_class("-resize-target")
        assert not app.data_catalog.has_class("-resize-target")
        await pilot.press("j", "j", "j", "j", "j")
        await pilot.pause()
        assert app.split_percent == 60
        assert (
            app.editor_collection.outer_size.height
            > app.results_viewer.outer_size.height
        )
        await pilot.press("tab")
        assert app.resize_target != "split"


@pytest.mark.asyncio
async def test_leaving_resize_mode_gives_keys_back(
    app: Harlequin,
    wait_for_workers: Callable[[Harlequin], Awaitable[None]],
) -> None:
    async with app.run_test(size=SIZE) as pilot:
        await wait_for_workers(app)
        editor = await wait_for_editor(pilot, app)
        editor.focus()
        await pilot.press("ctrl+shift+r")
        await pilot.pause()
        assert app.focused is None
        await pilot.press("escape")
        await pilot.pause()
        assert not app.resize_mode
        assert not app.editor_collection.has_class("-resize-target")
        assert app.focused is editor.text_input
        await pilot.press("j")
        await pilot.pause()
        assert editor.text == "j"
        assert app.split_percent == SPLIT_DEFAULT


@pytest.mark.asyncio
async def test_resized_panels_still_hide(
    app: Harlequin,
    wait_for_workers: Callable[[Harlequin], Awaitable[None]],
) -> None:
    async with app.run_test(size=SIZE) as pilot:
        await wait_for_workers(app)
        editor = await wait_for_editor(pilot, app)
        app.sidebar_width = 50
        app.split_percent = 70
        await pilot.pause()
        assert app.data_catalog.outer_size.width == 50

        await pilot.press("ctrl+b")
        await pilot.pause()
        assert app.data_catalog.outer_size.width == 0
        await pilot.press("ctrl+b")
        await pilot.pause()
        assert app.data_catalog.outer_size.width == 50

        editor.focus()
        await pilot.press("f10")
        await pilot.pause()
        assert app.results_viewer.outer_size.height == 0
        assert app.data_catalog.outer_size.width == 0
        await pilot.press("f10")
        await pilot.pause()
        assert app.results_viewer.outer_size.height > 0
        assert (
            app.editor_collection.outer_size.height
            > app.results_viewer.outer_size.height
        )


@pytest.mark.asyncio
async def test_dragging_the_sidebar_edge(
    app: Harlequin,
    wait_for_workers: Callable[[Harlequin], Awaitable[None]],
) -> None:
    async with app.run_test(size=SIZE) as pilot:
        await wait_for_workers(app)
        await wait_for_editor(pilot, app)
        catalog = app.data_catalog
        edge = catalog.region.right - 1
        y = catalog.region.y + 5
        await pilot.mouse_down(offset=(edge, y))
        assert catalog.has_class("-resize-target")
        await pilot.hover(offset=(edge + 10, y))
        await pilot.mouse_up(offset=(edge + 10, y))
        await pilot.pause()
        assert catalog.region.right - 1 == edge + 10


@pytest.mark.asyncio
async def test_dragging_the_split(
    app: Harlequin,
    wait_for_workers: Callable[[Harlequin], Awaitable[None]],
) -> None:
    async with app.run_test(size=SIZE) as pilot:
        await wait_for_workers(app)
        await wait_for_editor(pilot, app)
        editor_region = app.editor_collection.region
        x = editor_region.x + 5
        edge = editor_region.bottom - 1
        await pilot.mouse_down(offset=(x, edge))
        await pilot.hover(offset=(x, edge - 6))
        await pilot.mouse_up(offset=(x, edge - 6))
        await pilot.pause()
        assert app.editor_collection.region.bottom - 1 == edge - 6
        assert (
            app.editor_collection.outer_size.height
            < app.results_viewer.outer_size.height
        )


@pytest.mark.asyncio
async def test_focusing_a_widget_ends_resize_mode(
    app: Harlequin,
    wait_for_workers: Callable[[Harlequin], Awaitable[None]],
) -> None:
    async with app.run_test(size=SIZE) as pilot:
        await wait_for_workers(app)
        editor = await wait_for_editor(pilot, app)
        await pilot.press("ctrl+shift+r")
        await pilot.pause()
        assert app.resize_mode
        app.results_viewer.focus()
        await pilot.pause()
        assert not app.resize_mode
        assert app.focused is not None
        assert editor is not None


@pytest.mark.asyncio
async def test_sidebar_leaves_room_for_the_main_panel_beside_the_keys_panel(
    app: Harlequin,
    wait_for_workers: Callable[[Harlequin], Awaitable[None]],
) -> None:
    async with app.run_test(size=SIZE) as pilot:
        await wait_for_workers(app)
        await wait_for_editor(pilot, app)
        app.data_catalog.focus()
        await pilot.press("f7")
        await pilot.pause()
        assert app.screen.query(KeysPanel)
        await pilot.press("ctrl+shift+r", *["L"] * 20)
        await pilot.pause()
        main_panel = app.query_one("#main_panel")
        assert main_panel.outer_size.width >= SIDEBAR_MIN_REMAINING
