import streamlit as st
import time
import json
import os
import random
import pandas as pd


# Paths to data directories
USERS_FILE = './data/users.json'
SUBJECTS_DIR = './data/subjects/'
USER_PROGRESS_DIR = './data/user_progress/'

# Ensure necessary directories exist
os.makedirs(SUBJECTS_DIR, exist_ok=True)
os.makedirs(USER_PROGRESS_DIR, exist_ok=True)

# Utility function to display the title "Avani Academy" on all screens
def show_title():
    st.title("Avani Academy")

# Load users from JSON file
def load_users():
    if not os.path.exists(USERS_FILE):
        return []
    with open(USERS_FILE, 'r') as file:
        return json.load(file)["users"]

# Save users to JSON file
def save_users(users):
    with open(USERS_FILE, 'w') as file:
        json.dump({"users": users}, file, indent=4)

# Function to sign up a new user
def signup_user(new_user):
    users = load_users()
    users.append({"username": new_user, "scores": {}})
    save_users(users)
    st.success(f"User {new_user} signed up successfully!")
    st.session_state["logged_in_user"] = new_user
    st.rerun()  # Trigger a rerun after signup

# Function to load questions for a subject
def load_subject_questions(subject):
    subject_file = os.path.join(SUBJECTS_DIR, f"{subject.lower()}.json")
    if not os.path.exists(subject_file):
        st.error(f"Expected file '{subject_file}' not found.")
        return []
    with open(subject_file, 'r') as file:
        return json.load(file)["questions"]

# Function to load user progress
def load_user_progress(username):
    user_file = os.path.join(USER_PROGRESS_DIR, f"{username}.json")
    if not os.path.exists(user_file):
        return {}
    with open(user_file, 'r') as file:
        return json.load(file)

# Function to save user progress
def save_user_progress(username, progress):
    user_file = os.path.join(USER_PROGRESS_DIR, f"{username}.json")
    with open(user_file, 'w') as file:
        json.dump(progress, file, indent=4)

def login_screen():
    show_title()
    st.subheader("Login or Signup")

    users = load_users()

    if users:
        user_list = [user['username'] for user in users]
        selected_user = st.selectbox("Select your name", options=user_list)

        if st.button("Login"):
            st.session_state["logged_in_user"] = selected_user
            st.success(f"Welcome back, {selected_user}!")
            st.rerun()

    # Smaller font for New User signup
    st.markdown(
        '<p style="font-size: 14px;">New User? Sign up below.</p>',
        unsafe_allow_html=True
    )
    new_username = st.text_input("Enter your name to sign up")
    if st.button("Sign up"):
        if new_username and not any(user['username'] == new_username for user in users):
            signup_user(new_username)
        else:
            st.error("Username already exists or input is empty.")


def subject_selection_screen():
    show_title()
    user = st.session_state["logged_in_user"]
    st.title(f"Welcome, {user}!")
    st.subheader("What would you like to learn today?")

    # Add 'Logout' button
    col1, col2 = st.columns([4, 1])  # Adjust column width to place logout button on the right
    with col2:
        if st.button("Logout"):
            st.session_state.clear()
            st.rerun()

    # Load user scores
    users = load_users()
    user_data = next((u for u in users if u['username'] == user), None)
    if user_data is None:
        st.error("User data not found.")
        return

    # List of subjects
    subjects = ["English", "Maths", "Science", "Social Studies", "Hindi", "Computer Science", "Kannada"]

    # Subject selection
    selected_subject = st.selectbox("Choose a subject", options=subjects)
    if st.button("Start Learning"):
        st.session_state["selected_subject"] = selected_subject
        st.session_state["question_attempts"] = 0  # Reset attempt counter
        st.session_state["current_question"] = None
        st.rerun()

    # Display leaderboard in table format
    st.subheader("Your Scores:")
    scores = user_data.get("scores", {})

    # Create a DataFrame for the table
    score_data = {
        "Subject": subjects,
        "Points": [scores.get(subject, 0) for subject in subjects]
    }
    score_df = pd.DataFrame(score_data)

    # Display the DataFrame as a table
    st.table(score_df)



# Function to get the next question
def get_next_question(username, subject):
    questions = load_subject_questions(subject)
    if not questions:
        st.error("No questions available for this subject.")
        return None

    # Load user progress
    progress = load_user_progress(username)
    attempted_questions = progress.get(subject, {}).get("attempted", {})

    # Separate questions into new, incorrect, and already correctly answered
    new_questions = [q for q in questions if q['id'] not in attempted_questions]
    incorrect_questions = [q for q in questions if q['id'] in attempted_questions and not attempted_questions[q['id']]]
    old_questions = [q for q in questions if q['id'] in attempted_questions and attempted_questions[q['id']]]

    # 30% chance to show an already correctly answered question
    random_number = random.randint(1, 10)

    # Decide whether to show a new question, incorrect question, or an old correct question
    if incorrect_questions and (random.random() < 0.8):  # Prioritize incorrectly answered questions
        # Occasionally revisit an incorrect question
        question = random.choice(incorrect_questions)
        st.session_state["old_question"] = False  # Incorrect questions can update the score
    elif random_number <= 3 and old_questions:  # 30% chance to show an old question
        question = random.choice(old_questions)
        st.session_state["old_question"] = True  # Mark it as an old, correctly answered question
    elif new_questions:
        question = random.choice(new_questions)
        st.session_state["old_question"] = False  # New question, so it can update the score
    else:
        st.success("You've completed all questions for this subject!")
        return None

    return question


# Question and answer screen
def question_screen():
    show_title()
    user = st.session_state["logged_in_user"]
    subject = st.session_state["selected_subject"]
    st.title(f"{subject} Quiz")
    st.write(f"User: {user}")

    # Add 'Home' and 'Logout' buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Home"):
            # Reset session state to go back to home screen
            st.session_state.pop("selected_subject", None)
            st.session_state.pop("current_question", None)
            st.session_state.pop("question_attempts", None)
            st.session_state.pop("question_completed", None)
            st.rerun()
    with col2:
        if st.button("Logout"):
            st.session_state.clear()
            st.rerun()

    # Define a list of color options
    color_options = ['#FFDDC1', '#C1E1C1', '#C1D3FF', '#FFCCCC', '#FFEB99']

    # Load user progress
    progress = load_user_progress(user)
    subject_progress = progress.get(subject, {"attempted": {}})
    attempted_questions = subject_progress["attempted"]

    # Get the current question or fetch a new one
    if st.session_state.get("current_question") is None:
        question = get_next_question(user, subject)
        if question is None:
            st.write("No more questions available.")
            st.write("Return to the Home screen to select another subject.")
            return
        st.session_state["current_question"] = question
        st.session_state["question_attempts"] = 0

        # Select a random background color for the next question
        st.session_state["bg_color"] = random.choice(color_options)
    else:
        question = st.session_state["current_question"]  # Ensure question is always assigned

    # Apply the background color to the question area
    bg_color = st.session_state.get("bg_color", "#FFFFFF")  # Default to white if not set
    st.markdown(
        f"""
        <style>
        .question-area {{
            background-color: {bg_color};
            padding: 10px;
            border-radius: 10px;
        }}
        </style>
        """, unsafe_allow_html=True
    )

    # Display the question inside the question area
    st.markdown('<div class="question-area">', unsafe_allow_html=True)
    st.write(f"**Chapter:** {question.get('chapter', 'Unknown Chapter')}")
    st.write(f"**Question:** {question['question']}")
    options = question['options']
    user_choice = st.radio("Choose an option:", options, key=st.session_state["question_attempts"])
    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("Submit Answer"):
        st.session_state["question_attempts"] += 1
        correct_answer = question['answer']

        if user_choice == correct_answer:
            if st.session_state["old_question"]:
                st.info("Correct! This was a previously answered question, so no points are added.")
            else:
                st.success("Bravo! That is correct.")
                # Update user's score for new or incorrect questions only
                users = load_users()
                for u in users:
                    if u['username'] == user:
                        u.setdefault('scores', {})
                        u['scores'][subject] = u['scores'].get(subject, 0) + 1
                        break
                save_users(users)

            # Update user progress
            attempted_questions[question['id']] = True
            progress[subject] = {"attempted": attempted_questions}
            save_user_progress(user, progress)

            # Move to the next question (and change the color)
            st.session_state["current_question"] = None
            st.session_state["question_attempts"] = 0
            st.rerun()

        else:
            if st.session_state["question_attempts"] < 2:
                st.error("That is not correct. Try again.")
            else:
                st.error("That is not correct. Let's come back to this later.")
                # Update user progress
                attempted_questions[question['id']] = False
                progress[subject] = {"attempted": attempted_questions}
                save_user_progress(user, progress)

                # Move to the next question (and change the color)
                st.session_state["current_question"] = None
                st.session_state["question_attempts"] = 0
                st.rerun()

# Main app flow
if "logged_in_user" not in st.session_state:
    login_screen()
elif "selected_subject" not in st.session_state:
    subject_selection_screen()
else:
    question_screen()

