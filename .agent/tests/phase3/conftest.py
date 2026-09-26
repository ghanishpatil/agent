from __future__ import annotations

import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Callable, Iterator

import pytest


class _RoutedHandler(BaseHTTPRequestHandler):
    routes: dict[str, Callable[["_RoutedHandler"], None]] = {}

    def log_message(self, format: str, *args: object) -> None:  # noqa: A002 - stdlib signature
        return None

    def do_GET(self) -> None:  # noqa: N802 - stdlib method name
        self._dispatch()

    def do_POST(self) -> None:  # noqa: N802 - stdlib method name
        self._dispatch()

    def _dispatch(self) -> None:
        handler = type(self).routes.get(self.path)
        if handler is None:
            self.send_response(404)
            self.end_headers()
            return
        handler(self)


@pytest.fixture
def local_http_server() -> Iterator[tuple[str, dict[str, Callable[[_RoutedHandler], None]]]]:
    """Starts a real local HTTP server on 127.0.0.1 with a caller-populated route table.

    This is used only to validate the ``HttpAdapter`` boundary against a controlled, local,
    synthetic target. It never contacts a third-party host.
    """
    routes: dict[str, Callable[[_RoutedHandler], None]] = {}
    handler_cls = type("RoutedHandler", (_RoutedHandler,), {"routes": routes})
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler_cls)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    host, port = server.server_address
    try:
        yield f"http://{host}:{port}", routes
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
