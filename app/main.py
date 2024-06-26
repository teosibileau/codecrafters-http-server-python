
import socket

HTTP_200 = b"HTTP/1.1 200 OK\r\n\r\n"
HTTP_404 = b"HTTP/1.1 404 Not Found\r\n\r\n"

def main():
    print("Logs from your program will appear here!")

    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)

    while True:
        connection, address = server_socket.accept()
        print(f"client Address: {address}")
        data = connection.recv(1024)
        request_data = data.decode("utf-8").split("\r\n")
        if not data:
            break
        path = request_data[0].split(" ")[1]
        if path == "/":
            connection.sendall(HTTP_200)
        else:
            connection.sendall(HTTP_404)
        connection.close()


if __name__ == "__main__":
    main()
