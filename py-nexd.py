import socket
import os
import logging

class Handler:
    def __init__(self, base_path):
        self.base_path = base_path
        self.index_files = ['index']

    def handle(self, req, conn):
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

def listen_and_serve(handler):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('0.0.0.0', 1900))
        s.listen()

        logging.info("Server listening on port 1900")

        while True:
            conn, addr = s.accept()
            logging.info(f"Connection from {addr}")
            serve(handler, conn)


def main():
    # TODO: add better arg management to allow binding to localhost instead of 0.0.0.0
    if len(os.sys.argv) < 2:
        logging.info("usage: python3 script.py path")
        logging.info("No path provided, serving $PWD")
        base_path = os.getcwd()
    else:
        base_path = os.sys.argv[1]

    handler = Handler(base_path)
    listen_and_serve(handler)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
