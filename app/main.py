
import socket


def main():
    print("Logs from your program will appear here!")

    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    while True:
        client_socket, client_address = server_socket.accept()  # wait for client
        print(f"client Address: {client_address}")
        response = b"HTTP/1.1 200 OK\r\n\r\n"
        client_socket.sendall(response)
        client_socket.close()


if __name__ == "__main__":
    main()
