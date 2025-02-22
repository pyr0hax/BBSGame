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
        return [{'id': char[0], 'username': char[1], 'name': char[2], 'class': char[3]} for char in characters]

    def add_character(self, username, name, char_class):
        query = "INSERT INTO characters (username, name, class) VALUES (?, ?, ?)"
        self.execute_query(query, (username, name, char_class))