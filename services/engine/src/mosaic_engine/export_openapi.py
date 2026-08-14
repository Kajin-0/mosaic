import argparse
import json
from pathlib import Path

from mosaic_engine.main import app


def export_openapi(target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(app.openapi(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Export Mosaic Engine OpenAPI contract.")
    parser.add_argument("target", type=Path)
    args = parser.parse_args()
    export_openapi(args.target)


if __name__ == "__main__":
    main()
