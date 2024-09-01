import random
import string
import psycopg2
from psycopg2 import sql
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

def generate_api_key(length=40):
    """Generate a random alphanumeric API key."""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

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

def user_exists(conn, token):
    """Check if a user exists in the database with the provided token."""
    with conn.cursor() as cursor:
        query = sql.SQL("SELECT id FROM api_user WHERE secret_key = %s")
        cursor.execute(query, [token])
        result = cursor.fetchone()
        return result[0] if result else None

def save_auth_token(conn, api_key, user_id):
    """Save the API key in the AuthToken table."""
    with conn.cursor() as cursor:
        insert_query = sql.SQL("""
            INSERT INTO api_authtoken (key, user_id, created)
            VALUES (%s, %s, %s)
        """)
        cursor.execute(insert_query, (api_key, user_id, datetime.now()))
        conn.commit()

def create_auth_token():
    """Check user via token, generate API key, and save it."""
    # Prompt user for token
    token = input("Enter your token: ")
    
    # Connect to the PostgreSQL database
    conn = connect_db()
    
    # Check if user exists
    user_id = user_exists(conn, token)
    if not user_id:
        print("User with the provided token does not exist.")
        conn.close()
        return
    
    # Generate a 40-character alphanumeric API key
    api_key = generate_api_key()
    
    # Save the API key in the database
    save_auth_token(conn, api_key, user_id)
    
    # Close the database connection
    conn.close()
    
    print(f"API Key generated and saved successfully: {api_key}")

if __name__ == "__main__":
    create_auth_token()
