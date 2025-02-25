import socket
import threading
from game import Game
from database import Database

class TelnetServer:
    def __init__(self, db):
        self.db = db
        self.host = '0.0.0.0'
        self.port = 23
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"Telnet server started on {self.host}:{self.port}")

    def handle_client(self, client_socket):
        try:
            client_socket.sendall(b"\xff\xfb\x01" + b"\xff\xfb\x03" + b"\xff\xfd\x03")
            client_socket.sendall(b"\xff\xfb\x22" + b"\xff\xfd\x22")

            client_socket.sendall(b"\r\n\r\n")
            client_socket.sendall(b"Welcome to the MUD game!\r\n")
            client_socket.sendall(b"Type 'login' to log in or 'register' to create a new account:\r\n")

            while True:
                choice = self.read_line(client_socket).lower()
                if choice == 'login':
                    self.login(client_socket)
                    break
                elif choice == 'register':
                    self.register(client_socket)
                    break
                else:
                    client_socket.sendall(b"Invalid choice. Please type 'login' or 'register':\r\n")

            while True:
                client_socket.sendall(b"> ")
                command = self.read_line(client_socket)
                print(f"Command received: {command}")
                if command.lower() == 'quit':
                    client_socket.sendall(b"Goodbye!\r\n")
                    break
                elif command.lower() == '?':
                    self.show_help(client_socket)
                elif command.lower() == 's':
                    self.show_stats(client_socket)
                else:
                    client_socket.sendall(b"Unknown command.\r\n")

        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            client_socket.close()

    def read_initial_data(self, client_socket):
        while True:
            data = client_socket.recv(1024)
            if not data.startswith(b'\xff'):
                break

    def login(self, client_socket):
        client_socket.sendall(b"Username:\r\n")
        username = self.read_line(client_socket)
        client_socket.sendall(b"Password:\r\n")
        password = self.read_line(client_socket)

        user = self.db.get_user(username)
        if user and user['password'] == password:
            client_socket.sendall(b"Login successful! Welcome back!\r\n")
            self.game = Game(self.db, client_socket, username)
            self.game.select_or_create_character()
        else:
            client_socket.sendall(b"Invalid username or password. Please try again.\r\n")
            self.login(client_socket)

    def register(self, client_socket):
        client_socket.sendall(b"Username:\r\n")
        username = self.read_line(client_socket)
        client_socket.sendall(b"Password:\r\n")
        password = self.read_line(client_socket)
        client_socket.sendall(b"Sex (M/F):\r\n")
        sex = self.read_line(client_socket)
        client_socket.sendall(b"Age:\r\n")
        age = self.read_line(client_socket)

        if self.db.get_user(username):
            client_socket.sendall(b"Username already exists. Please try again.\r\n")
            self.register(client_socket)
        else:
            self.db.add_user(username, password, sex, age)
            client_socket.sendall(b"Registration successful! You can now log in.\r\n")
            self.login(client_socket)

    def show_help(self, client_socket):
        help_message = (
            "Available commands:\r\n"
            "? - Show this help message\r\n"
            "s - Show character stats\r\n"
            "quit - Quit the game\r\n"
        )
        client_socket.sendall(help_message.encode())

    def show_stats(self, client_socket):
        if hasattr(self, 'game') and self.game.current_character:
            self.game.show_stats()
        else:
            client_socket.sendall(b"No character selected.\r\n")

    def read_line(self, client_socket):
        buffer = b""
        while True:
            data = client_socket.recv(1024)
            buffer += data
            if b"\r\n" in buffer:
                break
        return buffer.decode(errors='ignore').strip()

    def start(self):
        while True:
            client_socket, addr = self.server_socket.accept()
            print(f"Connection from {addr}")
            client_handler = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_handler.start()

if __name__ == "__main__":
    db = Database("game.db")
    server = TelnetServer(db)
    server.start()