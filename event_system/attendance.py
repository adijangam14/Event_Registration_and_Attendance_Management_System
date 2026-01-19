# attendance.py
# Handles marking and viewing of student attendance for events.

from . import db
import datetime

def mark_attendance(event_id, student_id, attended_status='Y'):
    """
    Marks or updates a student's attendance for a given event.

    This function enforces several business rules:
    1.  Verifies that the event date is on or before the current date.
    2.  Checks if the student is registered for the event.
    3.  Inserts a new attendance record or updates an existing one.

    Args:
        event_id (int): The ID of the event.
        student_id (str): The ID of the student.
        attended_status (str): 'Y' for attended, 'N' for not attended.

    Returns:
        str: A message indicating the result of the operation.
    """
    conn = db.get_connection()
    if not conn:
        return "Database connection error."

    cursor = conn.cursor()
    try:
        # --- Check 1: Event Date vs. Current Date ---
        cursor.execute("SELECT event_date FROM EVENTS WHERE event_id = :event_id", {'event_id': event_id})
        result = cursor.fetchone()
        if not result:
            return "Error: Event not found."
        
        event_date = result[0]
        if event_date.date() > datetime.date.today():
            return f"Error: Attendance can only be marked on or after the event date ({event_date.strftime('%Y-%m-%d')})."

        # --- Check 2: Student Registration ---
        cursor.execute(
            "SELECT reg_id FROM REGISTRATIONS WHERE event_id = :event_id AND student_id = :student_id",
            {'event_id': event_id, 'student_id': student_id}
        )
        if not cursor.fetchone():
            return "Error: Cannot mark attendance for a student who is not registered for this event."

        # --- Check 3: Existing Attendance Record ---
        cursor.execute(
            "SELECT attendance_id FROM ATTENDANCE WHERE event_id = :event_id AND student_id = :student_id",
            {'event_id': event_id, 'student_id': student_id}
        )
        attendance_id = cursor.fetchone()

        if attendance_id:
            # Update existing record
            query = "UPDATE ATTENDANCE SET attended = :status WHERE attendance_id = :att_id"
            cursor.execute(query, {'status': attended_status, 'att_id': attendance_id[0]})
            message = "Success: Attendance record updated."
        else:
            # Insert new record
            query = "INSERT INTO ATTENDANCE (event_id, student_id, attended) VALUES (:eid, :sid, :status)"
            cursor.execute(query, {'eid': event_id, 'sid': student_id, 'status': attended_status})
            message = "Success: Attendance marked."
        
        conn.commit()
        return message

    except Exception as e:
        print(f"Error marking attendance: {e}")
        conn.rollback()
        return f"An unexpected error occurred: {e}"
    finally:
        cursor.close()
        conn.close()

def get_event_attendance(event_id):
    """
    Retrieves the attendance status for all registered students for an event.

    It joins REGISTRATIONS with ATTENDANCE to show all registered students,
    even if their attendance has not been marked yet (showing 'N' by default).

    Args:
        event_id (int): The ID of the event.

    Returns:
        list: A list of tuples, each containing:
              (student_id, student_name, attended_status).
              'Y' or 'N'.
    """
    conn = db.get_connection()
    if not conn:
        return []

    cursor = conn.cursor()
    try:
        # This query gets all registered students and their attendance status.
        # It uses a LEFT JOIN to include registered students even if they don't have an attendance record yet.
        # The NVL function ensures that if attendance is not marked, it defaults to 'N'.
        query = """
        SELECT
            s.student_id,
            s.name,
            NVL(a.attended, 'N') AS attendance_status
        FROM REGISTRATIONS r
        JOIN STUDENTS s ON r.student_id = s.student_id
        LEFT JOIN ATTENDANCE a ON r.event_id = a.event_id AND r.student_id = a.student_id
        WHERE r.event_id = :event_id
        ORDER BY s.name
        """
        cursor.execute(query, {'event_id': event_id})
        return cursor.fetchall()
    except Exception as e:
        print(f"Error fetching event attendance: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

# Example usage (for testing purposes)
if __name__ == '__main__':
    # ASSUMPTIONS FOR TESTING:
    # 1. An event exists with ID=1, and its date is in the past.
    #    (e.g., UPDATE EVENTS SET event_date = '01-JAN-24' WHERE event_id = 1;)
    # 2. Another event exists with ID=2, and its date is in the future.
    #    (e.g., from events.py test, or create one with a future date)
    # 3. Students 'S001' (Alice) and 'S002' (Bob) are registered for event 1.
    #    (e.g., from registrations.py test)

    PAST_EVENT_ID = 1
    FUTURE_EVENT_ID = 2

    print(f"--- Testing Attendance for Past Event (ID: {PAST_EVENT_ID}) ---")
    
    # Test 1: Mark attendance for a registered student
    print("\n1. Marking attendance for Alice (S001)...")
    result = mark_attendance(PAST_EVENT_ID, 'S001', 'Y')
    print(f"   Result: {result}")

    # Test 2: Update attendance for the same student
    print("\n2. Updating attendance for Alice (S001) to 'N'...")
    result = mark_attendance(PAST_EVENT_ID, 'S001', 'N')
    print(f"   Result: {result}")

    # Test 3: Mark attendance for an unregistered student
    print("\n3. Attempting to mark attendance for unregistered Charlie (S003)...")
    result = mark_attendance(PAST_EVENT_ID, 'S003', 'Y')
    print(f"   Result: {result}")

    print(f"\n--- Testing Attendance for Future Event (ID: {FUTURE_EVENT_ID}) ---")

    # Test 4: Attempt to mark attendance for a future event
    print("\n4. Attempting to mark attendance for future event...")
    result = mark_attendance(FUTURE_EVENT_ID, 'S001', 'Y') # Assuming S001 is registered
    print(f"   Result: {result}")

    # Test 5: Fetching attendance list
    print(f"\n--- Fetching attendance for event {PAST_EVENT_ID} ---")
    attendance_list = get_event_attendance(PAST_EVENT_ID)
    if attendance_list:
        print("   Attendance List:")
        for student in attendance_list:
            print(f"   - {student}")
    else:
        print("   No attendance records found or an error occurred.")

