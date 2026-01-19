-- Oracle SQL script for inserting sample data into the Event Management System

-- This script provides sample data for testing purposes.
-- It should be run after `database_setup.sql`.

-- Clear existing data to ensure a clean test environment
-- Use TRUNCATE for fast deletion of all rows.
-- Note: This will fail if there are active child records in other tables
-- and the parent records are attempted to be truncated. Best to delete in order.
DELETE FROM ATTENDANCE;
DELETE FROM REGISTRATIONS;
DELETE FROM EVENTS;
DELETE FROM STUDENTS;
DELETE FROM USERS;

-- 1. Insert Sample Users
-- Passwords are now hashed using bcrypt.
INSERT INTO users (username, password, role) VALUES ('admin1', '$2b$12$HOXstXWr0ZINtI7.Gk3giuyyRG99ovrczd6JNPciU3NS8dZukPdBy', 'admin'); -- password: admin123
INSERT INTO users (username, password, role) VALUES ('volunteer1', '$2b$12$xA6CVpKQV.rO9z7dMxA7COfGDjk5rV/nSPmPNca4GQJcHez1QjPba', 'volunteer'); -- password: volunteer123



-- 2. Insert Sample Students
INSERT INTO STUDENTS (student_id, name, email, course, year) VALUES ('S2024001', 'Aditya jangam', 'adityajangam301@gmail.com', 'Computer Science', 3);
INSERT INTO STUDENTS (student_id, name, email, course, year) VALUES ('S2024002', 'Bob Williams', 'jangam15@gmail.com', 'Information Technology', 2);
INSERT INTO STUDENTS (student_id, name, email, course, year) VALUES ('S2024003', 'Charlie Brown', 'aditya15@gmail.com', 'Mechanical Engineering', 4);
INSERT INTO STUDENTS (student_id, name, email, course, year) VALUES ('S2024004', 'Diana Miller', 'aditya15jangam@gmail.com', 'Electronics', 3);
INSERT INTO STUDENTS (student_id, name, email, course, year) VALUES ('S2024005', 'Ethan Davis', 'jangam15aditya@gmail.com', 'Computer Science', 1);

-- 3. Insert Sample Events
-- One event in the past (for testing attendance marking)
-- One event in the future (for testing restriction on attendance marking)
-- One event with very limited slots (for testing capacity enforcement)
INSERT INTO EVENTS (event_name, event_date, venue, total_slots)
VALUES ('Python Programming Workshop', TO_DATE('2024-03-15', 'YYYY-MM-DD'), 'Lab 3, CS Building', 3);

INSERT INTO EVENTS (event_name, event_date, venue, total_slots)
VALUES ('Annual College Tech Fest', TO_DATE('2024-10-20', 'YYYY-MM-DD'), 'Main Auditorium', 150);

INSERT INTO EVENTS (event_name, event_date, venue, total_slots)
VALUES ('Exclusive AI Seminar', TO_DATE('2024-11-05', 'YYYY-MM-DD'), 'Seminar Hall A', 2);


-- 4. Insert Sample Registrations
-- Let's register some students for the 'Python Programming Workshop' (event_id should be 1 based on sequence)
-- Assuming the sequence starts at 1, the event_ids will be 1, 2, 3.
-- We will hardcode the IDs here for clarity, but in a real script you might select them.
INSERT INTO REGISTRATIONS (event_id, student_id, reg_date) VALUES (1, 'S2024001', SYSDATE - 5);
INSERT INTO REGISTRATIONS (event_id, student_id, reg_date) VALUES (1, 'S2024002', SYSDATE - 4);
INSERT INTO REGISTRATIONS (event_id, student_id, reg_date) VALUES (1, 'S2024004', SYSDATE - 4); -- This will fill up the 'Python Programming Workshop'

-- Register students for the 'Exclusive AI Seminar' (event_id = 3)
INSERT INTO REGISTRATIONS (event_id, student_id, reg_date) VALUES (3, 'S2024003', SYSDATE - 2);
INSERT INTO REGISTRATIONS (event_id, student_id, reg_date) VALUES (3, 'S2024005', SYSDATE - 1); -- This seminar is now full

-- 5. Insert Sample Attendance
-- Let's mark attendance for the 'Python Programming Workshop' since it's in the past.
INSERT INTO ATTENDANCE (event_id, student_id, attended) VALUES (1, 'S2024001', 'Y');
INSERT INTO ATTENDANCE (event_id, student_id, attended) VALUES (1, 'S2024002', 'N');
-- Student S2024004 has no attendance record yet, so will default to 'N' in reports.


-- Commit the changes
COMMIT;

-- Confirmation message
-- In SQL*Plus or similar tools, you can use a prompt.
-- For a script, this comment serves as a note.
-- PROMPT Sample data inserted successfully.

-- End of script
