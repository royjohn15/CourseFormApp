import streamlit as st
import pandas as pd
import os
import hashlib
from datetime import datetime

# Page configuration
st.set_page_config(page_title="Course Preference Form", layout="centered")

# Initialize session state
if 'submissions' not in st.session_state:
    # Check if data file exists
    if os.path.exists('submissions.csv'):
        st.session_state.submissions = pd.read_csv('submissions.csv')
    else:
        st.session_state.submissions = pd.DataFrame(columns=[
            'Name', 'Email', 'Course Preference 1', 'Course Preference 2', 
            'Course Preference 3', 'Course Preference 4', 'Course Preference 5',
            'Submission Date'
        ])

# Admin password (in production, use environment variables)
ADMIN_PASSWORD = "phoffice@206#"  # Change this to a secure password

# Sample courses
COURSES = [
    "Introduction to Python",
    "Data Science Fundamentals",
    "Web Development with Django",
    "Machine Learning Basics",
    "Advanced Data Structures",
    "Algorithms and Complexity",
    "Database Design",
    "Cloud Computing",
    "Mobile App Development",
    "Cybersecurity Essentials"
]

# Function to hash password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Function to save data
def save_submissions():
    st.session_state.submissions.to_csv('submissions.csv', index=False)

# App mode selector
app_mode = st.sidebar.selectbox("Select Mode", ["Course Selection Panel", "Admin Panel"])

if app_mode == "Course Selection Panel":
    st.title("Course Registration Form")
    
    # Initialize form
    with st.form(key="registration_form"):
        name = st.text_input("Name")
        email = st.text_input("Email")
        
        # Create 5 dropdown selectors for courses with unique options
        preferences = []
        for i in range(1, 6):
            course = st.selectbox(
                f"Course Preference {i}",
                options=[""] + COURSES,
                key=f"pref_{i}"
            )
            preferences.append(course)
            
        submit_button = st.form_submit_button("Submit Registration")
        
        if submit_button:
            # Validation
            if not name or not email:
                st.error("Name and Email are required fields.")
            elif not all(preferences):
                st.error("Please select all course preferences.")
            elif len(set(preferences)) < 5:
                st.error("Please select unique courses for each preference.")
            else:
                # Add submission to dataframe
                new_submission = pd.DataFrame({
                    'Name': [name],
                    'Email': [email],
                    'Course Preference 1': [preferences[0]],
                    'Course Preference 2': [preferences[1]],
                    'Course Preference 3': [preferences[2]],
                    'Course Preference 4': [preferences[3]],
                    'Course Preference 5': [preferences[4]],
                    'Submission Date': [datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
                })
                
                st.session_state.submissions = pd.concat([st.session_state.submissions, new_submission], ignore_index=True)
                save_submissions()
                st.success("Thank you for your submission!")
                st.balloons()
    
elif app_mode == "Admin Panel":
    st.title("Admin Panel")
    
    # Password authentication
    password_input = st.text_input("Enter Admin Password", type="password")
    
    if password_input:
        if hash_password(password_input) == hash_password(ADMIN_PASSWORD):
            st.success("Authentication successful!")
            
            # Display all submissions
            st.header("All Submissions")
            if not st.session_state.submissions.empty:
                st.dataframe(st.session_state.submissions)
                
                # Download button for CSV
                csv = st.session_state.submissions.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name="course_registrations.csv",
                    mime="text/csv"
                )
                st.write(f"Total submissions: {len(st.session_state.submissions)}")
                
                # # Course popularity
                # st.subheader("Course Popularity")
                
                # # Combine all course preferences into one series
                # all_prefs = pd.concat([
                #     st.session_state.submissions['Course Preference 1'],
                #     st.session_state.submissions['Course Preference 2'],
                #     st.session_state.submissions['Course Preference 3'],
                #     st.session_state.submissions['Course Preference 4'],
                #     st.session_state.submissions['Course Preference 5']
                # ])
                
                # course_counts = all_prefs.value_counts()
                # st.bar_chart(course_counts)
                
            else:
                st.info("No submissions yet.")
                
        else:
            st.error("Invalid password. Please try again.")