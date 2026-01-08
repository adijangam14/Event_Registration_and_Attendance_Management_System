# reports.py
# Generates statistics and handles CSV exports for event attendance.

import csv
import os
from . import db

def get_event_statistics(event_id):
    """
    Calculates attendance statistics for a specific event.

    Args:
        event_id (int): The ID of the event.

    Returns:
        dict: A dictionary containing the statistics:
              'registered': Total number of registered students.
              'attended': Total number of attended students.
              'percentage': Attendance percentage.
              Returns None if the event is not found or an error occurs.
    """
    conn = db.get_connection()
    if not conn:
        return None

    cursor = conn.cursor()
    try:
        # Check if event exists
        cursor.execute("SELECT event_name FROM EVENTS WHERE event_id = :event_id", {'event_id': event_id})
        if not cursor.fetchone():
            print(f"No event found with ID: {event_id}")
            return None

        # Get total registered students
        cursor.execute("SELECT COUNT(*) FROM REGISTRATIONS WHERE event_id = :event_id", {'event_id': event_id})
        total_registered = cursor.fetchone()[0]

        # Get total attended students
        cursor.execute(
            "SELECT COUNT(*) FROM ATTENDANCE WHERE event_id = :event_id AND attended = 'Y'",
            {'event_id': event_id}
        )
        total_attended = cursor.fetchone()[0]

        # Calculate attendance percentage
        if total_registered > 0:
            percentage = (total_attended / total_registered) * 100
        else:
            percentage = 0

        return {
            'registered': total_registered,
            'attended': total_attended,
            'percentage': round(percentage, 2)
        }
    except Exception as e:
        print(f"Error calculating statistics for event {event_id}: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

def export_attendance_to_csv(event_id, file_path='.'):
    """
    Exports the attendance list for an event to a CSV file.

    The CSV file will be named `event_{event_id}_attendance.csv`.

    Args:
        event_id (int): The ID of the event.
        file_path (str): The directory where the CSV file will be saved.

    Returns:
        str: The full path of the generated CSV file, or None on failure.
    """
    conn = db.get_connection()
    if not conn:
        return None

    cursor = conn.cursor()
    try:
        # Get event name to use in the filename
        cursor.execute("SELECT event_name FROM EVENTS WHERE event_id = :event_id", {'event_id': event_id})
        result = cursor.fetchone()
        if not result:
            print(f"Cannot export: Event with ID {event_id} not found.")
            return None
        
        event_name = result[0].replace(' ', '_').lower()

        # Fetch the attendance data
        query = """
        SELECT s.student_id, s.name, NVL(a.attended, 'N') AS attendance_status
        FROM REGISTRATIONS r
        JOIN STUDENTS s ON r.student_id = s.student_id
        LEFT JOIN ATTENDANCE a ON r.event_id = a.event_id AND r.student_id = a.student_id
        WHERE r.event_id = :event_id
        ORDER BY s.name
        """
        cursor.execute(query, {'event_id': event_id})
        attendance_data = cursor.fetchall()
        
        if not attendance_data:
            print(f"No registrations found for event ID {event_id}. Nothing to export.")
            return None

        # Define CSV file path
        csv_filename = f"event_{event_id}_{event_name}_attendance.csv"
        full_path = os.path.join(file_path, csv_filename)

        # Write data to CSV
        with open(full_path, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            
            # Write header
            csv_writer.writerow(['Student ID', 'Student Name', 'Attendance Status (Y/N)'])
            
            # Write data rows
            csv_writer.writerows(attendance_data)
        
        print(f"Successfully exported attendance data to {full_path}")
        return full_path

    except Exception as e:
        print(f"Error exporting attendance to CSV for event {event_id}: {e}")
        return None
    finally:
        cursor.close()
        conn.close()


# Example usage (for testing purposes)
if __name__ == '__main__':
    # Assumptions for testing:
    # - Event with ID 1 exists.
    # - Students are registered and some have attendance marked for event 1.
    
    EVENT_ID_TO_TEST = 1

    print(f"--- Testing Reports for Event ID: {EVENT_ID_TO_TEST} ---")

    # Test 1: Get event statistics
    print("\n1. Fetching event statistics...")
    stats = get_event_statistics(EVENT_ID_TO_TEST)
    if stats:
        print(f"   - Total Registered: {stats['registered']}")
        print(f"   - Total Attended: {stats['attended']}")
        print(f"   - Attendance Percentage: {stats['percentage']}%")
    else:
        print("   Could not retrieve statistics.")

    # Test 2: Export attendance to CSV
    print("\n2. Exporting attendance to CSV...")
    # Creating a temporary directory for the export
    export_dir = "temp_exports"
    if not os.path.exists(export_dir):
        os.makedirs(export_dir)
        
    csv_file_path = export_attendance_to_csv(EVENT_ID_TO_TEST, file_path=export_dir)
    if csv_file_path:
        print(f"   CSV export test passed. File created at: {csv_file_path}")
        # You can open the file to verify its contents
    else:
        print("   CSV export test failed.")
