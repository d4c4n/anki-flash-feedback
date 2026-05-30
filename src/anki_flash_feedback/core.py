"""Pure-logic helpers. No Qt or Anki imports."""
from __future__ import annotations

from typing import Any, Dict, Tuple

VALID_EASES: Tuple[int, ...] = (1, 2, 3, 4)
EASE_LABELS: Dict[int, str] = {1: "Again", 2: "Hard", 3: "Good", 4: "Easy"}

DEFAULT_CONFIG: Dict[str, Any] = {
    "enabled": True,
    "target_opacity": 0.18,
    "hold_ms": 240,
    "fade_ms": 140,
    "eases": {
        "1": {"enabled": True, "color": "#ff3b30"},
        "2": {"enabled": True, "color": "#ff9500"},
        "3": {"enabled": True, "color": "#34c759"},
        "4": {"enabled": True, "color": "#0a84ff"},
    },
}


def clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def default_eases() -> Dict[int, Dict[str, Any]]:
    return {int(k): dict(v) for k, v in DEFAULT_CONFIG["eases"].items()}


def normalize_eases(cfg: Dict[str, Any]) -> Dict[int, Dict[str, Any]]:
    """
    Produce {int_ease: {"enabled": bool, "color": "#hex"}} from any supported
    config shape, falling back to defaults for anything missing/invalid:
      - current:      "eases": {"1": {"enabled": bool, "color": "#hex"}, ...}
      - intermediate: "ease_colors": {"1": "#hex" | "" | null, ...}
      - legacy:       "fail_color"/"pass_color"/"fail_eases"/"pass_eases"
    """
    eases = default_eases()

    src = cfg.get("eases")
    if isinstance(src, dict):
        for key, val in src.items():
            try:
                e = int(key)
            except (TypeError, ValueError):
                continue
            if e not in VALID_EASES or not isinstance(val, dict):
                continue
            if "enabled" in val:
                eases[e]["enabled"] = bool(val.get("enabled"))
            color = val.get("color")
            if color:
                eases[e]["color"] = str(color)
        return eases

    flat = cfg.get("ease_colors")
    if isinstance(flat, dict):
        for key, val in flat.items():
            try:
                e = int(key)
            except (TypeError, ValueError):
                continue
            if e not in VALID_EASES:
                continue
            hexv = "" if val is None else str(val)
            eases[e]["enabled"] = bool(hexv)
            if hexv:
                eases[e]["color"] = hexv
        return eases

    if any(k in cfg for k in ("fail_color", "pass_color", "fail_eases", "pass_eases")):
        def _assign(ease_list: Any, color: Any) -> None:
            for raw in ease_list:
                try:
                    e = int(raw)
                except (TypeError, ValueError):
                    continue
                if e in VALID_EASES:
                    eases[e] = {"enabled": True, "color": str(color)}

        _assign(cfg.get("fail_eases", [1]), cfg.get("fail_color", "#ff0000"))
        _assign(cfg.get("pass_eases", [2, 3, 4]), cfg.get("pass_color", "#00ff00"))
        return eases

    return eases


def normalize_config(raw: Any) -> Dict[str, Any]:
    """Clamp, coerce, and migrate a raw config dict (or None) to the current schema."""
    cfg: Dict[str, Any] = dict(raw) if isinstance(raw, dict) else dict(DEFAULT_CONFIG)

    cfg["enabled"] = bool(cfg.get("enabled", DEFAULT_CONFIG["enabled"]))

    cfg["target_opacity"] = float(cfg.get("target_opacity", DEFAULT_CONFIG["target_opacity"]))
    cfg["target_opacity"] = clamp(cfg["target_opacity"], 0.0, 0.6)

    cfg["hold_ms"] = int(cfg.get("hold_ms", DEFAULT_CONFIG["hold_ms"]))
    cfg["hold_ms"] = max(0, min(cfg["hold_ms"], 1000))

    cfg["fade_ms"] = int(cfg.get("fade_ms", DEFAULT_CONFIG["fade_ms"]))
    cfg["fade_ms"] = max(40, min(cfg["fade_ms"], 400))

    cfg["eases"] = normalize_eases(cfg)

    return cfg
