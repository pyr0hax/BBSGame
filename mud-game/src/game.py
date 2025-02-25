import random

class Game:
    def __init__(self, db, client_socket, username):
        self.db = db
        self.client_socket = client_socket
        self.username = username
        self.current_character = None

    def select_or_create_character(self):
        characters = self.db.get_characters(self.username)
        if characters:
            self.client_socket.sendall(b"Select a character:\r\n")
            for i, character in enumerate(characters, 1):
                self.client_socket.sendall(f"{i}. {character['name']} ({character['class']})\r\n".encode())
            self.client_socket.sendall(b"Enter the number of the character to select or type 'new' to create a new character:\r\n")
            choice = self.read_line().lower()
            if choice == 'new':
                self.create_character()
            else:
                try:
                    choice = int(choice)
                    if 1 <= choice <= len(characters):
                        selected_character = characters[choice - 1]
                        self.client_socket.sendall(f"Character {selected_character['name']} selected.\r\n".encode())
                        self.current_character = selected_character
                    else:
                        self.client_socket.sendall(b"Invalid choice. Please try again.\r\n")
                        self.select_or_create_character()
                except ValueError:
                    self.client_socket.sendall(b"Invalid choice. Please try again.\r\n")
                    self.select_or_create_character()
        else:
            self.create_character()

    def create_character(self):
        self.client_socket.sendall(b"Enter character name:\r\n")
        character_name = self.read_line()
        self.client_socket.sendall(b"Choose a class (Warrior, Mage, Holy Man):\r\n")
        character_class = self.read_line()
        if character_class in ["Warrior", "Mage", "Holy Man"]:
            self.client_socket.sendall(b"Do you want to select the character stats manually or let the game roll the stats? (type 'manual' or 'roll'):\r\n")
            choice = self.read_line().lower()
            if choice == 'manual':
                stats = self.manual_stats()
            elif choice == 'roll':
                stats = self.roll_stats()
            else:
                self.client_socket.sendall(b"Invalid choice. Please try again.\r\n")
                self.create_character()
                return

            self.db.add_character(self.username, character_name, character_class, stats)
            self.client_socket.sendall(b"Character created successfully!\r\n")
            self.current_character = {'username': self.username, 'name': character_name, 'class': character_class, 'stats': stats}
        else:
            self.client_socket.sendall(b"Invalid class. Please try again.\r\n")
            self.create_character()

    def manual_stats(self):
        stats = {}
        for stat in ["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"]:
            self.client_socket.sendall(f"Enter {stat} (1-20):\r\n".encode())
            while True:
                value = self.read_line()
                try:
                    value = int(value)
                    if 1 <= value <= 20:
                        stats[stat] = value
                        break
                    else:
                        self.client_socket.sendall(f"Invalid value for {stat}. Please enter a number between 1 and 20:\r\n".encode())
                except ValueError:
                    self.client_socket.sendall(f"Invalid value for {stat}. Please enter a number between 1 and 20:\r\n".encode())
        return stats

    def roll_stats(self):
        stats = {}
        for stat in ["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"]:
            rolls = sorted([random.randint(1, 6) for _ in range(4)], reverse=True)
            stats[stat] = sum(rolls[:3])
        return stats

    def show_stats(self):
        if self.current_character:
            character = self.current_character
            stats_message = (
                f"Character Stats:\r\n"
                f"Name: {character['name']}\r\n"
                f"Class: {character['class']}\r\n"
                f"Strength: {character['stats']['Strength']}\r\n"
                f"Dexterity: {character['stats']['Dexterity']}\r\n"
                f"Constitution: {character['stats']['Constitution']}\r\n"
                f"Intelligence: {character['stats']['Intelligence']}\r\n"
                f"Wisdom: {character['stats']['Wisdom']}\r\n"
                f"Charisma: {character['stats']['Charisma']}\r\n"
            )
            self.client_socket.sendall(stats_message.encode())
        else:
            self.client_socket.sendall(b"No character selected.\r\n")

    def read_line(self):
        buffer = b""
        while True:
            data = self.client_socket.recv(1024)
            buffer += data
            if b"\r\n" in buffer:
                break
        return buffer.decode(errors='ignore').strip()