# Game Manual

## Introduction

Welcome to the MUD game! This manual will guide you through the current features of the game and the specifications needed to run it.

## Features

### User Registration

- New users can register by providing a username, password, sex, and age.
- The system checks if the username already exists and prompts the user to try again if it does.

### User Login

- Registered users can log in by providing their username and password.
- The system verifies the credentials and grants access if they are correct.

### Character Management

- After logging in, users can select an existing character or create a new one.
- Users can create a character by providing a character name and choosing a class (Warrior, Mage, Holy Man).
- The system stores the character information and allows users to select it in future sessions.

### Commands

- `?` - Show the help message with available commands.
- `s` - Show the current character's stats.
- `quit` - Quit the game.

## Specifications

### Requirements

- Python 3.7 or higher
- SQLite3

### Installation

1. Clone the repository:
    ```sh
    git clone <repository-url>
    ```

2. Navigate to the project directory:
    ```sh
    cd mud-game
    ```

3. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

### Running the Game

1. Start the game server:
    ```sh
    python src/main.py
    ```

2. Connect to the game server using a Telnet client:
    ```sh
    telnet <server-ip> 23
    ```

### .gitignore

Ensure that the [game.db] file is not pushed to the repository by adding the following line to your [.gitignore] file:
```ignore
*.db