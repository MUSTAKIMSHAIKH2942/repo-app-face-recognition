import csv
import json
import os
import bcrypt

def load_users():
    users = []
    if not os.path.exists('data'):
        os.makedirs('data')  # Ensure the directory exists
    
    try:
        with open("data/users.csv", mode="r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if 'username' not in row or 'password' not in row or 'role' not in row:
                    continue  # Skip invalid rows
                users.append(row)
    except FileNotFoundError:
        # Default admin and user
        users = [
            {"username": "admin", "password": hash_password("admin123"), "role": "admin"},
            {"username": "user", "password": hash_password("user123"), "role": "user"},
        ]
        save_users(users)
    except csv.Error as e:
        print(f"CSV reading error: {e}")
        return []

    return users


def save_users(users):
    with open("data/users.csv", mode="w", newline="") as file:
        fieldnames = ["username", "password", "role"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        writer.writeheader()  # Write the header row
        writer.writerows(users)  # Write the user data rows

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def check_password(stored_hash, password):
    return bcrypt.checkpw(password.encode('utf-8'), stored_hash)


CAMERA_FILE_PATH = "data/camera_indices.json"

def load_cameras():
    if not os.path.exists(CAMERA_FILE_PATH):  # If file doesn't exist, create it
        with open(CAMERA_FILE_PATH, "w") as file:
            json.dump([], file)  # Default to an empty list
    
    with open(CAMERA_FILE_PATH, "r") as file:
        try:
            content = file.read().strip()
            if not content:  # If file is empty, reset it
                return []
            return json.loads(content)
        except json.JSONDecodeError:
            return []  # Return empty list if JSON is invalid
def save_cameras(cameras):
    with open("data/camera_indices.json", "w") as file:
        json.dump(cameras, file)

        import json
import os

LIMITS_FILE = "data/limits.json"

def load_limits():
    """Loads the user and camera limits from a JSON file."""
    if not os.path.exists(LIMITS_FILE):
        return {"MAX_USERS": 20, "MAX_CAMERAS": 5}  # Default limits

    with open(LIMITS_FILE, "r") as f:
        return json.load(f)

def save_limits(max_users, max_cameras):
    """Saves the user and camera limits to a JSON file."""
    limits = {"MAX_USERS": max_users, "MAX_CAMERAS": max_cameras}
    with open(LIMITS_FILE, "w") as f:
        json.dump(limits, f)
