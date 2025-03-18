import streamlit as st
import pandas as pd
import os
import hashlib
import sqlite3
import random
import string
from datetime import datetime

# Page configuration
st.set_page_config(page_title="Course Preference Form", layout="centered")

# Database setup functions
def init_database():
    """Initialize the SQLite database with required tables."""
    conn = sqlite3.connect('course_preferences.db')
    c = conn.cursor()
    
    # Create admin table if it doesn't exist
    c.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            username TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL,
            is_default INTEGER DEFAULT 1
        )
    ''')
    
    # Create submissions table if it doesn't exist
    c.execute('''
        CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            t_pref1 TEXT NOT NULL,
            t_pref2 TEXT NOT NULL,
            t_pref3 TEXT NOT NULL,
            t_pref4 TEXT NOT NULL,
            t_pref5 TEXT NOT NULL,
            l_pref1 TEXT NOT NULL,
            l_pref2 TEXT NOT NULL,
            l_pref3 TEXT NOT NULL,
            remarks TEXT,
            submission_date TEXT NOT NULL
        )
    ''')
    
    # Check if any admin exists
    c.execute("SELECT COUNT(*) FROM admins")
    if c.fetchone()[0] == 0:
        # Generate a random default password
        default_username = "phoffice"
        default_password = "phoffice@206#"
        password_hash = hashlib.sha256(default_password.encode()).hexdigest()
        
        c.execute("INSERT INTO admins (username, password_hash, is_default) VALUES (?, ?, 1)", 
                  (default_username, password_hash))
        
        # Store the default credentials in a file for the admin to see once
        with open('admin_credentials.txt', 'w') as f:
            f.write(f"Initial Admin Username: {default_username}\n")
            f.write(f"Initial Admin Password: {default_password}\n")
            f.write("IMPORTANT: Please log in and change these credentials immediately for security reasons.")
    
    conn.commit()
    conn.close()
    
    return check_default_credentials_exist()

def check_default_credentials_exist():
    """Check if default credentials file exists."""
    return os.path.exists('admin_credentials.txt')

def get_default_credentials():
    """Get the default credentials from the file."""
    if os.path.exists('admin_credentials.txt'):
        with open('admin_credentials.txt', 'r') as f:
            lines = f.readlines()
            username = lines[0].split(': ')[1].strip()
            password = lines[1].split(': ')[1].strip()
        return username, password
    return None, None

def verify_admin(username, password):
    """Verify admin credentials against the database."""
    conn = sqlite3.connect('course_preferences.db')
    c = conn.cursor()
    
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    c.execute("SELECT is_default FROM admins WHERE username = ? AND password_hash = ?", 
              (username, password_hash))
    
    result = c.fetchone()
    conn.close()
    
    if result:
        return True, result[0] == 1
    return False, False

def update_admin_credentials(username, password):
    """Update admin credentials in the database."""
    conn = sqlite3.connect('course_preferences.db')
    c = conn.cursor()
    
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    # Remove existing admin accounts
    c.execute("DELETE FROM admins")
    
    # Insert new admin credentials
    c.execute("INSERT INTO admins (username, password_hash, is_default) VALUES (?, ?, 0)", 
              (username, password_hash))
    
    conn.commit()
    conn.close()
    
    # Remove the default credentials file if it exists
    if os.path.exists('admin_credentials.txt'):
        os.remove('admin_credentials.txt')

def save_submission(name, email, preferences, remarks):
    """Save a new submission to the database."""
    conn = sqlite3.connect('course_preferences.db')
    c = conn.cursor()
    
    c.execute('''
        INSERT INTO submissions (name, email, t_pref1, t_pref2, t_pref3, t_pref4, t_pref5, l_pref1, l_pref2, l_pref3, remarks, submission_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (name, email, preferences[0], preferences[1], preferences[2], 
          preferences[3], preferences[4], preferences[5], preferences[6], preferences[7], remarks,  datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    
    conn.commit()
    conn.close()

def get_all_submissions():
    """Retrieve all submissions from the database."""
    conn = sqlite3.connect('course_preferences.db')
    submissions = pd.read_sql_query("SELECT * FROM submissions", conn)
    conn.close()
    return submissions

# Initialize database on app startup
default_credentials_exist = init_database()

# theory courses
THEORY_COURSES = [
    'EP2100 : Introduction to Engineering Optics',
    'EP2102 : Classical Dynamics',
    'EP2110 : Introduction to Mathematical Physics',
    'EP3110 : Electromagnetics and Applications',
    'EP3120 : Statistical Physics and   Applications',
    'ID5843W : Experimental Techniques for Quantum Computation and Metrology',
    'PHPCL0 : Preparatory Course - Physics Theory',
    'PH1010 : Physics I',
    'PH1020 : Physics II',
    'PH1050 : Foundation of Computational Physics',
    'PH1080 : Thermodynamics and Kinetic Theory',
    'PH2170 : Basic Electronics',
    'PH3051 : Introduction to Astronomy and Astrophysics',
    'PH5010 : Mathematical Physics I',
    'PH5011 : Science and Technology of Solid state',
    'PH5030 : Classical Mechanics',
    'PH5040 : Electronics',
    'PH5050 : Mathematical Physics II',
    'PH5100 : Quantum Mechanics- I',
    'PH5110 : Optics & Photonics',
    'PH5210 : Condensed Matter Physics II',
    'PH5211 : High Energy Physics',
    'PH5310 : Synthesis and Characterization of Functional Materials',
    'PH5320 : Techniques of Characterization of Materials and Physical Measurements',
    'PH5410 : Atomic and Molecular Physics',
    'PH5480 : Quantum Field Theory I',
    'PH5490 : Advanced Statistical Physics',
    'PH5600 : Physics At Low Temperatures',
    'PH5670 : Physics & Tech. of Thin Films',
    'PH5690 : Applied Magnetics',
    'PH5814 : Laser Physics and Applications',
    'PH5820 : Classical Physics',
    'PH5840 : Quantum Computation and Quantum Information',
    'PH5870 : Introduction to General Relativity',
    'PH6021 : Introduction to Research',
    'PH6022 : Introduction to Nanoscience',
    'PH6999 : Special Topics in Physics',
    'PH7080 : Foundations in Theoretical Physics',
    'PH7090 : Foundations of Experimental Physics',
    'PH7999 : Special Topics in Physics'
]

# lab courses
LAB_COURSES = [
    'EP2090 : Engineering Physics Lab I',
    'EP3290 : Engg Physics Lab III',
    'ID5841 : Quantum Computing Lab',
    'PHPCT0: Preparatory Course - Physics Lab',
    'PH1030 : Physics Laboratory I',
    'PH2050 : Physics Lab III',
    'PH5060 : Physics Lab 1 (PG)',
    'PH5270 : Physics Lab III',
    'PH5330 : Laboratory for Synthesis and characterization of Functional Materials'
]


# Show initial admin credentials if they exist
if default_credentials_exist:
    st.warning("⚠️ IMPORTANT: Initial admin credentials have been generated!")
    username, password = get_default_credentials()
    st.info(f"""
    Initial Admin Username: **{username}**  
    Initial Admin Password: **{password}**
    
    **IMPORTANT:** Please log in and change these credentials immediately for security reasons.
    """)

# App mode selector
app_mode = st.sidebar.selectbox("Select Mode", ["Course Selection Panel", "Admin Panel"])

if app_mode == "Course Selection Panel":
    st.title("Course Preference Form")
    st.write(
            '''
            Dear Colleagues,

            [1]. Please use the drop-down menu to register your choice(s) for the July-Nov 2025 teaching semester. At present, how many electives we can offer are still being determined. This will be decided after we find teachers for all the core courses. Please select a minimum of 3 core courses.

            [2]. If you are not available to teach next semester or if you are preparing for a course in another department, please indicate that in the 'Remarks column.'

            Please indicate if your schedule is still being determined, but you may be unavailable partly or wholly. It will not be possible for us to consider such factors later.

            The last date to complete this form is 19 March 2025, before 05.00 PM.

            Please make sure you prefer different choices among each given five (Mandatory) and Three lab courses ( Mandatory )

            Thank you.

            Head of the Department. 
            '''
        )
    
    # Initialize form
    with st.form(key="registration_form"):
        name = st.text_input("Name")
        email = st.text_input("IITM Email")
        
        # Create 5 dropdown selectors for courses with unique options
        st.write("Choose 5 theory courses")
        preferences = []
        for i in range(1, 6):
            course = st.selectbox(
                f"Theory Course Preference {i}",
                options=[""] + THEORY_COURSES,
                key=f"theory_pref_{i}"
            )
            preferences.append(course)
        st.write("Choose 3 lab courses")
        for i in range(1, 4):
            course = st.selectbox(
                f"LAB Course Preference {i}",
                options=[""] + LAB_COURSES,
                key=f"lab_pref_{i}"
            )
            preferences.append(course)
        remarks = st.text_input("Remarks")

            
        submit_button = st.form_submit_button("Submit Preferences")
        
        if submit_button:
            # Validation
            if not name or not email:
                st.error("Name and Email are required fields.")
            elif not all(preferences):
                st.error("Please select all course preferences.")
            elif len(set(preferences)) < 8:
                st.error("Please select unique courses for each preference.")
            else:
                # Save submission to database
                save_submission(name, email, preferences, remarks)
                st.success("Thank you for your submission!")
                st.balloons()
    
elif app_mode == "Admin Panel":
    st.title("Admin Panel")
    
    # Initialize session state for admin authentication
    if 'admin_authenticated' not in st.session_state:
        st.session_state.admin_authenticated = False
        st.session_state.is_default_admin = False
    
    # Admin authentication
    if not st.session_state.admin_authenticated:
        with st.form(key="admin_login"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            login_button = st.form_submit_button("Login")
        
        if login_button:
            authenticated, is_default = verify_admin(username, password)
            if authenticated:
                st.session_state.admin_authenticated = True
                st.session_state.is_default_admin = is_default
                st.success("Authentication successful!")
                st.rerun()
            else:
                st.error("Invalid username or password. Please try again.")
    
    # Change credentials form for default admin
    elif st.session_state.is_default_admin:
        st.warning("⚠️ **SECURITY ALERT**: You are using the default admin credentials.")
        st.info("Please change your username and password immediately.")
        
        with st.form(key="change_credentials"):
            new_username = st.text_input("New Username")
            new_password = st.text_input("New Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            
            change_button = st.form_submit_button("Change Credentials")
            
            if change_button:
                if not new_username or not new_password:
                    st.error("Username and password cannot be empty.")
                elif new_password != confirm_password:
                    st.error("Passwords do not match.")
                elif len(new_password) < 8:
                    st.error("Password must be at least 8 characters long.")
                else:
                    update_admin_credentials(new_username, new_password)
                    st.session_state.admin_authenticated = False
                    st.session_state.is_default_admin = False
                    st.success("Credentials updated successfully! Please log in with your new credentials.")
                    st.rerun()
    
    # Admin panel content
    if st.session_state.admin_authenticated:
        # Display all submissions
        st.header("All Submissions")
        submissions = get_all_submissions()
        
        if not submissions.empty:
            # Display submissions table
            st.dataframe(submissions)
            
            # Download button for CSV
            csv = submissions.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="course_preferences.csv",
                mime="text/csv"
            )
            st.write(f"Total submissions: {len(submissions)}")
            
        else:
            st.info("No submissions yet.")
        
        # Add logout button
        if st.button("Logout"):
            st.session_state.admin_authenticated = False
            st.session_state.is_default_admin = False
            st.rerun()
