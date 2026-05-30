from __future__ import annotations

from typing import Any, Optional

from aqt import mw
from aqt.qt import QColor, QEvent, QObject, QTimer

from .core import normalize_config
from .overlay import FlashOverlay, parse_color

_manager: Optional[FlashManager] = None


def get_manager() -> Optional[FlashManager]:
    return _manager


class FlashManager(QObject):
    """Owns the overlay and keeps it aligned with the main window size."""

    def __init__(self) -> None:
        super().__init__()
        self._cfg = normalize_config(mw.addonManager.getConfig(__package__))
        self._overlay = FlashOverlay(mw)
        mw.installEventFilter(self)

    def reload_config(self) -> None:
        self._cfg = normalize_config(mw.addonManager.getConfig(__package__))

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # type: ignore[override]
        if watched is mw and event.type() in (
            QEvent.Type.Resize,
            QEvent.Type.Show,
            QEvent.Type.WindowStateChange,
        ):
            if self._overlay.isVisible():
                self._overlay.setGeometry(mw.rect())
        return False

    def flash_for_ease(self, ease: int) -> None:
        self.reload_config()
        if not self._cfg.get("enabled", True):
            return
        info = self._cfg["eases"].get(int(ease))
        if not info or not info.get("enabled"):
            return
        color = parse_color(info.get("color") or "#ffffff", QColor("#ffffff"))
        target_opacity = float(self._cfg["target_opacity"])
        hold_ms = int(self._cfg["hold_ms"])
        fade_ms = int(self._cfg["fade_ms"])
        QTimer.singleShot(
            0,
            lambda c=color, o=target_opacity, h=hold_ms, f=fade_ms: self._overlay.flash(
                c, o, h, f
            ),
        )


def on_reviewer_did_answer_card(reviewer: Any, card: Any, ease: int) -> None:
    global _manager
    try:
        if _manager is None:
            _manager = FlashManager()
        _manager.flash_for_ease(int(ease))
    except Exception as e:
        print("[Anki Flash Feedback] Error:", repr(e))
