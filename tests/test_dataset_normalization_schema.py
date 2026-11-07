import importlib.util
from pathlib import Path

import pandas as pd
import pytest

MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "core" / "robots" / "robots" / "core" / "core"
    / "dataset_normalization_engine.py"
)
SPEC = importlib.util.spec_from_file_location("dataset_normalization_schema", MODULE_PATH)
engine = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(engine)


@pytest.mark.parametrize(
    "columns",
    [
        ["Placa", " Placa "],
        ["Título", "Placa"],
    ],
)
def test_tratar_arquivo_rejects_duplicate_columns_after_normalization(
    tmp_path, monkeypatch, columns
):
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()
    source = input_dir / "source.xlsx"
    source.write_text("placeholder", encoding="utf-8")
    frame = pd.DataFrame([["ABC1234", "XYZ9876"]], columns=columns)

    monkeypatch.setattr(engine, "INPUT_DIR", input_dir)
    monkeypatch.setattr(engine, "OUTPUT_DIR", output_dir)
    monkeypatch.setattr(engine.pd, "read_excel", lambda *args, **kwargs: frame.copy())

    with pytest.raises(ValueError, match="duplicadas"):
        engine.tratar_arquivo(source)

    assert not output_dir.exists()
