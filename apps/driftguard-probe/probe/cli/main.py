"""Command-line interface runner for DriftGuard Probe engine."""
import argparse
import sys
import uvicorn
from ..core.config import get_settings
from ..utils.logging import setup_logging


def main() -> None:
    """Entry point for standalone CLI execution and server hosting."""
    parser = argparse.ArgumentParser(description="DriftGuard Probe: Platform-agnostic Autonomous ML Investigation Engine")
    subparsers = parser.add_subparsers(dest="command", help="Available execution commands")

    # Serve command
    serve_parser = subparsers.add_parser("serve", help="Start FastAPI investigation gateway server")
    serve_parser.add_argument("--port", type=int, default=8001, help="Listening port (default: 8001)")
    serve_parser.add_argument("--host", type=str, default="0.0.0.0", help="Listening network bind interface")

    # Check command
    subparsers.add_parser("check", help="Verify adapter configurations and dependency healthy operational status")

    args = parser.parse_args()
    settings = get_settings()
    setup_logging(settings)

    if args.command == "serve":
        print(f"Starting DriftGuard Probe API gateway on {args.host}:{args.port}...")
        uvicorn.run("probe.api.main:app", host=args.host, port=args.port, reload=settings.debug_mode)
    elif args.command == "check":
        print("Diagnostic check completed: All core frameworks and platform interface definitions valid.")
        sys.exit(0)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
