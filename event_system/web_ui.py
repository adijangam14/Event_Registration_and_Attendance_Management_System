from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file
from event_system import auth, events, registrations, attendance, reports, email_utils
import datetime
import os

app = Flask(__name__, template_folder='templates')
app.secret_key = os.urandom(24)

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = auth.login(username, password)
        if role:
            session['username'] = username
            session['role'] = role
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    auth.logout()
    session.pop('username', None)
    session.pop('role', None)
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', username=session['username'], role=session['role'])

@app.route('/events', methods=['GET', 'POST'])
def events_page():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        if session.get('role') != 'admin':
            flash('You are not authorized to create events.', 'danger')
            return redirect(url_for('events_page'))
        
        event_name = request.form['event_name']
        event_date = request.form['event_date']
        event_time = request.form['event_time']
        venue = request.form['venue']
        total_slots = int(request.form['total_slots'])
        
        event_date = datetime.datetime.strptime(event_date, '%Y-%m-%d').date()
        
        if events.create_event(event_name, event_date, event_time, venue, total_slots):
            flash('Event created successfully!', 'success')
        else:
            flash('Failed to create event.', 'danger')
        
        return redirect(url_for('events_page'))

    all_events = events.get_all_events()
    return render_template('events.html', events=all_events, role=session.get('role'))

@app.route('/registrations', methods=['GET', 'POST'])
def registrations_page():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        if session.get('role') != 'admin':
            flash('You are not authorized to register students.', 'danger')
            return redirect(url_for('registrations_page'))

        event_id = int(request.form['event_id'])
        student_id = request.form['student_id']

        result = registrations.register_student_for_event(event_id, student_id)

        if "Success" in result:
            flash(result, 'success')
        elif "Info" in result:
            flash(result, 'info')
        else:
            flash(result, 'danger')
        
        return redirect(url_for('registrations_page', event_id=event_id))

    all_events = events.get_all_events()
    selected_event_id = request.args.get('event_id', type=int)
    registered_students = []
    if selected_event_id:
        registered_students = registrations.get_registered_students(selected_event_id)

    return render_template('registrations.html', events=all_events, registered_students=registered_students, selected_event_id=selected_event_id, role=session.get('role'))

@app.route('/attendance', methods=['GET', 'POST'])
def attendance_page():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        event_id = int(request.form['event_id'])
        student_id = request.form['student_id']
        status = request.form['status']

        result = attendance.mark_attendance(event_id, student_id, status)

        if "Success" in result:
            flash(result, 'success')
        else:
            flash(result, 'danger')
        
        return redirect(url_for('attendance_page', event_id=event_id))

    all_events = events.get_all_events()
    selected_event_id = request.args.get('event_id', type=int)
    attendance_list = []
    if selected_event_id:
        attendance_list = attendance.get_event_attendance(selected_event_id)

    return render_template('attendance.html', events=all_events, attendance_list=attendance_list, selected_event_id=selected_event_id)

@app.route('/reports', methods=['GET'])
def reports_page():
    if 'username' not in session:
        return redirect(url_for('login'))

    all_events = events.get_all_events()
    selected_event_id = request.args.get('event_id', type=int)
    stats = None
    if selected_event_id:
        stats = reports.get_event_statistics(selected_event_id)

    return render_template('reports.html', events=all_events, stats=stats, selected_event_id=selected_event_id)

@app.route('/reports/export/<int:event_id>')
def export_csv(event_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    path = reports.export_attendance_to_csv(event_id)
    if path:
        return send_file(path, as_attachment=True)
    else:
        flash('Could not export the report.', 'danger')
        return redirect(url_for('reports_page'))

@app.route('/emails', methods=['GET', 'POST'])
def emails_page():
    if 'username' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))

    if request.method == 'POST':
        event_id = int(request.form['event_id'])
        subject = request.form['subject']
        body = request.form['body']
        
        event_details = events.get_event_details(event_id)
        if not event_details:
            flash("Error: Could not retrieve event details.", 'danger')
            return redirect(url_for('emails_page'))

        _, event_name, _, _, _, _ = event_details

        if 'send_test' in request.form:
            recipient = EMAIL_CONFIG.get("sender_email")
            if not recipient or recipient == "your_email@example.com":
                flash("Please configure 'sender_email' in config.py for testing.", 'danger')
                return redirect(url_for('emails_page'))
            
            email_utils.send_email(recipient, f"TEST: {subject}", body)
            flash(f"Test email sent to {recipient}", 'success')
        else:
            registered_students_data = registrations.get_registered_students(event_id)
            if not registered_students_data:
                flash("No students are registered for this event.", 'warning')
                return redirect(url_for('emails_page'))

            recipients = [student[2] for student in registered_students_data if student[2]]
            if not recipients:
                flash("No valid email addresses found for registered students.", 'warning')
                return redirect(url_for('emails_page'))
            
            email_utils.send_emails_in_background(recipients, subject, body)
            flash(f"Emails are being sent to {len(recipients)} recipients in the background.", 'info')

        return redirect(url_for('emails_page'))

    all_events = events.get_all_events()
    return render_template('emails.html', events=all_events)







if __name__ == '__main__':
    app.run(debug=True)
