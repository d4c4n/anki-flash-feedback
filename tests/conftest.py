import sys
from pathlib import Path

# Allow `import core` to resolve to src/anki_flash_feedback/core.py
sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "anki_flash_feedback"))
