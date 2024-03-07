"""Main entry point to generate gantt chart."""

import argparse
import logging
import sys

from pydantic import ValidationError

from .config import load_global_config
from .report import generate_all_reports


def _create_argument_parser() -> argparse.ArgumentParser:
    """Create the list of arguments supported and return the parser."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Verbose mode",
        dest="verbose",
    )
    parser.add_argument(
        "config",
        action="store",
        help="Configuration file",
        nargs="?",
        metavar="config.yaml",
    )
    return parser


def main() -> None:
    """Entry point of gantt generator script."""
    # Parse command line
    parser = _create_argument_parser()
    args = parser.parse_args()

    log_level = logging.DEBUG if args.verbose else logging.INFO

    # Create logger
    logging.basicConfig(
        stream=sys.stdout,
        format="%(asctime)s - %(levelname)s - %(message)s",
        level=log_level,
    )

    if not args.config:
        parser.print_usage()
        return

    # Get configuration from JSON/YAML file
    try:
        global_config = load_global_config(args.config)
        global_config.update_custom_fields()
    except ValidationError as error:
        sys.exit(str(error))

    logging.getLogger().debug(global_config.json())
    generate_all_reports(global_config)
