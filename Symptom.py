import streamlit as st
import base64

def add_bg_from_local(image_path):
    with open(image_path, "rb") as img_file:
        encoded_img = base64.b64encode(img_file.read()).decode()
    st.markdown(
        f"""
        <style>
        html, body, [data-testid="stAppViewContainer"], .stApp {{
            background: url(data:image/jpg;base64,{encoded_img});
            background-size: cover;
            background-attachment: fixed;
            background-repeat: no-repeat;
            background-position: center;
            font-family: 'Segoe UI', sans-serif;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

def alzheimer_symptoms():
    add_bg_from_local("Image/Symptoms1.jpg")
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
        html, body, [data-testid="stAppViewContainer"] {
            font-family: 'Inter', sans-serif;
        }
        .glass-box {
            background: rgba(0, 0, 0, 0.4);
            border-radius: 16px;
            padding: 0px;
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.18);
            margin: 20px auto;
            width: 90%;
            max-width: 900px;
        }
        h1.title {
            text-align: center;
            color: #ffffff;
            font-weight: 700;
        }
        h4.subtitle {
            text-align: center;
            color: 	#003f7f;
            margin-top: -10px;
        }
        .question {
            font-size: 20px;
            font-weight: bold;
            text-align: center;
            color: #000000;
            margin-bottom: 10px;
        }
        .stRadio label {
            font-size: 18px !important;
            font-weight: 600;
            color: #000000;
        }
        .stButton button {
            font-size: 16px;
            font-weight: bold;
            padding: 10px 24px;
            border-radius: 10px;
            background-color: #0066cc;
            color: white;
            transition: 0.3s ease;
        }
        .stButton button:hover {
            background-color: #0066cc;
            transform: scale(1.02);
        }
        .stProgress > div > div > div > div {
            background-color: #2196F3 !important;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('''
    <div class="glass-box">
        <h1 class="title">🧠 Alzheimer Symptoms Checker</h1>
    </div>
    ''', unsafe_allow_html=True)

    st.markdown('<h4 class="subtitle">Answer the following questions. Each image shows a common symptom. Select <strong>Yes</strong> or <strong>No</strong>.</h4>', unsafe_allow_html=True)

    image_urls = [
        "Image/Forgetfulness.jpeg",
        "Image/Planning trouble.jpeg",
        "Image/Confusion.jpg",
        "Image/Misplacing things.jpg",
        "Image/Avoiding social.png",
        "Image/Language problems.jpg",
        "Image/Mood swings.jpg",
        "Image/Daily task issues.jpg",
        "Image/Visual problems.jpg",
        "Image/Poor judgment.jpg"
    ]

    questions = [
        "Do you often forget recent events or conversations?",
        "Do you have trouble planning or solving simple problems?",
        "Do you get confused about dates or places?",
        "Do you misplace things and can’t retrace your steps?",
        "Do you avoid social activities more than before?",
        "Do you struggle to find the right words during conversations?",
        "Have you noticed changes in mood or personality?",
        "Do you find it hard to complete daily tasks you used to do easily?",
        "Do you have trouble understanding visual images or spatial relationships?",
        "Do you make poor judgments more often?"
    ]

    # Initialize session state
    if "answers" not in st.session_state:
        st.session_state.answers = []
    if "current_question" not in st.session_state:
        st.session_state.current_question = 0

    current_question = st.session_state.current_question

    if current_question < len(questions):
        with st.container():
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f'<div class="question">{questions[current_question]}</div>', unsafe_allow_html=True)
                answer = st.radio("Select an option", ["No", "Yes"], key=f"radio_{current_question}")
                
                if st.button("Next Question"):
                    if len(st.session_state.answers) == current_question:
                        st.session_state.answers.append(answer)
                        st.session_state.current_question += 1

            with col2:
                st.image(image_urls[current_question], width=350)

        st.progress((current_question + 1) / len(questions))
        st.markdown('</div>', unsafe_allow_html=True)

    else:
        yes_count = st.session_state.answers.count("Yes")
        st.markdown('<div class="glass-box">', unsafe_allow_html=True)
        st.subheader("Assessment Result")

        if yes_count == 0:
            st.markdown("""
                    <div style='
                        background-color: #bbf7d0;  /* Light green */
                        padding: 0.75rem 1.25rem;
                        color: black;
                        border-radius: 10px;
                        font-weight: 500;
                        margin-bottom: 1rem;
                    '>
                    You did not select any concerning symptoms.
                    </div>
                """, unsafe_allow_html=True)

        elif yes_count <= 3:
            st.markdown("""
                <div style='
                    background-color: #fef08a;
                    padding: 0.75rem 1.25rem;
                    color: black;
                    border-radius: 10px;
                    font-weight: 500;
                    margin-bottom: 1rem;
                '>
                Only a few symptoms selected. May not be a concern, but keep observing.
                </div>
            """, unsafe_allow_html=True)

        elif 4 <= yes_count <= 6:
            st.markdown("""
                <div style='
                    background-color: #ffa726;
                    padding: 0.75rem 1.25rem;
                    color: black;
                    border-radius: 10px;
                    font-weight: 500;
                    margin-bottom: 1rem;
                '>
                Some warning signs detected. It is advisable to consult a doctor.
                </div>
            """, unsafe_allow_html=True)

        else:
            st.markdown("""
                <div style='
                    background-color: #ef5350;
                    padding: 0.75rem 1.25rem;
                    color: white;
                    border-radius: 10px;
                    font-weight: 500;
                    margin-bottom: 1rem;
                '>
                Multiple strong indicators of Alzheimer's. Please consult a medical professional as soon as possible.
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("""
                <div style='
                    background-color: #fef08a;
                    padding: 0.75rem 1.25rem;
                    color: black;
                    border-radius: 10px;
                    font-weight: 500;
                    margin-bottom: 1rem;
                '>
                ⚠️ Note: This is not a medical diagnosis. Please consult a professional for confirmation.
                </div>
            """, unsafe_allow_html=True)

        if st.button("🔁 Go Back to Questions"):
            st.session_state.current_question = 0
            st.session_state.answers = []

        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    alzheimer_symptoms()