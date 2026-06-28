import socket
import threading


class Request:
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
            self.headers[key] = value


class Response:
    def __init__(self, status_code=200, body="", content_type="text/plain"):
        codes = {
            200: "OK",
            201: "Created",
            404: "Not Found",
        }
        self.status = f"{status_code} {codes[status_code]}"
        self.body = body
        self.headers = {"Content-Type": content_type, "Content-Length": len(body)}

    def __bytes__(self):
        return str(self).encode("utf-8")

    def __str__(self):
        temp = f"HTTP/1.1 {self.status}\r\n"
        if self.body:
            for header, value in self.headers.items():
                temp += f"{header}: {value}\r\n"
            temp += "\r\n"
            temp += self.body
        return temp

    def __repr__(self):
        return str(self)


class HttpServer:
    def __init__(self, cli_args, router, host="0.0.0.0", port=8000):
        self.cli_args = cli_args
        self.host = host
        self.port = port
        self.router = router
        self.valid_encodings = ["gzip"]

    def handle_client(self, connection, address):
        data = connection.recv(1024)

        if not data:
            return

        request = Request(data)
        handler, params = self.router.match(request.path)

        compress_response = (
            True if request.headers.get("accept-encoding", None) == "gzip" else False
        )
        if handler:
            response = handler(request, params, self.cli_args)
        else:
            response = Response(status_code=404, body="Not found")

        if compress_response:
            response.headers["Content-Encoding"] = "gzip"
        connection.sendall(bytes(response))
        connection.close()

    def serve_forever(self):
        server_socket = socket.create_server((self.host, self.port), reuse_port=True)

        try:
            while True:
                connection, address = server_socket.accept()
                threading.Thread(
                    target=self.handle_client, args=(connection, address)
                ).start()
        except KeyboardInterrupt:
            print("\nServer is shutting down.")
        finally:
            server_socket.close()
            print("Server has been shut down.")
