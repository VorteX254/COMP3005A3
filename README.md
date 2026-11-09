# Database Interaction with PostgreSQL and Application Programming (COMP3005 Assignment 3 Q1)

A small Python terminal application that connects to a PostgreSQL database and performs CRUD (Create, Read, Update, Delete) operations on a `students` table.

Video: https://youtu.be/yyhKYvPeu3c

## Prerequisites

- Python 3.10+
- PostgreSQL
- pgAdmin 4

## Database setup

Create a database named `comp3005a3`, then run `schema.sql` to create the `students` table and insert the 3 initial rows.

**pgAdmin**

1. Create a database named `comp3005a3`.
2. Right-click the database and open the **Query Tool**.
3. Open `schema.sql` in the Query Tool and run it.

`schema.sql` can be re-run at any time. It drops the table first, so re-running it deletes any changes and restores the 3 initial rows.

## Application setup

1. Create and activate a virtual environment:

   Windows:
   ```
   python -m venv venv
   venv\Scripts\activate
   ```

   macOS/Linux:
   ```
   python3 -m venv venv
   source venv/bin/activate
   ```

2. Install the dependencies:

   ```
   pip install -r requirements.txt
   ```

3. Copy `.env.example` to `.env`:

   Windows:
   ```
   copy .env.example .env
   ```

   macOS/Linux:
   ```
   cp .env.example .env
   ```

4. Open `.env` and set `DB_PASSWORD` to your PostgreSQL password. Change the other settings if your server differs from the defaults.

## Compile and run

With the virtual environment active, run:

```
python app.py
```

## Usage

The application shows a menu. Enter a number to choose an option:

| Option | What it does | Function called |
|---|---|---|
| 1. View all students | Prints every student as a table | `getAllStudents()` |
| 2. Add a student | Asks for a first name, last name, email and optional enrollment date (`YYYY-MM-DD`), then inserts the student and prints the new ID | `addStudent(first_name, last_name, email, enrollment_date)` |
| 3. Update a student's email | Asks for a student ID and a new email, then updates that student | `updateStudentEmail(student_id, new_email)` |
| 4. Delete a student | Asks for a student ID, then deletes that student | `deleteStudent(student_id)` |
| 5. Exit | Closes the application | None |

The application prints a clear message instead of crashing for a duplicate email, a student ID that does not exist, an invalid date, or an ID that is not a number.

## Files

- `schema.sql`: creates the `students` table and inserts the initial data
- `app.py`: the application, with the four CRUD functions and the menu
- `requirements.txt`: the Python dependencies
- `.env.example`: template for the database connection settings
- `.gitignore`: keeps `.env` and generated folders out of git
- `README.md`: this file
