import importlib.util
from pathlib import Path

import pandas as pd
import pytest

MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "core" / "robots" / "robots" / "core" / "core"
    / "dataset_normalization_engine.py"
)
SPEC = importlib.util.spec_from_file_location("dataset_normalization_atomic", MODULE_PATH)
engine = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(engine)


def test_failed_excel_export_preserves_previous_output(tmp_path, monkeypatch):
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()
    output_dir.mkdir()
    source = input_dir / "source.xlsx"
    source.write_text("placeholder", encoding="utf-8")
    destination = output_dir / "NORMALIZADO_source.xlsx"
    destination.write_bytes(b"previous-valid-output")
    frame = pd.DataFrame({"Placa": ["ABC1234"], "UF Cliente": ["MG"]})

    monkeypatch.setattr(engine, "INPUT_DIR", input_dir)
    monkeypatch.setattr(engine, "OUTPUT_DIR", output_dir)
    monkeypatch.setattr(engine.pd, "read_excel", lambda *args, **kwargs: frame.copy())

    def fail_after_partial_write(self, path, **kwargs):
        Path(path).write_bytes(b"partial")
        raise OSError("simulated disk failure")

    monkeypatch.setattr(pd.DataFrame, "to_excel", fail_after_partial_write)

    with pytest.raises(OSError, match="simulated disk failure"):
        engine.tratar_arquivo(source)

    assert destination.read_bytes() == b"previous-valid-output"
    assert list(output_dir.glob("*.tmp.xlsx")) == []
