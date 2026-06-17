import json
from pathlib import Path

from mgrc_ai_trans.utils.format import MagirecoJSON


def test_example_sources_are_parseable():
    special = json.loads(Path("examples/special_latest.json").read_text(encoding="utf-8"))
    sample_paths = sorted(Path("examples/magireco-source").glob("*.json"))

    assert sample_paths
    for sample_path in sample_paths:
        source = json.loads(sample_path.read_text(encoding="utf-8"))
        src_text = MagirecoJSON(source, special).get_src_text(add_line_number=True)
        assert src_text
