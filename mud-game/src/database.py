import sqlite3
from sqlite3 import Error

class Database:
    def __init__(self, db_file):
        self.db_file = db_file
        self.create_tables()

    def create_connection(self):
        connection = None
        try:
            connection = sqlite3.connect(self.db_file)
            print("Connection to SQLite DB successful")
        except Error as e:
            print(f"The error '{e}' occurred")

        return connection

    def create_tables(self):
        create_users_table = """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            sex TEXT NOT NULL,
            age INTEGER NOT NULL
        );
        """
        create_characters_table = """
        CREATE TABLE IF NOT EXISTS characters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            name TEXT NOT NULL,
            class TEXT NOT NULL,
            level INTEGER NOT NULL,
            xp INTEGER NOT NULL,
            skill_points INTEGER NOT NULL,
            strength INTEGER NOT NULL,
            dexterity INTEGER NOT NULL,
            constitution INTEGER NOT NULL,
            intelligence INTEGER NOT NULL,
            wisdom INTEGER NOT NULL,
            charisma INTEGER NOT NULL,
            FOREIGN KEY (username) REFERENCES users (username)
        );
        """
        self.execute_query(create_users_table)
        self.execute_query(create_characters_table)

    def execute_query(self, query, params=()):
        connection = self.create_connection()
        cursor = connection.cursor()
        try:
            cursor.execute(query, params)
            connection.commit()
            print("Query executed successfully")
        except Error as e:
            print(f"The error '{e}' occurred")
        finally:
            connection.close()

    def get_user(self, username):
        connection = self.create_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        connection.close()
        if user:
            return {
                'id': user[0],
                'username': user[1],
                'password': user[2],
                'sex': user[3],
                'age': user[4]
            }
        return None

    def add_user(self, username, password, sex, age):
        query = "INSERT INTO users (username, password, sex, age) VALUES (?, ?, ?, ?)"
        self.execute_query(query, (username, password, sex, age))

    def get_characters(self, username):
        connection = self.create_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM characters WHERE username = ?", (username,))
        characters = cursor.fetchall()
        connection.close()
        return [{'id': char[0], 'username': char[1], 'name': char[2], 'class': char[3], 'level': char[4], 'xp': char[5], 'skill_points': char[6], 'strength': char[7], 'dexterity': char[8], 'constitution': char[9], 'intelligence': char[10], 'wisdom': char[11], 'charisma': char[12]} for char in characters]

    def add_character(self, username, name, char_class, stats):
        query = "INSERT INTO characters (username, name, class, level, xp, skill_points, strength, dexterity, constitution, intelligence, wisdom, charisma) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        self.execute_query(query, (username, name, char_class, 1, 0, 0, stats['Strength'], stats['Dexterity'], stats['Constitution'], stats['Intelligence'], stats['Wisdom'], stats['Charisma']))

    def update_character(self, character):
        query = """
            UPDATE characters
            SET level = ?, xp = ?, skill_points = ?, strength = ?, dexterity = ?, constitution = ?, intelligence = ?, wisdom = ?, charisma = ?
            WHERE id = ?
        """
        self.execute_query(query, (character['level'], character['xp'], character['skill_points'], character['strength'], character['dexterity'], character['constitution'], character['intelligence'], character['wisdom'], character['charisma'], character['id']))