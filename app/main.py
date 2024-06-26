
import socket


class Request:
    def __init__(self, data: bytes):
        data = data.decode("utf-8").split("\r\n")
        self.method, self.path, self.protocol = data[0].split(" ")
        self.headers = {
        }
        for header in data[1:]:
            if not header:
                continue
            key, value = header.split(": ")
            key = key.lower()
            self.headers[key] = value


class Response:
    def __init__(self, status_code=200, body=""):
        codes = {
            200: "OK",
            404: "Not Found",
        }
        self.status = f"{status_code} {codes[status_code]}"
        self.body = body

    def __bytes__(self):
        return str(self).encode("utf-8")

    def __str__(self):
        temp = f"HTTP/1.1 {self.status}\r\n"
        if self.body:
            temp += "Content-Type: text/plain\r\n"
            temp += f"Content-Length: {len(self.body)}\r\n"
            temp += "\r\n"
            temp += self.body
        return temp

    def __repr__(self):
        return str(self)


def main():
    print("Logs from your program will appear here!")

    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)

    try:
        while True:
            connection, address = server_socket.accept()
            print(f"client Address: {address}")
            data = connection.recv(1024)
            if not data:
                break
            request = Request(data)

            if request.path == "/":
                response = Response(body="Hello World")
            elif request.path == "/user-agent":
                response = Response(body=request.headers.get("user-agent", ""))
            elif request.path.startswith("/echo/"):
                response = Response(body=request.path.split("/echo/")[1])
            else:
                response = Response(status_code=404, body="Not found")
            connection.sendall(bytes(response))
            connection.close()
    except KeyboardInterrupt:
        print("\nServer is shutting down.")
    finally:
        server_socket.close()
        print("Server has been shut down.")


if __name__ == "__main__":
    main()
