# reports.py
# Generates statistics and handles CSV exports for event attendance.

import csv
import os
from . import db

def get_event_statistics(event_id):
    """
    Calculates attendance statistics for a specific event.
    """
    try:
        with db.get_connection() as conn:
            with conn.cursor() as cursor:
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
                percentage = (total_attended / total_registered) * 100 if total_registered > 0 else 0

                return {
                    'registered': total_registered,
                    'attended': total_attended,
                    'percentage': round(percentage, 2)
                }
    except Exception as e:
        print(f"Error calculating statistics for event {event_id}: {e}")
        return None

def export_attendance_to_csv(event_id, full_file_path):
    """
    Exports the attendance list for an event to a CSV file.
    Expects `full_file_path` to be the complete path including filename.
    """
    try:
        with db.get_connection() as conn:
            with conn.cursor() as cursor:
                # Check if event exists (optional, as registrations check implicitly)
                cursor.execute("SELECT event_name FROM EVENTS WHERE event_id = :event_id", {'event_id': event_id})
                if not cursor.fetchone():
                    return "Error: Event not found."

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
                    return "Info: No registrations found for this event. Nothing to export."

        # Write data to the specified full_file_path
        with open(full_file_path, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(['Student ID', 'Student Name', 'Attendance Status (Y/N)'])
            csv_writer.writerows(attendance_data)
        
        return f"Success: Attendance data exported to {os.path.abspath(full_file_path)}"

    except Exception as e:
        print(f"Error exporting attendance to CSV for event {event_id}: {e}")
        return f"Error: Failed to export attendance data. Reason: {e}"
