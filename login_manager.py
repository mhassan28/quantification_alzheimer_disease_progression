import streamlit as st
from pymongo import MongoClient
from datetime import date
import bcrypt
import base64
import re 

client = MongoClient("mongodb://localhost:27017")
db = client["LoginApp"]
users_collection = db["Users"]

def get_image_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

class LoginManager:
    def __init__(self):
        self.username = ""
        self.password = ""

    def run(self):
        if "page" not in st.session_state:
            st.session_state.page = "login"
        if st.session_state.page == "login":
            self.show_login()
        elif st.session_state.page == "signup":
            self.show_signup()

    def base_styles(self):
        encoded = get_image_base64("image/login.webp")
        st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;500;700&display=swap');

        html, body, [data-testid="stAppViewContainer"] {{
            font-family: 'Poppins', sans-serif;
            background: url("data:image/gif;base64,{encoded}") no-repeat center center fixed;
            background-size: cover;
        }}

        [data-testid="stAppViewContainer"]::before {{
            content: "";
            position: fixed;
            top: 0; left: 0;
            width: 100%; height: 100%;
            background-color: rgba(0,0,0,0.65);
            z-index: -1;
        }}

        .glass-box {{
            margin-top: 0vh;
            background: rgba(255, 255, 255, 0.93);
            border-radius: 20px;
            padding: 0rem 0rem;
            box-shadow: 0 0 25px rgba(0, 0, 0, 0.25);
            animation: fadeIn 0.8s ease;
        }}

        .title {{
            font-size: 2rem;
            font-weight: 700;
            text-align: center;
            color: #111;
            margin-bottom: 2rem;
            text-shadow: 0px 0px 12px #0ff;
        }}

        .stTextInput input, .stDateInput input {{
            border-radius: 25px;
            padding: 0.6rem 1rem;
            font-size: 0.9rem;
            background: rgba(255, 255, 255, 0.98);
        }}
        .stTextInput label, .stDateInput label {{
            font-weight: 600;
            font-size: 1.1rem; 
            color: #fef08a;
            text-shadow: 1px 1px 2px #000;
        }}

        .stButton button {{
            background: linear-gradient(135deg, #38bdf8, #0ea5e9);
            color: Black;
            font-weight: 600;
            font-size: 2rem;
            padding: 0.5rem 1.5rem;
            border: none;
            border-radius: 25px;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.15);
            transition: 0.3s ease-in-out;
        }}

        .stButton button:hover {{
            background: linear-gradient(135deg, #0ea5e9, #0284c7);
            transform: scale(1.04);
        }}

        .form-switch {{
            text-align: center;
            margin-top: 1.2rem;
        }}

        .form-switch button {{
            background: none;
            color: #38bdf8;
            font-weight: bold;
            border: none;
            cursor: pointer;
            font-size: 0.9rem;
        }}

        hr {{
            margin: 1.5rem 0;
            border: 0.5px solid rgba(255,255,255,0.2);
        }}

        @keyframes fadeIn {{
            0% {{ opacity: 0; transform: translateY(-15px); }}
            100% {{ opacity: 1; transform: translateY(0); }}
        }}
        </style>
        """, unsafe_allow_html=True)

    def show_login(self):
        self.base_styles()
        col1, col2, col3 = st.columns([1, 2.5, 1])
        with col2:
            st.markdown('<div class="glass-box"><div class="title">Login to Alzheimer Portal</div>', unsafe_allow_html=True)

            self.username = st.text_input("**Username**", placeholder="Enter your username")
            self.password = st.text_input("**Password**", placeholder="Enter your password", type="password")

            if st.button("Login"):
                self.authenticate(self.username, self.password)

            st.markdown('<hr>', unsafe_allow_html=True)

            with st.container():
                if st.button("Don’t have an account? Create One"):
                    st.session_state.page = "signup"
                    st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)

    def authenticate(self, username, password):
        user = users_collection.find_one({"username": username})
        if user and bcrypt.checkpw(password.encode("utf-8"), user["password"]):
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.markdown("""
                <div style='
                    background-color: #dc2626;
                    padding: 0.75rem 1.25rem;
                    color: white;
                    border-radius: 10px;
                    font-weight: 500;
                    margin-bottom: 1rem;
                '>
                Invalid username or password.
                </div>
                """, unsafe_allow_html=True)

    def show_signup(self):
        self.base_styles()
        col1, col2, col3 = st.columns([1, 2.5, 1])
        with col2:
            st.markdown('<div class="glass-box"><div class="title">Create Your Alzheimer Account</div>', unsafe_allow_html=True)
            with st.form("signup_form"):
                full_name = st.text_input("Full Name")
                new_username = st.text_input("Username")
                email = st.text_input("Email")
                new_password = st.text_input("Password", type="password")
                confirm_password = st.text_input("Confirm Password", type="password")
                dob = st.date_input("Date of Birth", value=date(2000, 1, 1))
                submitted = st.form_submit_button("Sign Up")

                if submitted:
                    self.create_account(full_name, new_username, email, new_password, confirm_password, dob)

            st.markdown('<div class="form-switch">', unsafe_allow_html=True)
            if st.button("Already registered? Login"):
                st.session_state.page = "login"
                st.rerun()
            st.markdown('</div></div>', unsafe_allow_html=True)

    def create_account(self, full_name, username, email, password, confirm_password, dob):
        if not full_name or not username or not email or not password or not confirm_password:
            st.markdown("""
                <div style='
                    background-color: #dc2626;
                    padding: 0.75rem 1.25rem;
                    color: white;
                    border-radius: 10px;
                    font-weight: 500;
                    margin-bottom: 1rem;
                '>
                ❌ Please fill in all the required fields.
                </div>
            """, unsafe_allow_html=True)

        elif not full_name.replace(" ", "").isalpha():
            st.markdown("""
                <div style='
                    background-color: #dc2626;
                    padding: 0.75rem 1.25rem;
                    color: white;
                    border-radius: 10px;
                    font-weight: 500;
                    margin-bottom: 1rem;
                '>
                ❌ Full name should only contain alphabetic characters.
                </div>
            """, unsafe_allow_html=True)

        elif not re.match("^[a-zA-Z0-9]+$", username):
            st.markdown("""
                <div style='
                    background-color: #dc2626;
                    padding: 0.75rem 1.25rem;
                    color: white;
                    border-radius: 10px;
                    font-weight: 500;
                    margin-bottom: 1rem;
                '>
                ❌ Username should only contain letters and numbers (no spaces or special characters).
                </div>
            """, unsafe_allow_html=True)

        elif not email.endswith("@gmail.com"):
            st.markdown("""
                <div style='
                    background-color: #dc2626;
                    padding: 0.75rem 1.25rem;
                    color: white;
                    border-radius: 10px;
                    font-weight: 500;
                    margin-bottom: 1rem;
                '>
                ❌ Only Gmail addresses are accepted (e.g., example@gmail.com).
                </div>
            """, unsafe_allow_html=True)

        elif password != confirm_password:
            st.markdown("""
                <div style='
                    background-color: #dc2626;
                    padding: 0.75rem 1.25rem;
                    color: white;
                    border-radius: 10px;
                    font-weight: 500;
                    margin-bottom: 1rem;
                '>
                ❌ Passwords do not match.
                </div>
            """, unsafe_allow_html=True)

        elif users_collection.find_one({"username": username}):
            st.markdown("""
                <div style='
                    background-color: #dc2626;
                    padding: 0.75rem 1.25rem;
                    color: white;
                    border-radius: 10px;
                    font-weight: 500;
                    margin-bottom: 1rem;
                '>
                ❌ Username already exists.
                </div>
            """, unsafe_allow_html=True)

        elif len(password) < 6:
            st.markdown("""
                <div style='
                    background-color: #fef08a;
                    padding: 0.75rem 1.25rem;
                    color: black;
                    border-radius: 10px;
                    font-weight: 500;
                    margin-bottom: 1rem;
                '>
                ⚠️ Password should be at least 6 characters.
                </div>
            """, unsafe_allow_html=True)

        else:
            hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
            users_collection.insert_one({
                "full_name": full_name,
                "username": username,
                "email": email,
                "password": hashed_pw,
                "dob": dob.strftime("%Y-%m-%d")
            })
            st.markdown("""
                <div style='
                    background-color: #bbf7d0;  /* Light green */
                    padding: 0.75rem 1.25rem;
                    color: black;
                    border-radius: 10px;
                    font-weight: 500;
                    margin-bottom: 1rem;
                '>
                ✅ Account created successfully! Please login.
                </div>
            """, unsafe_allow_html=True)


            st.session_state.page = "login"
            st.rerun()

if __name__ == "__main__":
    LoginManager().run()