import os
import csv

def count_users():
    user_count = 0
    if not os.path.exists("data/user_data_store.csv"):
        print("User file not found. Returning default count: 0")
        return user_count  # Return 0 if file doesn't exist

    try:
        with open("data/user_data_store.csv", mode="r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if 'username' in row and row['username'].strip():  # Ensure username exists
                    user_count += 1
    except csv.Error as e:
        print(f"CSV reading error: {e}")
        return 0

    return user_count
