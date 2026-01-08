# auth.py
# Handles user authentication and role-based access.

import bcrypt
from . import db

# A simple dictionary to act as a session store for the logged-in user.
# In a real multi-user or web application, a more robust session management
# mechanism would be required (e.g., using a server-side session store or tokens).
# For a single-user desktop app, this is sufficient.
CURRENT_USER_SESSION = {
    'user_id': None,
    'username': None,
    'role': None
}

def hash_password(plain_text_password):
    """Hashes a password using bcrypt."""
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(plain_text_password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')

def verify_password(plain_text_password, hashed_password):
    """Verifies a plain-text password against a hashed password."""
    return bcrypt.checkpw(plain_text_password.encode('utf-8'), hashed_password.encode('utf-8'))

def login(username, password):
    """
    Validates user credentials against the USERS table using hashed passwords.
    If successful, it populates the session and returns the user's role.

    Args:
        username (str): The user's username.
        password (str): The user's plain-text password.

    Returns:
        str: The user's role ('admin' or 'volunteer') if login is successful.
        None: If login fails.
    """
    conn = db.get_connection()
    if not conn:
        return None  # Database connection failed

    cursor = conn.cursor()
    try:
        # Fetch the hashed password from the database
        query = "SELECT user_id, password, role FROM USERS WHERE username = :username"
        cursor.execute(query, {'username': username})
        result = cursor.fetchone()

        if result:
            user_id, hashed_password_from_db, role = result
            # Verify the provided password against the stored hash
            if verify_password(password, hashed_password_from_db):
                # Populate the session
                CURRENT_USER_SESSION['user_id'] = user_id
                CURRENT_USER_SESSION['username'] = username
                CURRENT_USER_SESSION['role'] = role
                print(f"Login successful for user: {username}, Role: {role}")
                return role

        # If user not found or password doesn't match
        print("Invalid username or password.")
        return None
    except Exception as e:
        print(f"An error occurred during login: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

def logout():
    """
    Logs out the current user by clearing the session.
    """
    CURRENT_USER_SESSION['user_id'] = None
    CURRENT_USER_SESSION['username'] = None
    CURRENT_USER_SESSION['role'] = None
    print("User logged out.")

def get_current_role():
    """
    Returns the role of the currently logged-in user.
    """
    return CURRENT_USER_SESSION.get('role')

def is_admin():
    """
    Checks if the current user is an admin.
    """
    return get_current_role() == 'admin'

# Example usage (for testing purposes)
if __name__ == '__main__':
    # This assumes you have a user in your USERS table with a hashed password.
    # To test, you can use the create_user.py script to add a new admin.
    
    # Test successful login
    print("--- Testing Successful Login ---")
    # Replace 'admin123' with the password you used in create_user.py
    user_role = login('admin1', 'admin123')
    if user_role:
        print(f"Logged in with role: {user_role}")
        print(f"Is admin? {is_admin()}")
        print("Current session:", CURRENT_USER_SESSION)
        logout()
        print("Current session after logout:", CURRENT_USER_SESSION)
    else:
        print("Login failed. Make sure you have a user 'admin1' with a hashed password in the USERS table.")

    print("\n--- Testing Failed Login ---")
    user_role = login('admin1', 'wrongpassword')
    if not user_role:
        print("Failed login test passed.")

