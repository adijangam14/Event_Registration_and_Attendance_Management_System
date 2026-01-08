# events.py
# Handles event creation and listing.

from . import db
from . import auth
import datetime

def create_event(event_name, event_date, venue, total_slots):
    """
    Creates a new event and saves it to the database.
    This action is restricted to admin users.

    Args:
        event_name (str): The name of the event.
        event_date (datetime.date): The date of the event.
        venue (str): The location of the event.
        total_slots (int): The total number of available slots.

    Returns:
        bool: True if the event was created successfully, False otherwise.
    """
    if not auth.is_admin():
        print("Authorization Error: Only admins can create events.")
        return False

    conn = db.get_connection()
    if not conn:
        return False

    cursor = conn.cursor()
    try:
        query = """
        INSERT INTO EVENTS (event_name, event_date, venue, total_slots)
        VALUES (:event_name, :event_date, :venue, :total_slots)
        """
        cursor.execute(query, {
            'event_name': event_name,
            'event_date': event_date,
            'venue': venue,
            'total_slots': total_slots
        })
        conn.commit()
        print(f"Successfully created event: {event_name}")
        return True
    except Exception as e:
        print(f"Error creating event: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

def get_all_events():
    """
    Retrieves a list of all events from the database.

    Returns:
        list: A list of tuples, where each tuple represents an event
              (event_id, event_name, event_date, venue, total_slots).
              Returns an empty list if no events are found or an error occurs.
    """
    conn = db.get_connection()
    if not conn:
        return []

    cursor = conn.cursor()
    try:
        query = "SELECT event_id, event_name, event_date, venue, total_slots FROM EVENTS ORDER BY event_date DESC"
        cursor.execute(query)
        events = cursor.fetchall()
        return events
    except Exception as e:
        print(f"Error fetching events: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def get_event_details(event_id):
    """
    Retrieves details for a single event from the database.

    Args:
        event_id (int): The ID of the event to retrieve.

    Returns:
        tuple: A tuple representing the event (event_id, event_name, event_date, venue, total_slots)
               or None if the event is not found or an error occurs.
    """
    conn = db.get_connection()
    if not conn:
        return None

    cursor = conn.cursor()
    try:
        query = "SELECT event_id, event_name, event_date, venue, total_slots FROM EVENTS WHERE event_id = :event_id"
        cursor.execute(query, {'event_id': event_id})
        event = cursor.fetchone()
        return event
    except Exception as e:
        print(f"Error fetching event details for event_id {event_id}: {e}")
        return None
    finally:
        cursor.close()
        conn.close()


# Example usage (for testing purposes)
if __name__ == '__main__':
    # --- Test Case 1: Create event as an Admin ---
    # To test this, we first need to log in as an admin.
    print("--- Logging in as admin to test event creation ---")
    auth.login('admin', 'adminpass')
    
    if auth.is_admin():
        print("\n--- Testing Event Creation (as Admin) ---")
        # Creating a sample event
        event_created = create_event(
            'Annual Tech Symposium',
            datetime.date(2024, 10, 25),
            'Main Auditorium',
            150
        )
        if event_created:
            print("Event creation test passed.")
        else:
            print("Event creation test failed.")
    else:
        print("Could not test event creation because admin login failed.")
        print("Ensure you have an 'admin' user with password 'adminpass'.")

    # --- Test Case 2: Attempt to create event as a non-admin ---
    auth.logout() # Log out admin
    print("\n--- Logging in as volunteer to test event creation restriction ---")
    # This assumes a 'volunteer' user exists, e.g.,
    # INSERT INTO USERS (user_id, username, password, role) 
    # VALUES ('volunteer01', 'volunteer', 'volunteerpass', 'volunteer');
    auth.login('volunteer', 'volunteerpass')

    if not auth.is_admin() and auth.get_current_role() == 'volunteer':
        print("\n--- Testing Event Creation (as Volunteer) ---")
        event_created = create_event(
            'Unauthorized Event',
            datetime.date(2024, 11, 15),
            'Secret Location',
            50
        )
        if not event_created:
            print("Test passed: Volunteer was correctly prevented from creating an event.")
        else:
            print("Test failed: Volunteer was able to create an event.")
    auth.logout()


    # --- Test Case 3: Fetch all events ---
    print("\n--- Testing Fetching All Events ---")
    all_events = get_all_events()
    if all_events:
        print("Successfully fetched events:")
        for event in all_events:
            print(event)
    else:
        print("No events found or an error occurred. If you just created an event, there might be an issue.")

