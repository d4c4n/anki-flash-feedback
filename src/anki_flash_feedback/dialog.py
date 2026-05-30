from __future__ import annotations

from typing import Any, Dict

from aqt.qt import (
    QCheckBox,
    QColor,
    QColorDialog,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QLabel,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from .core import DEFAULT_CONFIG, EASE_LABELS, VALID_EASES
from .overlay import parse_color


class ConfigDialog(QDialog):
    def __init__(self, parent: QWidget, cfg: Dict[str, Any]) -> None:
        super().__init__(parent)
        self.setWindowTitle("Flash Feedback")

        self._enable_boxes: Dict[int, QCheckBox] = {}
        self._color_buttons: Dict[int, QPushButton] = {}
        self._colors: Dict[int, str] = {}

        layout = QVBoxLayout(self)

        self._master = QCheckBox("Enable flash feedback")
        self._master.setChecked(bool(cfg["enabled"]))
        layout.addWidget(self._master)

        ease_group = QGroupBox("Answer buttons")
        grid = QGridLayout(ease_group)
        grid.addWidget(QLabel("Button"), 0, 0)
        grid.addWidget(QLabel("Flash"), 0, 1)
        grid.addWidget(QLabel("Color"), 0, 2)
        for row, ease in enumerate(VALID_EASES, start=1):
            info = cfg["eases"][ease]
            grid.addWidget(QLabel(EASE_LABELS[ease]), row, 0)

            box = QCheckBox()
            box.setChecked(bool(info["enabled"]))
            self._enable_boxes[ease] = box
            grid.addWidget(box, row, 1)

            self._colors[ease] = str(info["color"])
            btn = QPushButton()
            btn.setFixedWidth(90)
            btn.clicked.connect(lambda _checked=False, e=ease: self._pick_color(e))
            self._color_buttons[ease] = btn
            self._apply_swatch(ease)
            grid.addWidget(btn, row, 2)
        layout.addWidget(ease_group)

        appearance = QGroupBox("Appearance")
        form = QFormLayout(appearance)

        self._hold = QSpinBox()
        self._hold.setRange(0, 1000)
        self._hold.setSuffix(" ms")
        self._hold.setValue(int(cfg["hold_ms"]))
        form.addRow("Hold duration", self._hold)

        self._fade = QSpinBox()
        self._fade.setRange(40, 400)
        self._fade.setSuffix(" ms")
        self._fade.setValue(int(cfg["fade_ms"]))
        form.addRow("Fade-out duration", self._fade)

        self._opacity = QDoubleSpinBox()
        self._opacity.setRange(0.0, 0.6)
        self._opacity.setSingleStep(0.01)
        self._opacity.setDecimals(2)
        self._opacity.setValue(float(cfg["target_opacity"]))
        self._opacity.setToolTip(
            "Peak opacity of the flash (capped at 0.60 to limit photosensitivity risk)."
        )
        form.addRow("Opacity", self._opacity)
        layout.addWidget(appearance)

        bb = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
            | QDialogButtonBox.StandardButton.RestoreDefaults
        )
        bb.accepted.connect(self.accept)
        bb.rejected.connect(self.reject)
        bb.button(QDialogButtonBox.StandardButton.RestoreDefaults).clicked.connect(
            self._restore_defaults
        )
        layout.addWidget(bb)

    def _apply_swatch(self, ease: int) -> None:
        hexv = self._colors[ease]
        c = parse_color(hexv, QColor("#ffffff"))
        text_color = "#000000" if c.lightness() > 128 else "#ffffff"
        btn = self._color_buttons[ease]
        btn.setText(c.name())
        btn.setStyleSheet(f"background-color: {c.name()}; color: {text_color};")

    def _pick_color(self, ease: int) -> None:
        initial = parse_color(self._colors[ease], QColor("#ffffff"))
        chosen = QColorDialog.getColor(initial, self, f"{EASE_LABELS[ease]} flash color")
        if chosen.isValid():
            self._colors[ease] = chosen.name()
            self._apply_swatch(ease)

    def _restore_defaults(self) -> None:
        self._master.setChecked(bool(DEFAULT_CONFIG["enabled"]))
        self._hold.setValue(int(DEFAULT_CONFIG["hold_ms"]))
        self._fade.setValue(int(DEFAULT_CONFIG["fade_ms"]))
        self._opacity.setValue(float(DEFAULT_CONFIG["target_opacity"]))
        for ease in VALID_EASES:
            d = DEFAULT_CONFIG["eases"][str(ease)]
            self._enable_boxes[ease].setChecked(bool(d["enabled"]))
            self._colors[ease] = str(d["color"])
            self._apply_swatch(ease)

    def result_config(self) -> Dict[str, Any]:
        return {
            "enabled": self._master.isChecked(),
            "target_opacity": round(float(self._opacity.value()), 3),
            "hold_ms": int(self._hold.value()),
            "fade_ms": int(self._fade.value()),
            "eases": {
                str(e): {
                    "enabled": self._enable_boxes[e].isChecked(),
                    "color": self._colors[e],
                }
                for e in VALID_EASES
            },
        }
