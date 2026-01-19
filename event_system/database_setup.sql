-- Oracle SQL script for College Event Registration and Attendance Management System

-- Drop existing tables and sequences to ensure a clean setup
-- This is useful for development and testing purposes.
-- In a production environment, you would be more careful with dropping objects.

BEGIN
   EXECUTE IMMEDIATE 'DROP TABLE ATTENDANCE';
EXCEPTION
   WHEN OTHERS THEN
      IF SQLCODE != -942 THEN
         RAISE;
      END IF;
END;
/

BEGIN
   EXECUTE IMMEDIATE 'DROP TABLE REGISTRATIONS';
EXCEPTION
   WHEN OTHERS THEN
      IF SQLCODE != -942 THEN
         RAISE;
      END IF;
END;
/

BEGIN
   EXECUTE IMMEDIATE 'DROP TABLE EVENTS';
EXCEPTION
   WHEN OTHERS THEN
      IF SQLCODE != -942 THEN
         RAISE;
      END IF;
END;
/

BEGIN
   EXECUTE IMMEDIATE 'DROP TABLE STUDENTS';
EXCEPTION
   WHEN OTHERS THEN
      IF SQLCODE != -942 THEN
         RAISE;
      END IF;
END;
/

BEGIN
   EXECUTE IMMEDIATE 'DROP TABLE USERS';
EXCEPTION
   WHEN OTHERS THEN
      IF SQLCODE != -942 THEN
         RAISE;
      END IF;
END;
/

BEGIN
   EXECUTE IMMEDIATE 'DROP SEQUENCE event_id_seq';
EXCEPTION
   WHEN OTHERS THEN
      IF SQLCODE != -2289 THEN
         RAISE;
      END IF;
END;
/

BEGIN
   EXECUTE IMMEDIATE 'DROP SEQUENCE reg_id_seq';
EXCEPTION
   WHEN OTHERS THEN
      IF SQLCODE != -2289 THEN
         RAISE;
      END IF;
END;
/

BEGIN
   EXECUTE IMMEDIATE 'DROP SEQUENCE attendance_id_seq';
EXCEPTION
   WHEN OTHERS THEN
      IF SQLCODE != -2289 THEN
         RAISE;
      END IF;
END;
/


-- Create Sequences for auto-generating primary keys
CREATE SEQUENCE user_id_seq START WITH 1 INCREMENT BY 1;
CREATE SEQUENCE event_id_seq START WITH 1 INCREMENT BY 1;
CREATE SEQUENCE reg_id_seq START WITH 1 INCREMENT BY 1;
CREATE SEQUENCE attendance_id_seq START WITH 1 INCREMENT BY 1;

-- Create Tables

-- EVENTS Table
CREATE TABLE EVENTS (
    event_id NUMBER DEFAULT event_id_seq.NEXTVAL NOT NULL,
    event_name VARCHAR2(255) NOT NULL,
    event_date DATE NOT NULL,
    event_time VARCHAR2(20) NOT NULL,
    venue VARCHAR2(255) NOT NULL,
    total_slots NUMBER NOT NULL,
    CONSTRAINT pk_events PRIMARY KEY (event_id)
);

-- STUDENTS Table
CREATE TABLE STUDENTS (
    student_id VARCHAR2(255) NOT NULL,
    name VARCHAR2(255) NOT NULL,
    email VARCHAR2(255) NOT NULL UNIQUE,
    course VARCHAR2(255),
    year NUMBER,
    CONSTRAINT pk_students PRIMARY KEY (student_id)
);

-- REGISTRATIONS Table
CREATE TABLE REGISTRATIONS (
    reg_id NUMBER DEFAULT reg_id_seq.NEXTVAL NOT NULL,
    event_id NUMBER NOT NULL,
    student_id VARCHAR2(255) NOT NULL,
    reg_date DATE DEFAULT SYSDATE,
    status VARCHAR2(50) DEFAULT 'REGISTERED', -- e.g., REGISTERED, CANCELLED
    CONSTRAINT pk_registrations PRIMARY KEY (reg_id),
    CONSTRAINT fk_reg_events FOREIGN KEY (event_id) REFERENCES EVENTS(event_id),
    CONSTRAINT fk_reg_students FOREIGN KEY (student_id) REFERENCES STUDENTS(student_id),
    CONSTRAINT uk_event_student UNIQUE (event_id, student_id)
);

-- ATTENDANCE Table
CREATE TABLE ATTENDANCE (
    attendance_id NUMBER DEFAULT attendance_id_seq.NEXTVAL NOT NULL,
    event_id NUMBER NOT NULL,
    student_id VARCHAR2(255) NOT NULL,
    attended CHAR(1) DEFAULT 'N' NOT NULL, -- 'Y' for Yes, 'N' for No
    CONSTRAINT pk_attendance PRIMARY KEY (attendance_id),
    CONSTRAINT fk_att_events FOREIGN KEY (event_id) REFERENCES EVENTS(event_id),
    CONSTRAINT fk_att_students FOREIGN KEY (student_id) REFERENCES STUDENTS(student_id),
    CONSTRAINT uk_att_event_student UNIQUE (event_id, student_id),
    CONSTRAINT chk_attended CHECK (attended IN ('Y', 'N'))
);

-- USERS Table
CREATE TABLE USERS (
    user_id NUMBER DEFAULT user_id_seq.NEXTVAL NOT NULL,
    username VARCHAR2(255) NOT NULL,
    password VARCHAR2(255) NOT NULL, -- In a real app, this should be a hashed password
    role VARCHAR2(50) NOT NULL,
    CONSTRAINT pk_users PRIMARY KEY (user_id),
    CONSTRAINT uk_username UNIQUE (username),
    CONSTRAINT chk_role CHECK (role IN ('admin', 'volunteer'))
);

-- Comments explaining the business rules and design choices

/*
-- DATABASE DESIGN NOTES --

1.  **Primary Keys and Sequences:**
    - `event_id`, `reg_id`, and `attendance_id` are set to auto-increment using Oracle sequences (`event_id_seq`, `reg_id_seq`, `attendance_id_seq`).
    - This ensures that each new record gets a unique, automatically generated ID.

2.  **Foreign Key Constraints:**
    - `REGISTRATIONS` and `ATTENDANCE` tables are linked to `EVENTS` and `STUDENTS` using foreign keys.
    - This maintains referential integrity, e.g., you cannot register a student for an event that does not exist.

3.  **Unique Constraints:**
    - `UK_EVENT_STUDENT` in `REGISTRATIONS`: Prevents a student from registering for the same event more than once.
    - `UK_ATT_EVENT_STUDENT` in `ATTENDANCE`: Ensures that there is only one attendance record per student for a given event.
    - `UK_USERNAME` in `USERS`: Ensures that every username is unique.

4.  **Check Constraints:**
    - `CHK_ATTENDED` in `ATTENDANCE`: Restricts the `attended` column to 'Y' or 'N'.
    - `CHK_ROLE` in `USERS`: Restricts the `role` column to 'admin' or 'volunteer'.

5.  **Default Values:**
    - `reg_date` in `REGISTRATIONS` defaults to the current system date (`SYSDATE`).
    - `status` in `REGISTRATIONS` defaults to 'REGISTERED'.
    - `attended` in `ATTENDANCE` defaults to 'N'.

-- BUSINESS RULE IMPLEMENTATION IN DB --

1.  **Event Capacity Enforcement:**
    - This is not directly enforced by a database constraint, as it requires checking the count of registrations against `EVENTS.total_slots`.
    - This logic will be implemented in the `registrations.py` module before an INSERT into the `REGISTRATIONS` table.

2.  **Attendance Rules:**
    - **"Student must be registered"**: The application logic in `attendance.py` will check for a valid registration in the `REGISTRATIONS` table before allowing attendance marking.
    - **"One attendance record per student per event"**: Enforced by the `UK_ATT_EVENT_STUDENT` unique constraint.
    - **"Attendance only on or after event_date"**: This will be handled in the `attendance.py` module. A database trigger could also be used for this, but application-level control is often more flexible.

3.  **Data Validation:**
    - **"No duplicate registrations"**: Enforced by `UK_EVENT_STUDENT`.
    - **"No attendance without registration"**: Application logic will enforce this, although a foreign key from ATTENDANCE to REGISTRATIONS could also be an option (but the current design is also valid).
*/

-- End of script
