import os

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import mysql.connector


app = FastAPI(
    title="Docker FastAPI + MySQL",
    version="1.0.0"
)


# -----------------------------
# Database connection
# -----------------------------

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "db"),
        port=int(os.getenv("MYSQL_PORT", "3306")),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE")
    )


# -----------------------------
# Request model
# -----------------------------

class UserCreate(BaseModel):
    name: str
    email: str


# -----------------------------
# Home
# -----------------------------

@app.get("/")
def home():
    return {
        "message": "FastAPI + MySQL running with Docker Compose"
    }


# -----------------------------
# Health check
# -----------------------------

@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


# -----------------------------
# Database test
# -----------------------------

@app.get("/db-test")
def database_test():

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT DATABASE()")

    result = cursor.fetchone()

    cursor.close()
    connection.close()

    return {
        "database": result[0],
        "status": "connected"
    }


# -----------------------------
# CREATE USER
# -----------------------------

@app.post("/users")
def create_user(user: UserCreate):

    connection = get_db_connection()
    cursor = connection.cursor()

    query = """
        INSERT INTO users (name, email)
        VALUES (%s, %s)
    """

    cursor.execute(
        query,
        (user.name, user.email)
    )

    connection.commit()

    user_id = cursor.lastrowid

    cursor.close()
    connection.close()

    return {
        "message": "User created",
        "id": user_id,
        "name": user.name,
        "email": user.email
    }


# -----------------------------
# READ ALL USERS
# -----------------------------

@app.get("/users")
def get_users():

    connection = get_db_connection()

    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT * FROM users")

    users = cursor.fetchall()

    cursor.close()
    connection.close()

    return {
        "users": users
    }


# -----------------------------
# READ ONE USER
# -----------------------------

@app.get("/users/{user_id}")
def get_user(user_id: int):

    connection = get_db_connection()

    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM users WHERE id = %s",
        (user_id,)
    )

    user = cursor.fetchone()

    cursor.close()
    connection.close()

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return user


# -----------------------------
# UPDATE USER
# -----------------------------

@app.put("/users/{user_id}")
def update_user(
    user_id: int,
    user: UserCreate
):

    connection = get_db_connection()

    cursor = connection.cursor()

    query = """
        UPDATE users
        SET name = %s, email = %s
        WHERE id = %s
    """

    cursor.execute(
        query,
        (user.name, user.email, user_id)
    )

    connection.commit()

    if cursor.rowcount == 0:

        cursor.close()
        connection.close()

        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    cursor.close()
    connection.close()

    return {
        "message": "User updated",
        "id": user_id,
        "name": user.name,
        "email": user.email
    }


# -----------------------------
# DELETE USER
# -----------------------------

@app.delete("/users/{user_id}")
def delete_user(user_id: int):

    connection = get_db_connection()

    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM users WHERE id = %s",
        (user_id,)
    )

    connection.commit()

    if cursor.rowcount == 0:

        cursor.close()
        connection.close()

        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    cursor.close()
    connection.close()

    return {
        "message": "User deleted",
        "id": user_id
    }