# main.py
import os
import argparse
import multiprocessing

from dash import (
    Input,
    Output,
    State,
    ctx,
)

from bqc_dash.app import app
from bqc_dash.logger import logger, set_logger_level

# Import callbacks
# Must be imported after app.layout
import bqc_dash.image_display.callbacks  # noqa: E402, F401
import bqc_dash.rejection.callbacks  # noqa: E402, F401
import bqc_dash.scan.callbacks  # noqa: E402, F401
import bqc_dash.performance.callbacks  # noqa: E402, F401
import bqc_dash.checkpoint.callbacks  # noqa: E402, F401
import bqc_dash.help.callbacks  # noqa: E402, F401
import bqc_dash.zoom.callbacks  # noqa: E402, F401
import bqc_dash.toaster.callbacks  # noqa: E402, F401

# Debug keyboard event handling (existing code)
debug_keyboard_event = False
if debug_keyboard_event:

    @app.callback(
        [
            Output("log-store", "data"),
        ],
        [
            Input("keybord-listener", "n_keydowns"),
            Input("keybord-listener", "key_pressed"),
        ],
        [State("keybord-listener", "keydown")],
    )
    def log_keypress(n_keydowns, key_pressed, event):
        """Log keypresses to the store"""
        logger.debug("Start log_keypress")
        logger.debug(f"Key pressed: {key_pressed}")
        active_element = ctx.triggered_id
        logger.debug(f"Active: {active_element}")
        logger.debug(f"Active: {ctx.triggered}")
        logger.debug(f"Event: {event}")
        if n_keydowns:
            # Log the key press
            logger.info(f"Key pressed: {key_pressed}")
            return [None]
        return [None]


def run_dev_server(debug=False, host="0.0.0.0", port=8050, clear_session=False):
    """Run the development server"""
    if debug:
        # Set logger level to DEBUG if debug mode is enabled
        set_logger_level("DEBUG")
    logger.info(f"Starting development server on {host}:{port}")
    app.run(debug=debug, host=host, port=port)


def run_gunicorn_server(host="0.0.0.0", port=8050, workers=None, clear_session=False):
    """Run the Gunicorn production server"""
    try:
        import gunicorn.app.base
    except ImportError:
        logger.error("Gunicorn not installed. Install with: pip install gunicorn")
        return

    if workers is None:
        # Default to number of CPU cores + 1, which is a common best practice
        workers = (multiprocessing.cpu_count() * 2) + 1

    logger.info(f"Starting Gunicorn server on {host}:{port} with {workers} workers")

    class StandaloneApplication(gunicorn.app.base.BaseApplication):
        def __init__(self, app, options=None):
            self.options = options or {}
            self.application = app
            super().__init__()

        def load_config(self):
            for key, value in self.options.items():
                if key in self.cfg.settings and value is not None:
                    self.cfg.set(key.lower(), value)

        def load(self):
            return self.application

    # Get Flask server from Dash app
    server = app.server

    options = {
        "bind": f"{host}:{port}",
        "workers": workers,
        "worker_class": "gevent",
        "timeout": 120,
    }

    StandaloneApplication(server, options).run()


def run_waitress_server(host="0.0.0.0", port=8050, threads=None, clear_session=False):
    """Run the Waitress production server (Windows compatible)"""
    try:
        from waitress import serve
    except ImportError:
        logger.error("Waitress not installed. Install with: pip install waitress")
        return

    if threads is None:
        threads = multiprocessing.cpu_count() * 2

    logger.info(f"Starting Waitress server on {host}:{port} with {threads} threads")

    # Get Flask server from Dash app
    server = app.server
    serve(server, host=host, port=port, threads=threads)


def main():
    """Main entry point with command-line argument parsing"""
    parser = argparse.ArgumentParser(description="BQC Dash Application")
    parser.add_argument(
        "--server",
        choices=["dev", "gunicorn", "waitress"],
        default="dev",
        help="Server to use (default: dev)",
    )
    parser.add_argument(
        "--host", default="0.0.0.0", help="Host to bind to (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port", type=int, default=8050, help="Port to bind to (default: 8050)"
    )
    parser.add_argument(
        "--debug", action="store_true", help="Enable debug mode (dev server only)"
    )
    parser.add_argument("--workers", type=int, help="Number of workers (gunicorn only)")
    parser.add_argument("--threads", type=int, help="Number of threads (waitress only)")

    args = parser.parse_args()

    # Check for environment variables (maintain compatibility with existing code)
    if args.debug is False:  # Only use env var if not explicitly set by args
        args.debug = os.environ.get("BQC_DEBUG", "False").lower() == "true"

    if args.server == "dev":
        run_dev_server(args.debug, args.host, args.port)
    elif args.server == "gunicorn":
        run_gunicorn_server(args.host, args.port, args.workers)
    elif args.server == "waitress":
        run_waitress_server(args.host, args.port, args.threads)


if __name__ == "__main__":
    main()
