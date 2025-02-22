import socket
import threading
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

            client_socket.sendall(b"Press Enter To Start The Game\r\n")
            self.read_initial_data(client_socket)

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
            self.select_or_create_character(client_socket, username)
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

    def select_or_create_character(self, client_socket, username):
        characters = self.db.get_characters(username)
        if characters:
            client_socket.sendall(b"Select a character:\r\n")
            for i, character in enumerate(characters, 1):
                client_socket.sendall(f"{i}. {character['name']} ({character['class']})\r\n".encode())
            client_socket.sendall(b"Enter the number of the character to select or type 'new' to create a new character:\r\n")
            choice = self.read_line(client_socket).lower()
            if choice == 'new':
                self.create_character(client_socket, username)
            else:
                try:
                    choice = int(choice)
                    if 1 <= choice <= len(characters):
                        selected_character = characters[choice - 1]
                        client_socket.sendall(f"Character {selected_character['name']} selected.\r\n".encode())
                        self.current_character = selected_character
                    else:
                        client_socket.sendall(b"Invalid choice. Please try again.\r\n")
                        self.select_or_create_character(client_socket, username)
                except ValueError:
                    client_socket.sendall(b"Invalid choice. Please try again.\r\n")
                    self.select_or_create_character(client_socket, username)
        else:
            self.create_character(client_socket, username)

    def create_character(self, client_socket, username):
        client_socket.sendall(b"Enter character name:\r\n")
        character_name = self.read_line(client_socket)
        client_socket.sendall(b"Choose a class (Warrior, Mage, Holy Man):\r\n")
        character_class = self.read_line(client_socket)
        if character_class in ["Warrior", "Mage", "Holy Man"]:
            self.db.add_character(username, character_name, character_class)
            client_socket.sendall(b"Character created successfully!\r\n")
            self.current_character = {'username': username, 'name': character_name, 'class': character_class}
        else:
            client_socket.sendall(b"Invalid class. Please try again.\r\n")
            self.create_character(client_socket, username)

    def show_help(self, client_socket):
        help_message = (
            "Available commands:\r\n"
            "? - Show this help message\r\n"
            "s - Show character stats\r\n"
            "quit - Quit the game\r\n"
        )
        client_socket.sendall(help_message.encode())

    def show_stats(self, client_socket):
        if hasattr(self, 'current_character'):
            character = self.current_character
            stats_message = (
                f"Character Stats:\r\n"
                f"Name: {character['name']}\r\n"
                f"Class: {character['class']}\r\n"
            )
            client_socket.sendall(stats_message.encode())
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