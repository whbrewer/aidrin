import argparse
import json
import sys
from typing import List, Optional

from .api import list_available_metrics, run_batch_metrics, run_metric
from .config import HeadlessConfig


def _parse_list(value: Optional[str]) -> Optional[List[str]]:
    if value is None:
        return None
    items = [item.strip() for item in value.split(",") if item.strip()]
    return items or None


def _dump_result(result: object) -> None:
    sys.stdout.write(json.dumps(result, indent=2))
    sys.stdout.write("\n")


def _build_run_kwargs(args: argparse.Namespace) -> dict:
    return {
        "columns": _parse_list(args.columns),
        "target_column": args.target_column,
        "quasi_identifiers": _parse_list(args.quasi_identifiers),
        "sensitive_column": args.sensitive_column,
        "epsilon": args.epsilon,
        "id_column": args.id_column,
        "eval_columns": _parse_list(args.eval_columns),
        "distance_metric": args.distance_metric,
        "cat_columns": _parse_list(args.cat_columns),
        "num_columns": _parse_list(args.num_columns),
        "y_true_column": args.y_true_column,
        "sensitive_attribute_column": args.sensitive_attribute_column,
        "save_images": args.save_images,
        "image_dir": args.image_dir,
    }


def _configure_common_run_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--file-type", dest="file_type", default=None)
    parser.add_argument("--columns", default=None, help="Comma-separated column list")
    parser.add_argument("--target-column", default=None)
    parser.add_argument("--quasi-identifiers", default=None)
    parser.add_argument("--sensitive-column", default=None)
    parser.add_argument("--epsilon", type=float, default=None)
    parser.add_argument("--id-column", default=None)
    parser.add_argument("--eval-columns", default=None)
    parser.add_argument("--distance-metric", default=None)
    parser.add_argument("--cat-columns", default=None)
    parser.add_argument("--num-columns", default=None)
    parser.add_argument("--y-true-column", default=None)
    parser.add_argument("--sensitive-attribute-column", default=None)
    parser.add_argument("--save-images", dest="save_images", action="store_true")
    parser.add_argument("--no-save-images", dest="save_images", action="store_false")
    parser.set_defaults(save_images=True)
    parser.add_argument("--image-dir", default=None)


def main() -> None:
    parser = argparse.ArgumentParser(prog="aidrin")
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list", help="List available metrics")
    list_parser.add_argument("--category", default=None)

    run_parser = subparsers.add_parser("run", help="Run a single metric")
    run_parser.add_argument("metric")
    run_parser.add_argument("file_path")
    _configure_common_run_args(run_parser)

    batch_parser = subparsers.add_parser("batch", help="Run metrics from config JSON")
    batch_parser.add_argument("config_path")

    args = parser.parse_args()

    try:
        if args.command == "list":
            _dump_result(list_available_metrics(category=args.category))
            return

        if args.command == "run":
            result = run_metric(
                args.metric,
                args.file_path,
                file_type=args.file_type,
                **_build_run_kwargs(args),
            )
            _dump_result(result)
            return

        if args.command == "batch":
            config = HeadlessConfig.from_json_file(args.config_path)
            result = run_batch_metrics(config)
            _dump_result(result)
            return
    except Exception as exc:
        sys.stderr.write(f"Error: {exc}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
