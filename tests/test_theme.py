"""The code's tokens match DESIGN.md, the design system's source of truth."""
import re
from pathlib import Path

from nodus.theme import COLORS


def test_theme_colors_match_design_md():
    front = Path("DESIGN.md").read_text().split("---")[1]
    block = front.split("colors:")[1].split("typography:")[0]
    declared = dict(re.findall(r'^\s+([\w-]+):\s+"(#[0-9A-Fa-f]{6})"', block, re.M))
    assert {k: v.upper() for k, v in declared.items()} == {k: v.upper() for k, v in COLORS.items()}
