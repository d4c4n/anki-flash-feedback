from __future__ import annotations

from aqt.qt import (
    QColor,
    QGraphicsOpacityEffect,
    QPainter,
    QPropertyAnimation,
    Qt,
    QTimer,
    QWidget,
)


def parse_color(value: str, fallback: QColor) -> QColor:
    """Accepts "#RRGGBB" or "#AARRGGBB". Returns fallback on failure."""
    try:
        c = QColor(value)
        return c if c.isValid() else fallback
    except Exception:
        return fallback


class FlashOverlay(QWidget):
    """
    Transparent widget that paints a solid color over its entire rect, with a
    QGraphicsOpacityEffect for fade-out. Ignores mouse/keyboard events.
    """

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.setAutoFillBackground(False)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self._color: QColor = QColor(0, 0, 0, 0)
        self._fade_ms: int = 140

        self._effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self._effect)
        self._effect.setOpacity(0.0)

        self._anim = QPropertyAnimation(self._effect, b"opacity", self)
        self._anim.finished.connect(self._on_anim_finished)

        self._hold_timer = QTimer(self)
        self._hold_timer.setSingleShot(True)
        self._hold_timer.timeout.connect(self._start_fade)

        self.hide()

    def set_color(self, color: QColor) -> None:
        self._color = QColor(color)
        self.update()

    def paintEvent(self, event) -> None:  # type: ignore[override]
        if self._color.alpha() == 0:
            return
        p = QPainter(self)
        p.fillRect(self.rect(), self._color)

    def flash(self, color: QColor, target_opacity: float, hold_ms: int, fade_ms: int) -> None:
        """Start/restart a flash. Safe for rapid repeated calls."""
        if self._hold_timer.isActive():
            self._hold_timer.stop()
        if self._anim.state() != QPropertyAnimation.State.Stopped:
            self._anim.stop()

        self.set_color(color)

        parent = self.parentWidget()
        if parent is not None:
            self.setGeometry(parent.rect())

        self.show()
        self.raise_()

        self._effect.setOpacity(target_opacity)
        self._fade_ms = fade_ms
        self._hold_timer.start(hold_ms)

    def _start_fade(self) -> None:
        current = float(self._effect.opacity())
        self._anim.stop()
        self._anim.setDuration(self._fade_ms)
        self._anim.setStartValue(current)
        self._anim.setEndValue(0.0)
        self._anim.start()

    def _on_anim_finished(self) -> None:
        if float(self._effect.opacity()) <= 0.001:
            self.hide()
