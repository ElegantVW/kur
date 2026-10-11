"""Kur TUI tests — think filter, mind door, hatch honesty, frame shape."""
from __future__ import annotations

import importlib.machinery
import importlib.util
import io
import json
import sys
from contextlib import contextmanager
from pathlib import Path

BIN = Path(__file__).resolve().parent.parent / "bin"


def _load():
    path = BIN / "kur"
    name = "kur_under_test"
    loader = importlib.machinery.SourceFileLoader(name, str(path))
    spec = importlib.util.spec_from_loader(name, loader)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    loader.exec_module(mod)
    return mod


@contextmanager
def _urlopen(mod, payload=None, fail=False):
    import urllib.request

    class Fake:
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def read(self):
            return json.dumps(payload or {}).encode()

    orig = urllib.request.urlopen

    def fake(*a, **k):
        if fail:
            raise ConnectionRefusedError("no pen")
        return Fake()

    urllib.request.urlopen = fake
    try:
        yield
    finally:
        urllib.request.urlopen = orig


class StubEgg:
    def __init__(self, hatched=False):
        self.hatched = hatched
        self.calls = 0

    def try_hatch_from_kur_success(self):
        self.calls += 1
        return self.hatched


def test_strip_think():
    m = _load()
    assert m.strip_think("a\nb\nc") == "a\nb\nc"
    assert m.strip_think("a <think>noisy</think> b") == "a  b"
    assert m.strip_think("line one\n<think>trailing never closes") == "line one"
    assert m.strip_think("x<think>a</think>y<think>b</think>z") == "xyz"


def test_voice_url_default_and_env(monkeypatch):
    m = _load()
    monkeypatch.delenv("KUR_URL", raising=False)
    assert m._voice_url() == "http://127.0.0.1:8083/generate"
    monkeypatch.setenv("KUR_URL", "http://10.0.0.9:9999/")
    assert m._voice_url() == "http://10.0.0.9:9999/generate"


def test_speak_once_success_and_hatch(monkeypatch):
    m = _load()
    egg = StubEgg(hatched=True)
    monkeypatch.setattr(m, "fae_egg", egg)
    with _urlopen(m, {"text": "first\n<think>noise</think>\nsecond\nthird"}):
        text, hatched = m.speak_once("hi")
    assert text == "first\n\nsecond\nthird"
    assert hatched is True
    assert egg.calls == 1


def test_speak_once_no_hatch(monkeypatch):
    m = _load()
    egg = StubEgg(hatched=False)
    monkeypatch.setattr(m, "fae_egg", egg)
    with _urlopen(m, {"text": "a\nb\nc"}):
        text, hatched = m.speak_once("hi")
    assert (text, hatched) == ("a\nb\nc", False)


def test_speak_once_asleep(monkeypatch):
    m = _load()
    monkeypatch.setattr(m, "fae_egg", StubEgg())
    try:
        with _urlopen(m, fail=True):
            m.speak_once("hi", timeout=1)
    except m.MindAsleep as e:
        assert "8083" in str(e) and "menagerie" in str(e)
    else:
        raise AssertionError("expected MindAsleep")


def test_help_and_no_tty_fallback(capsys):
    m = _load()
    assert m.main(["-h"]) == 0
    out = capsys.readouterr().out
    assert "Usage" in out
    # No tty in tests: TUI path must refuse loudly, not hang.
    assert m.main([]) == 1


def test_frame_shape():
    m = _load()
    frame = m.render_tui(
        [("you", "autumn rain"), ("glass", "grey\nrites\nunder")],
        "half-typed",
        0,
        "awake",
        False,
        2,
        "",
    )
    assert "Kur" in frame
    assert "▸ autumn rain" in frame
    assert "✦ grey" in frame
    assert "> half-typed" in frame
    assert "q quit" in frame
    assert "pen awake" in frame
    assert "· 2" in frame
