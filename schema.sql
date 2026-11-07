-- schema.sql
-- Creates the "students" table and loads the initial data.

-- Remove the table if it already exists so the script can be re-run for a clean demo.
DROP TABLE IF EXISTS students;

-- Create the students table.
--   student_id      : primary key
--   first_name      : required text
--   last_name       : required text
--   email           : required text and must be unique across all students
--   enrollment_date : optional date
CREATE TABLE students (
    student_id      SERIAL PRIMARY KEY,
    first_name      TEXT NOT NULL,
    last_name       TEXT NOT NULL,
    email           TEXT NOT NULL UNIQUE,
    enrollment_date DATE
);

-- Insert the provided initial data 
INSERT INTO students (first_name, last_name, email, enrollment_date) VALUES
('John', 'Doe', 'john.doe@example.com', '2023-09-01'),
('Jane', 'Smith', 'jane.smith@example.com', '2023-09-01'),
('Jim', 'Beam', 'jim.beam@example.com', '2023-09-02');
