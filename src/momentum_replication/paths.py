"""Central place for folder locations, so scripts work from any directory."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"            # downloaded prices (git-ignored)
UNIVERSE_DIR = ROOT / "universe"    # ticker lists (committed)
RESULTS_DIR = ROOT / "results"      # tables and charts (committed)
