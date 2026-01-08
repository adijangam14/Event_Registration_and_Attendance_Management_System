# main.py
# Main entry point for the Event Registration and Attendance System.

from .ui import EventSystemUI

def main():
    """
    Initializes and runs the Tkinter application.
    """
    app = EventSystemUI()
    app.mainloop()

if __name__ == "__main__":
    # To run this application, you would typically run the module:
    # python -m event_system.main
    # This ensures that the relative imports within the package work correctly.
    
    # For direct execution testing, you might need to adjust python path,
    # but the standard is to run it as a module from the parent directory.
    print("Starting the Event Management System...")
    print("Please run this application as a module from the parent directory, for example:")
    print("python -m event_system")

    # The below is a workaround to allow direct execution for simplicity in some environments
    # by adding the parent directory to the path.
    import os
    import sys
    # Adding the parent directory of 'event_system' to the python path
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    
    from event_system.ui import EventSystemUI
    app = EventSystemUI()
    app.mainloop()
