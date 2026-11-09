"""
Student Database - Database Interaction with PostgreSQL and Application Programming (COMP3005 Assignment 3).

This program connects to a PostgreSQL database and performs CRUD
(Create, Read, Update, Delete) operations on the "students" table
created by schema.sql. It provides an interactive terminal menu that
calls the following functions:

    getAllStudents()      - Read:   show every student
    addStudent(...)       - Create: insert a new student
    updateStudentEmail()  - Update: change a student's email
    deleteStudent()       - Delete: remove a student

How to run:
    1. Run schema.sql against your database (see README.md).
    2. Copy .env.example to .env and fill in your PostgreSQL password.
    3. pip install -r requirements.txt
    4. python app.py
"""

import os
import sys
from datetime import datetime

import psycopg2
from psycopg2 import errors
from dotenv import load_dotenv


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
# Load connection settings from the .env file into environment variables.
load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
    "dbname": os.getenv("DB_NAME", "comp3005a3"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD"),
}


# ---------------------------------------------------------------------------
# Connection helper
# ---------------------------------------------------------------------------
def get_connection():
    """
    Open and return a new psycopg2 connection using the settings in DB_CONFIG.
    """
    try:
        return psycopg2.connect(**DB_CONFIG)
    except psycopg2.Error as e:
        print("Could not connect to PostgreSQL - check your .env settings "
              "and that the server is running.")
        print(f"Details: {e}")
        sys.exit(1)


# ---------------------------------------------------------------------------
# CRUD functions
# ---------------------------------------------------------------------------
def getAllStudents():
    """
    Read: retrieve and display every record in the students table.

    Parameters:
        None

    SQL:
        SELECT * FROM students ORDER BY student_id;

    Prints the rows as an aligned table with column headers, or
    "No students found." if the table is empty.
    """
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM students ORDER BY student_id;")
                rows = cur.fetchall()
                # cur.description holds the column metadata; use it for headers.
                headers = [col.name for col in cur.description]
    finally:
        conn.close()

    if not rows:
        print("No students found.")
        return

    # Convert every value to text (NULL -> empty string) so widths can be measured.
    table = [["" if value is None else str(value) for value in row] for row in rows]

    # Each column is as wide as its longest value or its header, whichever is longer.
    widths = [
        max(len(header), *(len(row[i]) for row in table))
        for i, header in enumerate(headers)
    ]

    # Print the header, a separator line, then one line per student.
    print("  ".join(h.ljust(w) for h, w in zip(headers, widths)))
    print("  ".join("-" * w for w in widths))
    for row in table:
        print("  ".join(value.ljust(w) for value, w in zip(row, widths)))


def addStudent(first_name, last_name, email, enrollment_date):
    """
    Create: insert a new student record into the students table.

    Parameters:
        first_name (str):      student's first name
        last_name (str):       student's last name
        email (str):           student's email (must be unique)
        enrollment_date (str): date in YYYY-MM-DD format, or empty/None to
                               store NULL

    SQL:
        INSERT INTO students (first_name, last_name, email, enrollment_date)
        VALUES (%s, %s, %s, %s)
        RETURNING student_id;

    Prints the new student's ID, or a friendly message if the email is
    already in use or the date is invalid. Returns True on success.
    """
    # Validate the date before touching the database. An empty value is
    # allowed and stored as NULL because enrollment_date is optional.
    if enrollment_date:
        try:
            datetime.strptime(enrollment_date, "%Y-%m-%d")
        except ValueError:
            print(f"Invalid date '{enrollment_date}'. Use the format YYYY-MM-DD.")
            return False
    else:
        enrollment_date = None

    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO students (first_name, last_name, email, enrollment_date) "
                    "VALUES (%s, %s, %s, %s) RETURNING student_id;",
                    (first_name, last_name, email, enrollment_date),
                )
                # RETURNING gives back the ID that SERIAL generated for the new row.
                new_id = cur.fetchone()[0]
        print(f"Student added with ID {new_id}.")
        return True
    except errors.UniqueViolation:
        # The UNIQUE constraint on email rejected the insert. Leaving the
        # "with conn:" block through this exception has already rolled the
        # transaction back, so the database is unchanged.
        print(f"A student with email '{email}' already exists.")
        return False
    finally:
        conn.close()


def updateStudentEmail(student_id, new_email):
    """
    Update: change the email address of the student with the given ID.

    Parameters:
        student_id (int): ID of the student to update
        new_email (str):  the new email address (must be unique)

    SQL:
        UPDATE students SET email = %s WHERE student_id = %s;

    Prints a confirmation, "No student with ID X" if the ID does not
    exist, or a friendly message if the email is already in use.
    Returns True on success.
    """
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE students SET email = %s WHERE student_id = %s;",
                    (new_email, student_id),
                )
                # rowcount is the number of rows the UPDATE changed; 0 means no match.
                updated = cur.rowcount
        if updated == 0:
            print(f"No student with ID {student_id}.")
            return False
        print(f"Email for student {student_id} updated to '{new_email}'.")
        return True
    except errors.UniqueViolation:
        # Another student already has this email; "with conn:" rolled back.
        print(f"A student with email '{new_email}' already exists.")
        return False
    finally:
        conn.close()


def deleteStudent(student_id):
    """
    Delete: remove the student with the given ID from the students table.

    Parameters:
        student_id (int): ID of the student to delete

    SQL:
        DELETE FROM students WHERE student_id = %s;

    Prints a confirmation, or "No student with ID X" if the ID does not
    exist. Returns True on success.
    """
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM students WHERE student_id = %s;", (student_id,))
                # rowcount is the number of rows deleted; 0 means no match.
                deleted = cur.rowcount
    finally:
        conn.close()

    if deleted == 0:
        print(f"No student with ID {student_id}.")
        return False
    print(f"Student {student_id} deleted.")
    return True


# ---------------------------------------------------------------------------
# Input helpers for menu
# ---------------------------------------------------------------------------
# These keep asking until the user types something valid, so bad input never
# crashes the program.

def prompt_int(message):
    """Ask for a whole number, re-prompting until a valid integer is entered."""
    while True:
        value = input(message).strip()
        try:
            return int(value)
        except ValueError:
            print("Please enter a whole number (e.g. 1).")


def prompt_required(message):
    """Ask for text that cannot be empty, re-prompting until something is entered."""
    while True:
        value = input(message).strip()
        if value:
            return value
        print("This field is required.")


# ---------------------------------------------------------------------------
# Interactive menu
# ---------------------------------------------------------------------------
MENU = """
=== Student Database ===
1. View all students
2. Add a student
3. Update a student's email
4. Delete a student
5. Exit"""


def main():
    # Show the menu in a loop and call the matching CRUD function.
    while True:
        print(MENU)
        choice = input("Choose an option (1-5): ").strip()

        try:
            if choice == "1":
                getAllStudents()

            elif choice == "2":
                first_name = prompt_required("First name: ")
                last_name = prompt_required("Last name: ")
                email = prompt_required("Email: ")
                enrollment_date = input("Enrollment date (YYYY-MM-DD, blank for none): ").strip()
                ok = addStudent(first_name, last_name, email, enrollment_date)
                print("Add succeeded." if ok else "Add failed.")

            elif choice == "3":
                student_id = prompt_int("Student ID: ")
                new_email = prompt_required("New email: ")
                ok = updateStudentEmail(student_id, new_email)
                print("Update succeeded." if ok else "Update failed.")

            elif choice == "4":
                student_id = prompt_int("Student ID: ")
                ok = deleteStudent(student_id)
                print("Delete succeeded." if ok else "Delete failed.")

            elif choice == "5":
                print("Goodbye!")
                break

            else:
                print("Invalid choice. Please enter a number from 1 to 5.")

        except psycopg2.Error as e:
            # Safety net for any other database error (e.g. the table does not
            # exist yet) so the menu reports it instead of crashing.
            print(f"Database error: {e}")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        # Ctrl+C / Ctrl+D: exit cleanly without an error.
        print("\nGoodbye!")
