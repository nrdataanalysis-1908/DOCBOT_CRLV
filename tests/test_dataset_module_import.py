import importlib.util
from pathlib import Path


def test_import_does_not_create_input_or_output_directories(tmp_path):
    module_dir = tmp_path / "core" / "robots" / "robots" / "core" / "core"
    module_dir.mkdir(parents=True)
    source = (
        Path(__file__).resolve().parents[1]
        / "core" / "robots" / "robots" / "core" / "core"
        / "dataset_normalization_engine.py"
    )
    copied = module_dir / "dataset_normalization_engine.py"
    copied.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")

    spec = importlib.util.spec_from_file_location("isolated_dataset_engine", copied)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    assert not module.INPUT_DIR.exists()
    assert not module.OUTPUT_DIR.exists()

    module.main()

    assert module.INPUT_DIR.is_dir()
    assert not module.OUTPUT_DIR.exists()
