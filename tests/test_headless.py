import importlib.util
import sys
import types
from pathlib import Path

import pytest


ROOT_DIR = Path(__file__).resolve().parents[1]
HAS_H5PY = importlib.util.find_spec("h5py") is not None
HAS_FLASK = importlib.util.find_spec("flask") is not None
HAS_CELERY = importlib.util.find_spec("celery") is not None
HAS_SEABORN = importlib.util.find_spec("seaborn") is not None
HAS_SKLEARN = importlib.util.find_spec("sklearn") is not None
HAS_DYTHON = importlib.util.find_spec("dython") is not None
HAS_OPENPYXL = importlib.util.find_spec("openpyxl") is not None

if not HAS_H5PY:
    h5py_stub = types.ModuleType("h5py")

    class _H5StubError(RuntimeError):
        pass

    class _H5StubType:
        pass

    def _stub_file(*args, **kwargs):
        raise _H5StubError("h5py is not installed")

    h5py_stub.File = _stub_file
    h5py_stub.Group = _H5StubType
    h5py_stub.Dataset = _H5StubType
    sys.modules["h5py"] = h5py_stub

if not HAS_FLASK:
    flask_stub = types.ModuleType("flask")

    class _FlaskStubError(RuntimeError):
        pass

    def _stub_unavailable(*args, **kwargs):
        raise _FlaskStubError("flask is not installed")

    flask_stub.current_app = None
    flask_stub.session = {}
    flask_stub.Flask = _stub_unavailable
    sys.modules["flask"] = flask_stub

if not HAS_CELERY:
    celery_stub = types.ModuleType("celery")
    celery_exceptions_stub = types.ModuleType("celery.exceptions")

    class Task:
        pass

    class SoftTimeLimitExceeded(Exception):
        pass

    def shared_task(*args, **kwargs):
        def decorator(func):
            def wrapper(*w_args, **w_kwargs):
                return func(*w_args, **w_kwargs)

            wrapper.__wrapped__ = func
            return wrapper

        return decorator

    celery_stub.Task = Task
    celery_stub.shared_task = shared_task
    celery_exceptions_stub.SoftTimeLimitExceeded = SoftTimeLimitExceeded
    sys.modules["celery"] = celery_stub
    sys.modules["celery.exceptions"] = celery_exceptions_stub

if not HAS_SEABORN:
    seaborn_stub = types.ModuleType("seaborn")

    def _no_seaborn(*args, **kwargs):
        raise RuntimeError("seaborn is not installed")

    seaborn_stub.heatmap = _no_seaborn
    seaborn_stub.set = _no_seaborn
    sys.modules["seaborn"] = seaborn_stub

if not HAS_SKLEARN:
    sklearn_stub = types.ModuleType("sklearn")
    sklearn_preprocessing_stub = types.ModuleType("sklearn.preprocessing")

    class LabelEncoder:
        def fit_transform(self, values):
            raise RuntimeError("sklearn is not installed")

    sklearn_preprocessing_stub.LabelEncoder = LabelEncoder
    sys.modules["sklearn"] = sklearn_stub
    sys.modules["sklearn.preprocessing"] = sklearn_preprocessing_stub

if not HAS_DYTHON:
    dython_stub = types.ModuleType("dython")
    dython_nominal_stub = types.ModuleType("dython.nominal")

    def associations(*args, **kwargs):
        raise RuntimeError("dython is not installed")

    dython_nominal_stub.associations = associations
    sys.modules["dython"] = dython_stub
    sys.modules["dython.nominal"] = dython_nominal_stub


def _ensure_package(name: str, package_path: Path) -> types.ModuleType:
    module = sys.modules.get(name)
    if module is None:
        module = types.ModuleType(name)
        module.__path__ = [str(package_path)]
        sys.modules[name] = module
    return module


def _load_module(name: str, relative_path: str, package: str | None = None):
    module_path = ROOT_DIR / relative_path
    spec = importlib.util.spec_from_file_location(name, module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module: {module_path}")
    module = importlib.util.module_from_spec(spec)
    if package:
        module.__package__ = package
    spec.loader.exec_module(module)
    return module


_ensure_package("aidrin", ROOT_DIR / "aidrin")
_ensure_package("aidrin.headless", ROOT_DIR / "aidrin" / "headless")

_api = _load_module(
    "aidrin.headless.api", "aidrin/headless/api.py", package="aidrin.headless"
)

run_batch_metrics = _api.run_batch_metrics
run_metric = _api.run_metric
HeadlessConfig = _api.HeadlessConfig


TEST_DATA_DIR = ROOT_DIR / "aidrin" / "static" / "datasets" / "test_data"


@pytest.mark.parametrize(
    "relative_path",
    [
        Path("csv/adult.csv"),
        Path("csv/smallSample.csv"),
        Path("json/adult.json"),
        Path("json/employees.json"),
        pytest.param(
            Path("xlsx/adult.xlsx"),
            marks=pytest.mark.skipif(
                not HAS_OPENPYXL, reason="openpyxl not installed"
            ),
        ),
        pytest.param(
            Path("xlsx/smallSample.xlsx"),
            marks=pytest.mark.skipif(
                not HAS_OPENPYXL, reason="openpyxl not installed"
            ),
        ),
        Path("npz/adult.npz"),
        pytest.param(
            Path("h5/adult.h5"),
            marks=pytest.mark.skipif(not HAS_H5PY, reason="h5py not installed"),
        ),
        pytest.param(
            Path("h5/employees.h5"),
            marks=pytest.mark.skipif(not HAS_H5PY, reason="h5py not installed"),
        ),
        Path("dcat/BUTTER-E.json"),
        Path("dcat/EGS_Collab_Experiment.json"),
    ],
)
def test_headless_completeness_runs_on_test_data(relative_path):
    file_path = TEST_DATA_DIR / relative_path
    assert file_path.exists()

    result = run_metric("completeness", str(file_path), save_images=False)

    assert isinstance(result, dict)
    assert "Completeness scores" in result
    assert "Overall Completeness" in result


def test_headless_batch_metrics_on_adult_csv():
    file_path = TEST_DATA_DIR / "csv" / "adult.csv"
    config = HeadlessConfig(
        file_path=str(file_path),
        metrics=["completeness", "duplicity", "outliers"],
        save_images=False,
    )

    results = run_batch_metrics(config)

    assert set(results.keys()) == {"completeness", "duplicity", "outliers"}
    assert "Completeness scores" in results["completeness"]
    assert "Duplicity scores" in results["duplicity"]
    assert "Outlier scores" in results["outliers"]
