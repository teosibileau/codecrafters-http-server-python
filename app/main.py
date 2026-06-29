import socket
import threading
import argparse
import os
import logging

from .server import Request, Response, HttpServer
from .router import Router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


def home_handler(request, params, cli_args):
    return Response(body="Hello World")


def user_agent_handler(request, params, cli_args):
    return Response(body=request.headers.get("user-agent", ""))


def echo_handler(request, params, cli_args):
    return Response(body=params["message"])


def files_handler(request, params, cli_args):
    files_directory = cli_args.directory
    if request.method == "GET":
        files = os.listdir(files_directory)
        file_to_retrieve = request.path.split("/files/")[1]
        if not file_to_retrieve in files:
            return Response(status_code=404, body="Not found")
        if file_to_retrieve in files:
            file_path = cli_args.directory + file_to_retrieve
            with open(file_path, "r") as file:
                return Response(
                    body=file.read(), content_type="application/octet-stream"
                )
        return Response(status_code=404, body="Not found")
    if request.method == "POST":
        file_to_save = request.path.split("/files/")[1]
        file_path = files_directory + file_to_save
        with open(file_path, "w+") as file:
            file.write(request.body)
        return Response(body="File saved", status_code=201)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", default="/tmp/")
    cli_args = parser.parse_args()
    router = Router()

    router.exact("/", home_handler)
    router.exact("/user-agent", user_agent_handler)
    router.prefix("/echo/", echo_handler, param="message")
    router.prefix("/files/", files_handler, param="file_name")

    server = HttpServer(cli_args, router, "localhost", 4221)
    server.serve_forever()


if __name__ == "__main__":
    main()
