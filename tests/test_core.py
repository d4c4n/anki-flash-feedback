"""Tests for core.py — run with plain CPython, no aqt/PyQt needed."""

import core


def test_normalize_current_schema_passthrough() -> None:
    raw = {
        "enabled": True,
        "target_opacity": 0.18,
        "hold_ms": 240,
        "fade_ms": 140,
        "eases": {
            "1": {"enabled": True, "color": "#ff3b30"},
            "2": {"enabled": False, "color": "#ff9500"},
            "3": {"enabled": True, "color": "#34c759"},
            "4": {"enabled": True, "color": "#0a84ff"},
        },
    }
    cfg = core.normalize_config(raw)
    assert cfg["eases"][1]["color"] == "#ff3b30"
    assert cfg["eases"][2]["enabled"] is False
    assert cfg["eases"][3]["color"] == "#34c759"
    assert cfg["eases"][4]["enabled"] is True


def test_normalize_intermediate_schema() -> None:
    raw = {
        "ease_colors": {
            "1": "#ff0000",
            "2": "",
            "3": None,
            "4": "#0000ff",
        }
    }
    cfg = core.normalize_config(raw)
    assert cfg["eases"][1]["enabled"] is True
    assert cfg["eases"][1]["color"] == "#ff0000"
    assert cfg["eases"][2]["enabled"] is False
    assert cfg["eases"][3]["enabled"] is False
    assert cfg["eases"][4]["enabled"] is True
    assert cfg["eases"][4]["color"] == "#0000ff"


def test_normalize_legacy_schema() -> None:
    raw = {
        "fail_color": "#ff0000",
        "pass_color": "#00ff00",
        "fail_eases": [1],
        "pass_eases": [2, 3, 4],
    }
    cfg = core.normalize_config(raw)
    assert cfg["eases"][1]["enabled"] is True
    assert cfg["eases"][1]["color"] == "#ff0000"
    assert cfg["eases"][2]["color"] == "#00ff00"
    assert cfg["eases"][3]["enabled"] is True
    assert cfg["eases"][4]["color"] == "#00ff00"


def test_clamp_opacity_above_max() -> None:
    cfg = core.normalize_config({"target_opacity": 1.5})
    assert cfg["target_opacity"] == 0.6


def test_clamp_opacity_below_min() -> None:
    cfg = core.normalize_config({"target_opacity": -0.1})
    assert cfg["target_opacity"] == 0.0


def test_clamp_hold_above_max() -> None:
    cfg = core.normalize_config({"hold_ms": 9999})
    assert cfg["hold_ms"] == 1000


def test_clamp_hold_below_min() -> None:
    cfg = core.normalize_config({"hold_ms": -1})
    assert cfg["hold_ms"] == 0


def test_clamp_fade_above_max() -> None:
    cfg = core.normalize_config({"fade_ms": 9999})
    assert cfg["fade_ms"] == 400


def test_clamp_fade_below_min() -> None:
    cfg = core.normalize_config({"fade_ms": 0})
    assert cfg["fade_ms"] == 40


def test_none_config_returns_defaults() -> None:
    cfg = core.normalize_config(None)
    assert cfg["enabled"] == core.DEFAULT_CONFIG["enabled"]
    assert cfg["target_opacity"] == core.DEFAULT_CONFIG["target_opacity"]
    assert cfg["hold_ms"] == core.DEFAULT_CONFIG["hold_ms"]
    assert cfg["fade_ms"] == core.DEFAULT_CONFIG["fade_ms"]
    for e in core.VALID_EASES:
        assert e in cfg["eases"]


def test_invalid_ease_keys_ignored() -> None:
    raw = {
        "eases": {
            "0": {"enabled": True, "color": "#ff0000"},
            "5": {"enabled": True, "color": "#ff0000"},
            "abc": {"enabled": True, "color": "#ff0000"},
        }
    }
    cfg = core.normalize_config(raw)
    for e in core.VALID_EASES:
        assert e in cfg["eases"]


def test_missing_color_keeps_default() -> None:
    raw = {"eases": {"1": {"enabled": True}}}
    cfg = core.normalize_config(raw)
    assert cfg["eases"][1]["color"] == core.DEFAULT_CONFIG["eases"]["1"]["color"]


def test_round_trip_dialog_schema() -> None:
    """Schema produced by ConfigDialog.result_config() survives normalize_config."""
    dialog_output = {
        "enabled": False,
        "target_opacity": 0.25,
        "hold_ms": 300,
        "fade_ms": 200,
        "eases": {
            "1": {"enabled": True, "color": "#ff3b30"},
            "2": {"enabled": False, "color": "#ff9500"},
            "3": {"enabled": True, "color": "#34c759"},
            "4": {"enabled": True, "color": "#0a84ff"},
        },
    }
    cfg = core.normalize_config(dialog_output)
    assert cfg["enabled"] is False
    assert cfg["target_opacity"] == 0.25
    assert cfg["hold_ms"] == 300
    assert cfg["fade_ms"] == 200
    assert cfg["eases"][1]["color"] == "#ff3b30"
    assert cfg["eases"][2]["enabled"] is False
