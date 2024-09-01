import random
import string
import pyperclip
import psycopg2
from psycopg2 import sql
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

def generate_secret_key(length=40):
    """Generate a random alphanumeric secret key."""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))
        # 'ENGINE': os.getenv("ENGINE"),
        # 'NAME': os.getenv("NAME"),
        # 'USER': os.getenv("USER"),
        # 'PASSWORD': os.getenv("PASSWORD"),
        # 'HOST': os.getenv("HOST"),
        # 'PORT': os.getenv("PORT"),
def connect_db():
    """Connect to the PostgreSQL database."""
    conn = psycopg2.connect(
        dbname= os.getenv("NAME"),
        user= os.getenv("USER"),
        password= os.getenv("PASSWORD"),
        host= os.getenv("HOST"),
        port= os.getenv("PORT")
    )
    return conn

def save_user(conn, username, organization, email, secret_key):

    """Save the user details in the users table."""
    with conn.cursor() as cursor:
        insert_query = sql.SQL("""
            INSERT INTO api_user (username, organization, email, secret_key, created)
            VALUES (%s, %s, %s, %s, %s)
        """)
        cursor.execute(insert_query, (username, organization, email, secret_key, datetime.now()))
        conn.commit()

def create_user():
    """Prompt the user for details, create a new user, and save to database."""
    print("Please enter the following details to create a new user:\n")
    
    username = input("Username: ")
    organization = input("Organization: ")
    email = input("Email: ")
    
    # Generate a 40-character alphanumeric secret key
    secret_key = generate_secret_key()
    
    # Copy the secret key to clipboard
    pyperclip.copy(secret_key)
    
    # Connect to the PostgreSQL database
    conn = connect_db()
    
    # Save the user in the database
    save_user(conn, username, organization, email, secret_key)
    
    # Close the database connection
    conn.close()
    
    print("\nUser created successfully!")
    print(f"Username: {username}")
    print(f"Organization: {organization}")
    print(f"Email: {email}")
    print(f"Secret Key: {secret_key}")
    print("Secret Key has been copied to the clipboard.")

if __name__ == "__main__":
    create_user()
