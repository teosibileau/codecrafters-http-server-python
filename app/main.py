import socket
import threading
import argparse
import os


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
        self.content_type = content_type

    def __bytes__(self):
        return str(self).encode("utf-8")

    def __str__(self):
        temp = f"HTTP/1.1 {self.status}\r\n"
        if self.body:
            temp += f"Content-Type: {self.content_type}\r\n"
            temp += f"Content-Length: {len(self.body)}\r\n"
            temp += "\r\n"
            temp += self.body
        return temp

    def __repr__(self):
        return str(self)


def handle_client(connection, address, cli_args):
    print(f"client Address: {address}")
    data = connection.recv(1024)
    if not data:
        return
    request = Request(data)

    if request.path == "/":
        response = Response(body="Hello World")
    elif request.path == "/user-agent":
        response = Response(body=request.headers.get("user-agent", ""))
    elif request.path.startswith("/echo/"):
        response = Response(body=request.path.split("/echo/")[1])
    elif request.path.startswith("/files/"):
        if request.method == "GET":
            files = os.listdir(cli_args.directory)
            file_to_retrieve = request.path.split("/files/")[1]
            if file_to_retrieve in files:
                file_path = cli_args.directory + file_to_retrieve
                with open(file_path, "r") as file:
                    response = Response(
                        body=file.read(), content_type="application/octet-stream"
                    )
            else:
                response = Response(status_code=404, body="Not found")
        elif request.method == "POST":
            file_to_save = request.path.split("/files/")[1]
            file_path = cli_args.directory + file_to_save
            with open(file_path, "w+") as file:
                file.write(request.body)
            response = Response(body="File saved", status_code=201)
    else:
        response = Response(status_code=404, body="Not found")
    connection.sendall(bytes(response))
    connection.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", default="/tmp/")
    cli_args = parser.parse_args()

    print("Logs from your program will appear here!")

    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)

    try:
        while True:
            connection, address = server_socket.accept()
            threading.Thread(
                target=handle_client, args=(connection, address, cli_args)
            ).start()
    except KeyboardInterrupt:
        print("\nServer is shutting down.")
    finally:
        server_socket.close()
        print("Server has been shut down.")


if __name__ == "__main__":
    main()
