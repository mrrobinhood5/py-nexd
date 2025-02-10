import argparse
import socket
import os
import pathlib
import logging


# TODO: add better arg management to allow binding to localhost instead of 0.0.0.0
class Handler:
    def __init__(self, base_path):
        self.base_path = base_path
        self.index_files = ['index']

    def handle(self, req, conn):
        print(f"Request: {req}")
        req = '.' + req
        req_path = os.path.join(self.base_path, req)

        if os.path.isdir(req_path):
            for index_file in self.index_files:
                index_path = os.path.join(req_path, index_file)
                if os.path.exists(index_path):
                    self.serve_file(index_path, conn)
                    return True

            self.list_directory(req_path, conn)
            return True

        return self.serve_file(req_path, conn)

    def serve_file(self, file_path, conn):
        try:
            with open(file_path, 'rb') as f:
                conn.sendall(f.read())
            return True
        except FileNotFoundError:
            conn.sendall(b'document not found\n')
            logging.error(f'File not found: {file_path}')
            return False
        except IsADirectoryError:
            conn.sendall(b'Error: Requested path is a directory\n')
            logging.error(f'Is a directory: {file_path}')
            return False

    def list_directory(self, dir_path, conn):
        try:
            contents = os.listdir(dir_path)
            response = "Directory listing:\n"
            for c in contents:
                response += f'=> {c}\n'
            conn.sendall(response.encode('utf-8'))
        except Exception as e:
            conn.sendall(b'Error reading directory\n')
            logging.error(f'Error reading directory {dir_path}: {e}')


def serve(handler, conn):
    try:
        data = conn.recv(1024).decode('utf-8').strip()
        if data:
            handler.handle(data, conn)
    finally:
        conn.close()


def listen_and_serve(handler, use_ipv6=False):
    address_family = socket.AF_INET6 if use_ipv6 else socket.AF_INET
    with socket.socket(address_family, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        bind_address = ('::', 1900) if use_ipv6 else ('0.0.0.0', 1900)
        s.bind((bind_address))

        s.listen()

        log_address = "[::]" if use_ipv6 else "0.0.0.0"
        logging.info(f"""Server listening on {
                     log_address}:1900 (IPv6: {use_ipv6})""")

        while True:
            conn, addr = s.accept()
            logging.info(f"Connection from {addr}")
            serve(handler, conn)


def main():
    parser = argparse.ArgumentParser(
        description="Unofficial Python port of nexd by m15o")
    parser.add_argument("path", type=pathlib.Path,
                        help="Path of directory to serve")
    parser.add_argument("--ipv6", action="store_true",
                        help="Binds to IPv6 instead")
    args = parser.parse_args()

    if not args.path.exists():
        logging.error(f"Path does not exists: {args.path}")
        exit(1)

    if not args.path.is_dir():
        logging.error(f"Path is not a directory: {args.path}")
        exit(1)

    print("Path:", args.path)
    print("IPv6:", args.ipv6)

    handler = Handler(args.path)
    listen_and_serve(handler, args.ipv6)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
