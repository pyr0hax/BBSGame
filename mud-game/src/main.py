from server import TelnetServer
from database import Database

def main():
    db = Database("game.db")

    server = TelnetServer(db)
    server.start()

if __name__ == "__main__":
    main()