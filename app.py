import streamlit as st
import base64
import time
import json
import os
import random
import pandas as pd
import threading

# Enable wide mode
st.set_page_config(page_title="Avani Academy", page_icon='./data/logo.ico', layout="wide")

import streamlit as st

def show_video_list():
    st.write("Computer Science")
    
    chapters = {
        "How a computer works": {
            "Working of a Computer": "https://qrassets.s3.ap-south-1.amazonaws.com/videoplayertemplate/index.html?videofile=https://qrassets.s3.ap-south-1.amazonaws.com/Terabytes/TB3/Chapter1/tb3ch1svid1/master.m3u8",
            "Hardware and Software" : "https://qrassets.s3.ap-south-1.amazonaws.com/videoplayertemplate/index.html?videofile=https://qrassets.s3.ap-south-1.amazonaws.com/Terabytes/TB3/Chapter1/tb3ch1svid2/master.m3u8"
        },
        "Windows 10 Operating System": {
            "Operating System" : "https://qrassets.s3.ap-south-1.amazonaws.com/videoplayertemplate/index.html?videofile=https://qrassets.s3.ap-south-1.amazonaws.com/Terabytes/TB3/Chapter2/tb3ch2svid1/master.m3u8",
            "Desktop and its components" : "https://qrassets.s3.ap-south-1.amazonaws.com/videoplayertemplate/index.html?videofile=https://qrassets.s3.ap-south-1.amazonaws.com/Terabytes/TB3/Chapter2/tb3ch2anm1/master.m3u8",
            "Parts of a program Window" : "https://qrassets.s3.ap-south-1.amazonaws.com/videoplayertemplate/index.html?videofile=https://qrassets.s3.ap-south-1.amazonaws.com/Terabytes/TB3/Chapter2/tb3ch2svid2/master.m3u8"
        },
        "Enhance a Drawing with Paint tools" : {
            "Working with paint tools" : "https://qrassets.s3.ap-south-1.amazonaws.com/videoplayertemplate/index.html?videofile=https://qrassets.s3.ap-south-1.amazonaws.com/Terabytes/TB3/Chapter3/tb3ch3sr1/master.m3u8",
            "Rotating a picture" : "https://qrassets.s3.ap-south-1.amazonaws.com/videoplayertemplate/index.html?videofile=https://qrassets.s3.ap-south-1.amazonaws.com/Terabytes/TB3/Chapter3/tb3ch3sr2/master.m3u8",
            "Printing a picture" : "https://qrassets.s3.ap-south-1.amazonaws.com/videoplayertemplate/index.html?videofile=https://qrassets.s3.ap-south-1.amazonaws.com/Terabytes/TB3/Chapter3/tb3ch3svid1/master.m3u8"
        }
    }
    
    for chapter, videos in chapters.items():
        st.markdown(f"### {chapter}")
        for name, url in videos.items():
            st.markdown(
                f'<a href="{url}" target="_blank">{name}</a>',
                unsafe_allow_html=True
            )

# Function to play audio using base64 encoding
def autoplay_audio(file_path: str):
    with open(file_path, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        md = f"""
            <audio autoplay="true">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """
        st.markdown(md, unsafe_allow_html=True)

# Paths to data directories
USERS_FILE = './data/users.json'
SUBJECTS_DIR = './data/subjects/'
USER_PROGRESS_DIR = './data/user_progress/'
AVATAR_FILE = './data/avatar.png'

# Ensure necessary directories exist
os.makedirs(SUBJECTS_DIR, exist_ok=True)
os.makedirs(USER_PROGRESS_DIR, exist_ok=True)

def show_left_rail():
    logo_path = './data/logo.png'
    st.sidebar.image(logo_path, caption="Avani Academy", use_column_width=True)
    if "logged_in_user" in st.session_state:
        user = st.session_state["logged_in_user"]
        st.sidebar.subheader(f"User: {user}")
        
        avatar_path = f"./data/{user}.png"
        avatar_path = avatar_path.lower()
        if os.path.exists(avatar_path):
            st.sidebar.image(avatar_path, caption="User Avatar", width=80)

        if "selected_subject" in st.session_state:
            subject = st.session_state["selected_subject"]
            users = load_users()
            user_data = next((u for u in users if u['username'] == user), None)
            if user_data:
                score = user_data.get("scores", {}).get(subject, 0)
                st.sidebar.markdown(f"**{subject} Score: {score}**")

def load_users():
    if not os.path.exists(USERS_FILE):
        return []
    with open(USERS_FILE, 'r') as file:
        return json.load(file)["users"]

def save_users(users):
    with open(USERS_FILE, 'w') as file:
        json.dump({"users": users}, file, indent=4)

def signup_user(new_user):
    users = load_users()
    users.append({"username": new_user, "scores": {}})
    save_users(users)
    st.success(f"User {new_user} signed up successfully!")
    st.session_state["logged_in_user"] = new_user
    st.rerun()  # Trigger a rerun after signup

def load_subject_questions(subject):
    subject_file_name = subject.lower().replace(" ", "_")
    subject_file = os.path.join(SUBJECTS_DIR, f"{subject_file_name}.json")
    if not os.path.exists(subject_file):
        st.error(f"Expected file '{subject_file}' not found.")
        return []
    with open(subject_file, 'r') as file:
        return json.load(file)["questions"]

def load_user_progress(username):
    user_file = os.path.join(USER_PROGRESS_DIR, f"{username}.json")
    if not os.path.exists(user_file):
        return {}
    with open(user_file, 'r') as file:
        return json.load(file)

def save_user_progress(username, progress):
    user_file = os.path.join(USER_PROGRESS_DIR, f"{username}.json")
    with open(user_file, 'w') as file:
        json.dump(progress, file, indent=4)


def login_screen():
    logo_path = './data/logo.png'
    col1, col2 = st.columns([1, 9])

    with col1:
        st.image(logo_path, width=150)

    with col2:
        st.title("Avani Academy")


    users = load_users()

    if users:
        selected_user = None
        total_columns = 2 + len(users) + 2
        cols = st.columns(total_columns)

        for idx, user in enumerate(users):
            avatar_path = f"./data/{user['username']}.png"
            avatar_path = avatar_path.lower()

            # The user avatars start from the 3rd column (idx+2)
            with cols[idx + 2]:  # Shift index by 2 to skip the first 2 padding columns
                if os.path.exists(avatar_path):
                    # Display the avatar image with a button for login
                    st.image(avatar_path, caption=user['username'], width=150)
                    if st.button(f"{user['username']}", key=user['username']):
                        st.session_state["logged_in_user"] = user['username']
                        st.success(f"Welcome back, {user['username']}!")
                        st.rerun()

    show_video_list()


def subject_selection_screen():
    show_left_rail()
    user = st.session_state["logged_in_user"]
    
    st.title(f"Welcome, {user}!")
    st.subheader("What would you like to learn today?")
    
    # Load user scores
    users = load_users()
    user_data = next((u for u in users if u['username'] == user), None)
    if user_data is None:
        st.error("User data not found.")
        return

    subjects = ["English", "Maths", "Science", "Social Studies", "Computer Science", "Hindi", "Kannada"]
    selected_subject = st.selectbox("Choose a subject", options=subjects)
    
    if st.button("Start Learning"):
        st.session_state["selected_subject"] = selected_subject
        st.session_state["question_attempts"] = 0  # Reset attempt counter
        st.session_state["current_question"] = None
        st.rerun()

    scores = user_data.get("scores", {})

    # Create a DataFrame for the table
    score_data = {
        "Subject": subjects,
        "Points": [scores.get(subject, 0) for subject in subjects]
    }
    score_df = pd.DataFrame(score_data)
    st.sidebar.subheader("Your Scores:")
    st.sidebar.table(score_df)

    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.rerun()


# Function to get the next question
def get_next_question(username, subject):
    questions = load_subject_questions(subject)
    if not questions:
        st.error("No questions available for this subject.")
        return None

    # Load user progress
    progress = load_user_progress(username)
    attempted_questions = progress.get(subject, {}).get("attempted", {})

    # Separate questions into new and incorrect questions
    new_questions = [q for q in questions if q['id'] not in attempted_questions]
    incorrect_questions = [q for q in questions if q['id'] in attempted_questions and not attempted_questions[q['id']]]

    # Prioritize incorrectly answered questions
    if incorrect_questions:
        question = random.choice(incorrect_questions)
        st.session_state["old_question"] = False  # Incorrect questions can update the score
    elif new_questions:
        question = random.choice(new_questions)
        st.session_state["old_question"] = False  # New question, so it can update the score
    else:
        st.success("You've completed all questions for this subject!")
        return None

    return question

def get_next_question_fancy(username, subject):
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


def question_screen():
    show_left_rail()
    user = st.session_state["logged_in_user"]
    subject = st.session_state["selected_subject"]

    if 'question_count' not in st.session_state:
        st.session_state['question_count'] = 0  # Start with 0 questions

    st.sidebar.markdown(f"**Questions answered: {st.session_state['question_count']} / 20**")

    if st.session_state['question_count'] >= 20:
        st.error("Session is over. You have answered 20 questions. Logging out...")
        st.session_state.clear()
        st.rerun()

    # Add 'Home' and 'Logout' buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Home"):
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

    # Initialize a flag to control button state if not set
    if 'button_disabled' not in st.session_state:
        st.session_state['button_disabled'] = False
    if 'question_answered' not in st.session_state:
        st.session_state['question_answered'] = False
    if 'correct_answer' not in st.session_state:
        st.session_state['correct_answer'] = False  # Track if the current answer is correct

    # Get the current question or fetch a new one
    if st.session_state.get("current_question") is None:
        question = get_next_question(user, subject)
        
        if question is None:
            st.write("No more questions available for this subject.")
            st.write("Session is over. You have completed all available questions.")
            st.session_state.clear()
            st.rerun()

        st.session_state["current_question"] = question
        st.session_state["question_attempts"] = 0
        st.session_state['button_disabled'] = False  # Enable the button for the new question
        st.session_state['question_answered'] = False  # Reset answer flag
        st.session_state['correct_answer'] = False  # Reset correctness flag

        # Select a random background color for the next question
        st.session_state["bg_color"] = random.choice(color_options)
    else:
        question = st.session_state["current_question"]

    # Apply the background color to the question area
    bg_color = st.session_state.get("bg_color", "#FFFFFF")
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
    st.markdown(
        f"""
        <div style='font-size: 2em; font-weight: bold;'>
            Question: {question['question']}
        </div>
        """,
        unsafe_allow_html=True
    )
    options = question['options']

    # Inject CSS to make the radio label and options larger
    st.markdown(
        """
        <style>
        .radio-label {
            font-size: 1.5em;
            font-weight: bold;
        }
        .stRadio > div {
            font-size: 1.2em;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown("<div class='radio-label'>Choose an option:</div>", unsafe_allow_html=True)
    user_choice = st.radio("Choose an option:", options, key=st.session_state["question_attempts"], label_visibility="collapsed")

    # Handle the submit button logic
    if st.session_state['question_answered']:
        # Show the success/failure message and play the appropriate sound, then move to the next question
        if st.session_state['correct_answer']:
            st.success("Bravo! That is correct.")
            autoplay_audio('./sounds/correct_answer.mp3')
        else:
            st.error("That is not correct. Let's come back to this later.")
            autoplay_audio('./sounds/incorrect_answer.mp3')

        time.sleep(3)  # Pause for 3 seconds

        # Only update user's score and progress if the answer is correct
        if st.session_state['correct_answer']:
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
        else:
            attempted_questions[question['id']] = False  # Mark the question as incorrect

        # Move to the next question
        st.session_state["current_question"] = None
        st.session_state["question_attempts"] = 0
        st.session_state['question_count'] += 1  # Increment question count
        st.session_state['question_answered'] = False  # Reset flag
        st.rerun()

    else:
        if st.button("Submit Answer"):
            # Check if the selected answer is correct
            if user_choice == question['answer']:
                st.session_state['correct_answer'] = True
            else:
                st.session_state['correct_answer'] = False

            # Set the flag and rerun to display the result
            st.session_state['question_answered'] = True
            st.session_state['button_disabled'] = True  # Disable button immediately
            st.rerun()

# Main app flow
if "logged_in_user" not in st.session_state:
    login_screen()
elif "selected_subject" not in st.session_state:
    subject_selection_screen()
else:
    question_screen()
