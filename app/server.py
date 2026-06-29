import socket
import threading
import gzip
import logging

logger = logging.getLogger(__name__)


class Request:
    MULTI_VALUE_KEYS = ["accept-encoding"]
    HTTP11_PROTOCOL = "HTTP/1.1"

    def __init__(self, raw_data: bytes):
        parts = raw_data.decode("utf-8").split("\r\n\r\n")
        self.body = None
        if len(parts) > 1:
            self.body = parts[1]
        data = parts[0].split("\r\n")
        self.method, self.path, self.protocol = data[0].split(" ")
        self.headers = {}
        for header in data[1:]:
            if not header:
                continue
            key, value = header.split(": ")
            key = key.lower()
            if key in Request.MULTI_VALUE_KEYS:
                value = [v.strip() for v in value.split(",")]
            self.headers[key] = value

    @property
    def is_httpv11(self):
        return self.protocol == Request.HTTP11_PROTOCOL

    @property
    def close_connection(self):
        return self.is_httpv11 and self.headers.get("connection", None) == "close"

    @property
    def compress_response(self):
        return True if "gzip" in self.headers.get("accept-encoding", []) else False


class Response:
    def __init__(self, status_code=200, body="", content_type="text/plain"):
        codes = {
            200: "OK",
            201: "Created",
            404: "Not Found",
        }
        self.status = f"{status_code} {codes[status_code]}"
        self._body = body
        self.headers = {"Content-Type": content_type}

    def mark_gzip(self):
        self.headers["Content-Encoding"] = "gzip"

    @property
    def compress(self):
        if self.headers.get("Content-Encoding", None) == "gzip":
            return True
        return False

    @property
    def body(self):
        if self.compress:
            return gzip.compress(self._body.encode())
        return self._body.encode()

    def __bytes__(self):
        response = bytes(f"HTTP/1.1 {self.status}\r\n".encode())
        body = self.body
        if body:
            self.headers["Content-Length"] = len(body)
            for header, value in self.headers.items():
                response += bytes(f"{header}:{value}\r\n".encode())
            response += b"\r\n"
            response += body

        return response

    def __repr__(self):
        return bytes(self)


class HttpServer:
    def __init__(self, cli_args, router, host="0.0.0.0", port=8000):
        self.cli_args = cli_args
        self.host = host
        self.port = port
        self.router = router
        self.valid_encodings = ["gzip"]

    def handle_client(self, connection, address):
        logger.info("Client connected: %s", address)

        data = connection.recv(1024)

        while data:
            request = Request(data)
            logger.info("%s %s", request.method, request.path)

            handler, params = self.router.match(request.path)

            if handler:
                response = handler(request, params, self.cli_args)
            else:
                response = Response(status_code=404, body="Not found")

            if request.compress_response:
                response.mark_gzip()

            logger.info("Response: %s", response.status)
            connection.sendall(bytes(response))

            if request.close_connection:
                logger.info("Closing connection for %s", address)
                connection.close()
            else:
                data = connection.recv(1024)

    def serve_forever(self):
        server_socket = socket.create_server((self.host, self.port), reuse_port=True)
        logger.info("Server listening on %s:%d", self.host, self.port)

        try:
            while True:
                connection, address = server_socket.accept()
                threading.Thread(
                    target=self.handle_client, args=(connection, address)
                ).start()
        except KeyboardInterrupt:
            logger.info("Server is shutting down.")
        finally:
            server_socket.close()
            logger.info("Server has been shut down.")
