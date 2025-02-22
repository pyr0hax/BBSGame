import mysql.connector

class Database:
    def __init__(self):
        self.connection = None

    def connect(self):
        self.connection = mysql.connector.connect(
            host="localhost",
            user="yourusername",
            password="yourpassword",
            database="mudgame"
        )
        self.cursor = self.connection.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(255) UNIQUE NOT NULL,
                class VARCHAR(255) NOT NULL,
                level INT DEFAULT 1,
                health INT DEFAULT 100,
                mana INT DEFAULT 100,
                strength INT DEFAULT 10,
                intelligence INT DEFAULT 10,
                dexterity INT DEFAULT 10
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS items (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                type VARCHAR(255) NOT NULL,
                effect VARCHAR(255) NOT NULL
            )
        """)
        self.connection.commit()

    def get_user(self, username):
        self.cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        return self.cursor.fetchone()

    def create_user(self, username, user_class):
        if user_class == "Warrior":
            health, mana, strength, intelligence, dexterity = 150, 50, 15, 5, 10
        elif user_class == "Mage":
            health, mana, strength, intelligence, dexterity = 80, 150, 5, 15, 10
        elif user_class == "Holy Man":
            health, mana, strength, intelligence, dexterity = 100, 100, 10, 10, 10

        self.cursor.execute("""
            INSERT INTO users (username, class, health, mana, strength, intelligence, dexterity)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (username, user_class, health, mana, strength, intelligence, dexterity))
        self.connection.commit()