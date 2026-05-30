from __future__ import annotations

from typing import Any

from aqt import gui_hooks, mw
from aqt.qt import QDialog

from .core import normalize_config
from .dialog import ConfigDialog
from .manager import get_manager, on_reviewer_did_answer_card


def _open_config(*_args: Any) -> None:
    cfg = normalize_config(mw.addonManager.getConfig(__name__))
    dlg = ConfigDialog(mw, cfg)
    if dlg.exec() == QDialog.DialogCode.Accepted:
        mw.addonManager.writeConfig(__name__, dlg.result_config())
        mgr = get_manager()
        if mgr is not None:
            mgr.reload_config()


gui_hooks.reviewer_did_answer_card.append(on_reviewer_did_answer_card)
mw.addonManager.setConfigAction(__name__, _open_config)
