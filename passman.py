#!/usr/bin/env python3
# don't forget : chmod +x passman.py

from models import *
import bcrypt

line = '_' * 25

def initialize():
    """Create the database and tables if they don't already exist"""
    db.connect()
    db.create_tables([Password, User], safe = True)

def check_users():
    users = User.select()
    if not users.exists():
        create_user()


def create_user():
    """Create a new user"""
    new_user = False
    while new_user == False:
        username = input("Enter a username: ")
        password = input("Enter a password: ")
        confirmation = input("Confirm password: ")

        errors = []
        if username == "":
            errors.append('Missing username')
        if password == "":
            errors.append('Missing password')
        if confirmation == "":
            errors.append('Missing password confirmation')
        if password != confirmation:
            errors.append('Password and confirmation do not match')

        if len(errors) > 0:
            print("Error - User cannot be saved: ")
            for error in errors:
                print(error)
            print(line)
            continue

        query = User.select().where(User.username == username)
        if query.exists():
            print("Username unavailable. Please try again.")
            continue


        hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        User.create(
            username = username,
            password_hash = hash
        )
        print("User created successfully!")
        print(line)
        new_user = True


def login():
    login = False
    while login == False:
        entered_username = input("Please enter your user name: ")
        entered_password = input("Please enter your master password: ")

        query = User.select().where(User.username == entered_username)
        if not query.exists():
            print("User '{}' not found".format(entered_username))
            continue

        created_user = User.get(User.username == entered_username)
        encoded_entered_password = bytes(entered_password, 'utf-8')
        encoded_stored_hash = bytes(created_user.password_hash, 'utf-8')

        hash = bcrypt.hashpw(encoded_entered_password, encoded_stored_hash).decode('utf-8')

        if created_user.password_hash == hash:
            login = True
        else:
            print("Password not valid for user '{}'".format(entered_username))
            continue

def menu_loop():
    """Show the menu"""
    choice = None

    print(line)

    while choice != 'q':
        print("Enter 'q' to quit.")
        for key, value in menu.items():
            print('{}) {}'.format(key, value.__doc__))

        choice = input('Action: ').lower().strip()

        if choice in menu:
            menu[choice]()

def add_password():
    """Add a password"""
    application = input("Enter the application name: ")
    login = input("Enter the login name (email or username): ")
    password = input("Enter password: ")
    password_again = input("Confirm password: ")
    notes = input("(optional) Enter notes/ additional info: ")

    errors = []
    if application == "":
        errors.append('Missing application')
    if login == "":
        errors.append('Missing login')
    if password == "":
        errors.append('Missing password')
    if password_again == "":
        errors.append('Missing password confirmation')
    if password != password_again:
        errors.append('Password and confirmation do not match')

    if len(errors) > 0:
        print("Error - Password cannot be saved: ")
        for error in errors:
            print(error)
        print(line)

    if not errors:
        if input("Save password? [Yn] ").lower() != 'n':
            Password.create(
                application = application,
                login = login,
                password = password,
                notes = notes
            )
            print("Saved successfully!")

def view_passwords(search_query = None):
    """View all passwords"""
    passwords = Password.select().order_by(Password.modified_at.desc())
    if search_query:
        passwords = passwords.where(Password.application.contains(search_query))

    if not passwords:
        print("No records found...")
        print(line)

    for password in passwords:
        modified_at = password.modified_at.strftime('%A %B %d, %Y %I:%M%p')
        print(modified_at)
        print('=' * len(modified_at))
        print(f"Application Name: {password.application}")
        print(f"Login Credentials: {password.login}")
        print(f"Password: {password.password}")
        print(f"Notes: {password.notes}")
        print(line)
        print('n) for next password')
        print('q) return to main menu')

        next_action = input("Action: [Nq] ").lower().strip()
        if next_action == 'q':
            break

def search_passwords():
    """Search all passwords by application name"""
    query = input("Search: ").lower().strip()
    view_passwords(query)


def delete_password(password):
    """Delete a password"""

menu = OrderedDict([
    ('a', add_password),
    ('v', view_passwords),
    ('s', search_passwords),
    ('c', create_user)
])

if __name__ == '__main__':
    initialize()
    check_users()
    login()
    menu_loop()
