import streamlit as st
import base64
import time
import json
import os
import random
import pandas as pd
import streamlit.components.v1 as components

# Enable wide mode
st.set_page_config(page_title="Avani Academy", 
                   page_icon='./data/logo.ico', 
                   layout="wide")

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

os.makedirs(SUBJECTS_DIR, exist_ok=True)
os.makedirs(USER_PROGRESS_DIR, exist_ok=True)

def load_users():
    if not os.path.exists(USERS_FILE):
        return []
    with open(USERS_FILE, 'r') as file:
        return json.load(file)["users"]

def save_users(users):
    with open(USERS_FILE, 'w') as file:
        json.dump({"users": users}, file, indent=4)

def user_is_tutor(username):
    """Return True if the user has role == 'tutor' in users.json."""
    users = load_users()
    for u in users:
        if u["username"] == username:
            return u.get("role", "").lower() == "tutor"
    return False

def generate_worksheet_html(questions, subject):
    """
    Builds an HTML snippet with up to 20 questions of two different types:
    1. Multiple choice (10 questions) - options displayed horizontally
    2. Fill in the blanks (10 questions)
    This is for printing on paper (does not show correct answers).
    """
    # Separate questions into the two types
    total_questions = len(questions)
    mc_count = min(10, total_questions)
    blank_count = min(10, max(0, total_questions - mc_count))
    
    mc_questions = questions[:mc_count]
    blank_questions = questions[mc_count:mc_count + blank_count]
    
    html_parts = []
    html_parts.append(f"<h2 class='worksheet-title'>Worksheet - {subject}</h2>")
    html_parts.append("<p>Please complete all questions in each section.</p>")
    
    # Section 1: Multiple Choice with horizontal options
    if mc_questions:
        html_parts.append("<hr><h3>Section 1: Choose the correct option</h3>")
        for i, q in enumerate(mc_questions, start=1):
            question_text = q.get("question", "")
            options = q.get("options", [])
            chapter = q.get("chapter", "Unknown Chapter")
            html_parts.append(f"<div class='question'><p><b>Q{i}. ({chapter})</b> {question_text}</p>")
            
            if isinstance(options, list) and len(options) > 0:
                # Create horizontal options with flexbox
                html_parts.append("<div class='options-container' style='display: flex; flex-wrap: wrap; gap: 15px; margin-top: 10px; margin-bottom: 15px;'>")
                for idx, opt in enumerate(options):
                    option_letter = chr(97 + idx)  # Convert 0, 1, 2, 3 to a, b, c, d
                    html_parts.append(f"<div class='option'><span style='font-weight: bold;'>{option_letter})</span> {opt}</div>")
                html_parts.append("</div>")
            
            html_parts.append("</div>")
    
    # Section 2: Fill in the blanks
    if blank_questions:
        html_parts.append("<hr><h3>Section 2: Fill in the blanks</h3>")
        for i, q in enumerate(blank_questions, start=1):
            question_text = q.get("question", "")
            chapter = q.get("chapter", "Unknown Chapter")
            html_parts.append(f"<div class='question'><p><b>Q{i}. ({chapter})</b> {question_text}</p>")
            html_parts.append("<p>Answer: ____________________</p>")
            html_parts.append("</div>")
    
    # Add some basic styling for print
    html_parts.append("""
    <style>
        @media print {
            body { 
                font-family: Arial, sans-serif; 
            }
            /* Only apply page break for h2 that are NOT the first one */
            h2:not(:first-of-type) { 
                page-break-before: always; 
            }
            .worksheet-title {
                page-break-before: avoid !important; /* Specifically prevent page break before title */
                page-break-after: avoid;
                margin-top: 0;
            }
            .question { 
                margin-bottom: 20px; 
            }
            hr { 
                border: 0.5px solid #ddd; 
            }
            .options-container { 
                break-inside: avoid; /* Prevents option lists from breaking across pages */
            }
            .option {
                min-width: 120px; /* Ensures options have a minimum width */
            }
        }
    </style>
    """)
    
    html_parts.append("<hr>")
    return "\n".join(html_parts)

def generate_worksheet_html2(questions, subject):
    """
    Builds an HTML snippet with up to 20 questions (and their options).
    This is for printing on paper (does not show correct answers).
    """
    html_parts = []
    html_parts.append(f"<h2>Worksheet - {subject}</h2>")
    html_parts.append("<p>Please answer the following questions:</p>")

    for i, q in enumerate(questions, start=1):
        question_text = q.get("question", "")
        options = q.get("options", [])
        chapter = q.get("chapter", "Unknown Chapter")

        html_parts.append(f"<hr><h3>Q{i}. ({chapter})</h3>")
        html_parts.append(f"<p><b>{question_text}</b></p>")
        if isinstance(options, list) and len(options) > 0:
            html_parts.append("<ul>")
            for opt in options:
                html_parts.append(f"<li>{opt}</li>")
            html_parts.append("</ul>")
        else:
            # If there's no options list, you could do a blank line
            html_parts.append("<p>__________</p>")

    html_parts.append("<hr>")
    return "\n".join(html_parts)

def show_left_rail():
    logo_path = './data/logo.png'
    st.sidebar.image(logo_path, caption="Avani Academy", use_container_width=True)
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
    col1, col2 = st.columns([2, 8])

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

    if user_is_tutor(user):
        st.subheader("Tutor Mode - Generate Worksheet")
        if st.button("Create Worksheet"):
            all_questions = load_subject_questions(selected_subject)
            # Pick up to 20 questions randomly
            chosen_20 = random.sample(all_questions, min(20, len(all_questions)))
            # Build HTML and save it in session_state
            st.session_state["worksheet_html"] = generate_worksheet_html(chosen_20, selected_subject)
            st.session_state["show_worksheet"] = True
        
        # If we have generated a worksheet, display it + print button
        if st.session_state.get("show_worksheet"):
            
            component_height = st.slider("Adjust preview height", min_value=600, max_value=2000, value=800, step=100)
            
            components.html(
                f"""
                <html>
                <head>
                    <style>
                        body {{
                            font-family: Arial, sans-serif;
                            padding: 20px;
                        }}
                        .print-button {{
                            position: sticky;
                            bottom: 20px;
                            background-color: #4CAF50;
                            color: white;
                            padding: 10px 20px;
                            border: none;
                            border-radius: 4px;
                            cursor: pointer;
                            font-size: 16px;
                            margin-top: 20px;
                            z-index: 1000;
                        }}
                        .print-button:hover {{
                            background-color: #45a049;
                        }}
                        @media print {{
                            .print-button {{
                                display: none;
                            }}
                        }}
                    </style>
                </head>
                <body>
                    {st.session_state["worksheet_html"]}
                    <button class="print-button" onclick="window.print()">Print Worksheet</button>
                </body>
                </html>
                """,
                height=component_height,
                scrolling=True
            )
        
        if st.button("Logout", key="logout_tutor"):
            st.session_state.clear()
            st.rerun()
    else:
        # If user is a student -> show the old "Start Learning" flow
        st.subheader("Student Mode")
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

        if st.sidebar.button("Logout", key="logout_student"):
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

    # Define a list of color options for question background
    color_options = ['#FFDDC1', '#C1E1C1', '#C1D3FF', '#FFCCCC', '#FFEB99']

    # Load user progress
    progress = load_user_progress(user)
    subject_progress = progress.get(subject, {"attempted": {}})
    attempted_questions = subject_progress["attempted"]

    # Initialize some flags
    if 'button_disabled' not in st.session_state:
        st.session_state['button_disabled'] = False
    if 'question_answered' not in st.session_state:
        st.session_state['question_answered'] = False
    if 'correct_answer' not in st.session_state:
        st.session_state['correct_answer'] = False

    # Get or set current question
    if st.session_state.get("current_question") is None:
        question = get_next_question(user, subject)
        if question is None:
            st.write("No more questions available for this subject.")
            st.write("Session is over. You have completed all available questions.")
            st.session_state.clear()
            st.rerun()

        st.session_state["current_question"] = question
        st.session_state["question_attempts"] = 0
        st.session_state['button_disabled'] = False
        st.session_state['question_answered'] = False
        st.session_state['correct_answer'] = False
        st.session_state["bg_color"] = random.choice(color_options)
    else:
        question = st.session_state["current_question"]

    # Apply a random background color to the question area
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
    user_choice = st.radio("Choose an option:", options, 
                           key=st.session_state["question_attempts"], 
                           label_visibility="collapsed")

    if st.session_state['question_answered']:
        if st.session_state['correct_answer']:
            st.success("Bravo! That is correct.")
            autoplay_audio('./sounds/correct_answer.mp3')
        else:
            st.error("That is not correct. Let's come back to this later.")
            autoplay_audio('./sounds/incorrect_answer.mp3')

        time.sleep(3)

        # Update score only if correct
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
            attempted_questions[question['id']] = False

        # Move to the next question
        st.session_state["current_question"] = None
        st.session_state["question_attempts"] = 0
        st.session_state['question_count'] += 1
        st.session_state['question_answered'] = False
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
            st.session_state['button_disabled'] = True
            st.rerun()

# Main app flow
if "logged_in_user" not in st.session_state:
    login_screen()
elif "selected_subject" not in st.session_state:
    subject_selection_screen()
else:
    question_screen()
