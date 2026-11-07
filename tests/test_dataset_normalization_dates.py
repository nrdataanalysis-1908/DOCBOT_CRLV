import importlib.util
from pathlib import Path

import pandas as pd

MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "core" / "robots" / "robots" / "core" / "core"
    / "dataset_normalization_engine.py"
)
SPEC = importlib.util.spec_from_file_location("dataset_normalization_engine", MODULE_PATH)
engine = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(engine)


def test_normalizar_data_handles_brazilian_and_iso_dates():
    values = pd.Series(["31/01/2026", "2026-02-03", "01/02/2026", "invalid"])

    result = engine.normalizar_data(values)

    assert result.fillna("").tolist() == [
        "31/01/2026",
        "03/02/2026",
        "01/02/2026",
        "",
    ]


def test_listar_xlsx_is_deterministic_and_ignores_lock_files(tmp_path, monkeypatch):
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    older = input_dir / "a.xlsx"
    newer = input_dir / "b.xlsx"
    lock = input_dir / "~$locked.xlsx"
    other = input_dir / "notes.csv"
    for path in (older, newer, lock, other):
        path.write_text("placeholder", encoding="utf-8")
    older.touch()
    newer.touch()
    lock.touch()

    monkeypatch.setattr(engine, "INPUT_DIR", input_dir)

    assert engine.listar_xlsx() == [older, newer]
    assert engine.escolher_mais_recente([older, newer]) == newer
