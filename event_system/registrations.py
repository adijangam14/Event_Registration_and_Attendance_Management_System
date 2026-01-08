# registrations.py
# Handles student registrations for events, including capacity checks.

from . import db
import datetime

def register_student_for_event(event_id, student_id):
    """
    Registers a student for a specific event.

    This function enforces several business rules:
    1.  Checks if the event and student exist.
    2.  Checks if the student is already registered for the event.
    3.  Checks if the event has reached its maximum capacity.

    Args:
        event_id (int): The ID of the event.
        student_id (str): The ID of the student.

    Returns:
        str: A message indicating the result (success, or a specific error).
    """
    conn = db.get_connection()
    if not conn:
        return "Database connection error."

    cursor = conn.cursor()
    try:
        # --- Check 1: Event Capacity and Existence ---
        cursor.execute("SELECT total_slots FROM EVENTS WHERE event_id = :event_id", {'event_id': event_id})
        event_result = cursor.fetchone()
        if not event_result:
            return "Error: Event not found."
        
        total_slots = event_result[0]

        # --- Check 2: Student Existence ---
        cursor.execute("SELECT name FROM STUDENTS WHERE student_id = :student_id", {'student_id': student_id})
        if not cursor.fetchone():
            return "Error: Student not found."

        # --- Check 3: Already Registered ---
        cursor.execute(
            "SELECT reg_id FROM REGISTRATIONS WHERE event_id = :event_id AND student_id = :student_id",
            {'event_id': event_id, 'student_id': student_id}
        )
        if cursor.fetchone():
            return "Info: Student is already registered for this event."

        # --- Check 4: Capacity Check ---
        cursor.execute("SELECT COUNT(*) FROM REGISTRATIONS WHERE event_id = :event_id", {'event_id': event_id})
        registered_count = cursor.fetchone()[0]
        
        if registered_count >= total_slots:
            return "Error: Event is full. Cannot register."

        # --- If all checks pass, proceed with registration ---
        insert_query = """
        INSERT INTO REGISTRATIONS (event_id, student_id, reg_date)
        VALUES (:event_id, :student_id, :reg_date)
        """
        cursor.execute(insert_query, {
            'event_id': event_id,
            'student_id': student_id,
            'reg_date': datetime.datetime.now()
        })
        
        conn.commit()
        return "Success: Student registered successfully."

    except Exception as e:
        print(f"Error during registration: {e}")
        conn.rollback()
        return f"An unexpected error occurred: {e}"
    finally:
        cursor.close()
        conn.close()

def get_registered_students(event_id):
    """
    Retrieves a list of students registered for a given event.

    Args:
        event_id (int): The ID of the event.

    Returns:
        list: A list of tuples, where each tuple contains
              (student_id, student_name, registration_date).
              Returns an empty list on error or if no students are registered.
    """
    conn = db.get_connection()
    if not conn:
        return []

    cursor = conn.cursor()
    try:
        query = """
        SELECT s.student_id, s.name, s.email, r.reg_date
        FROM STUDENTS s
        JOIN REGISTRATIONS r ON s.student_id = r.student_id
        WHERE r.event_id = :event_id
        ORDER BY s.name
        """
        cursor.execute(query, {'event_id': event_id})
        return cursor.fetchall()
    except Exception as e:
        print(f"Error fetching registered students: {e}")
        return []
    finally:
        cursor.close()
        conn.close()


# Example usage (for testing purposes)
if __name__ == '__main__':
    # This assumes you have some data in your tables.
    # For example:
    # 1. An event (e.g., created via events.py, let's assume its ID is 1)
    #    Event: 'Annual Tech Symposium', total_slots: 2
    # 2. A student:
    #    INSERT INTO STUDENTS (student_id, name, course, year) VALUES ('S001', 'Alice', 'CS', 3);
    #    INSERT INTO STUDENTS (student_id, name, course, year) VALUES ('S002', 'Bob', 'IT', 2);
    #    INSERT INTO STUDENTS (student_id, name, course, year) VALUES ('S003', 'Charlie', 'CS', 4);

    EVENT_ID_TO_TEST = 1  # Change this to an existing event_id in your DB

    print(f"--- Testing Registration for Event ID: {EVENT_ID_TO_TEST} ---")

    # Test 1: Successful registration
    print("\n1. Testing successful registration for Alice (S001)...")
    result = register_student_for_event(EVENT_ID_TO_TEST, 'S001')
    print(f"   Result: {result}")

    # Test 2: Duplicate registration
    print("\n2. Testing duplicate registration for Alice (S001)...")
    result = register_student_for_event(EVENT_ID_TO_TEST, 'S001')
    print(f"   Result: {result}")

    # Test 3: Successful registration for another student
    print("\n3. Testing successful registration for Bob (S002)...")
    result = register_student_for_event(EVENT_ID_TO_TEST, 'S002')
    print(f"   Result: {result}")

    # Test 4: Attempt to register when full (assuming total_slots was 2)
    print("\n4. Testing registration when event is full for Charlie (S003)...")
    result = register_student_for_event(EVENT_ID_TO_TEST, 'S003')
    print(f"   Result: {result}")
    
    # Test 5: Registering for a non-existent event
    print("\n5. Testing registration for a non-existent event (ID 999)...")
    result = register_student_for_event(999, 'S001')
    print(f"   Result: {result}")

    # Test 6: Registering a non-existent student
    print("\n6. Testing registration for a non-existent student (ID S999)...")
    result = register_student_for_event(EVENT_ID_TO_TEST, 'S999')
    print(f"   Result: {result}")

    # Test 7: Fetching registered students
    print(f"\n7. Fetching all students registered for event {EVENT_ID_TO_TEST}...")
    registered_list = get_registered_students(EVENT_ID_TO_TEST)
    if registered_list:
        print("   Registered students:")
        for student in registered_list:
            print(f"   - {student}")
    else:
        print("   No students registered or an error occurred.")

