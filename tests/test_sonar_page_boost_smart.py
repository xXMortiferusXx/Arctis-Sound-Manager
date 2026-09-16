# Copyright (C) 2026 loteran
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for per-channel Boost / Smart Volume persistence (Option A).

Boost and Smart Volume used to be a single global value stored in a flat JSON
file and applied to every channel's filter chain. They are now per-channel:
one dict keyed by channel in ``sonar_boost.json`` / ``sonar_smart_volume.json``,
with a legacy flat file migrated in place on read.
"""

from __future__ import annotations

import json
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest

pytest.importorskip("PySide6")

from arctis_sound_manager.gui import sonar_page as sp  # noqa: E402


@pytest.fixture(autouse=True)
def _tmp_cfg(monkeypatch, tmp_path):
    monkeypatch.setattr(sp, "_CFG", tmp_path)
    monkeypatch.setattr(sp, "_BOOST_FILE", tmp_path / "sonar_boost.json")
    monkeypatch.setattr(sp, "_SMART_FILE", tmp_path / "sonar_smart_volume.json")
    return tmp_path


def test_boost_per_channel_isolated(tmp_path):
    """Saving boost for chat must not affect game/media/aux."""
    sp._save_boost("chat", {"enabled": True, "db": 6.0})
    sp._save_boost("game", {"enabled": False, "db": 3.0})

    assert sp._load_boost("chat")["enabled"] is True
    assert sp._load_boost("chat")["db"] == 6.0
    # game kept its own value; media/aux fall back to defaults.
    assert sp._load_boost("game") == {"enabled": False, "db": 3.0}
    assert sp._load_boost("media") == sp._BOOST_DEFAULTS
    assert sp._load_boost("aux") == sp._BOOST_DEFAULTS

    # On-disk format is a per-channel dict, not a flat value.
    on_disk = json.loads((tmp_path / "sonar_boost.json").read_text())
    assert set(on_disk) == {"chat", "game"}


def test_boost_legacy_flat_migrates(tmp_path):
    """A legacy flat boost file applies its value to every boost channel."""
    (tmp_path / "sonar_boost.json").write_text(
        json.dumps({"enabled": True, "db": 4.0})
    )
    for ch in sp._BOOST_CHANNELS:
        state = sp._load_boost(ch)
        assert state["enabled"] is True
        assert state["db"] == 4.0


def test_smart_per_channel_isolated(tmp_path):
    """Saving Smart Volume for chat must not affect game/media/aux."""
    sp._save_smart_volume("chat", {"enabled": True, "level": 80.0, "loudness": "loud"})

    assert sp._load_smart_volume("chat")["enabled"] is True
    assert sp._load_smart_volume("chat")["level"] == 80.0
    assert sp._load_smart_volume("chat")["loudness"] == "loud"
    assert sp._load_smart_volume("game") == sp._SMART_DEFAULTS

    on_disk = json.loads((tmp_path / "sonar_smart_volume.json").read_text())
    assert set(on_disk) == {"chat"}


def test_smart_legacy_flat_migrates(tmp_path):
    """A legacy flat smart-volume file applies its value to every channel."""
    (tmp_path / "sonar_smart_volume.json").write_text(
        json.dumps({"enabled": True, "level": 50.0, "loudness": "quiet"})
    )
    for ch in sp._BOOST_CHANNELS:
        state = sp._load_smart_volume(ch)
        assert state["enabled"] is True
        assert state["level"] == 50.0
        assert state["loudness"] == "quiet"


def test_defaults_are_sane():
    """Boost defaults to a usable +3 dB; Smart Volume to a mid level (so it is
    not a no-op compressor when enabled)."""
    assert sp._BOOST_DEFAULTS == {"enabled": False, "db": 3.0}
    assert sp._SMART_DEFAULTS == {"enabled": False, "level": 50.0, "loudness": "balanced"}
