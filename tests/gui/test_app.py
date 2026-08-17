from __future__ import annotations

import tkinter as tk
from pathlib import Path
from types import SimpleNamespace

from ubuntu_ai.gui import app as gui_app


class FakeRoot:
    def __init__(self) -> None:
        self.calls: list[tuple[bool, object]] = []

    def iconphoto(self, default: bool, image: object) -> None:
        self.calls.append((default, image))


def make_app(candidates: tuple[Path, ...]):
    application = gui_app.UbuntuAIApp.__new__(gui_app.UbuntuAIApp)
    application.root = FakeRoot()
    application._icon_candidates = lambda: candidates
    return application


def test_window_icon_uses_first_valid_candidate(
    tmp_path: Path,
    monkeypatch,
) -> None:
    icon = tmp_path / "valid.png"
    icon.write_bytes(b"valid")
    loaded = SimpleNamespace(name="loaded")

    monkeypatch.setattr(gui_app.tk, "PhotoImage", lambda **_kwargs: loaded)
    application = make_app((icon,))

    application._set_window_icon()

    assert application._window_icon is loaded
    assert application.root.calls == [(True, loaded)]


def test_window_icon_skips_corrupt_candidate(
    tmp_path: Path,
    monkeypatch,
) -> None:
    corrupt = tmp_path / "corrupt.png"
    valid = tmp_path / "valid.png"
    corrupt.write_bytes(b"corrupt")
    valid.write_bytes(b"valid")
    loaded = SimpleNamespace(name="fallback")

    def load_image(*, file: Path):
        if file == corrupt:
            raise tk.TclError("corrupt image")
        return loaded

    monkeypatch.setattr(gui_app.tk, "PhotoImage", load_image)
    application = make_app((corrupt, valid))

    application._set_window_icon()

    assert application._window_icon is loaded
    assert application.root.calls == [(True, loaded)]


def test_window_icon_tolerates_missing_candidates(tmp_path: Path) -> None:
    application = make_app((tmp_path / "missing.png",))

    application._set_window_icon()

    assert application._window_icon is None
    assert application.root.calls == []
