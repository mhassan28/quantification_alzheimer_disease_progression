import streamlit as st
import base64
from pymongo import MongoClient

# MongoDB setup
client = MongoClient("mongodb://localhost:27017")
db = client["MRI_Scan"]
patients_collection = db["Patients"]

def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

def add_local_background(image_path):
    base64_img = get_base64_image(image_path)
    css = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');

    html, body, .stApp {{
        font-family: 'Inter', sans-serif;
        background-image: url("data:image/jpeg;base64,{base64_img}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}

    .form-box {{
        background: rgba(255, 255, 255, 1);
        border-radius: 16px;
        padding: 0px 0px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        border: 8px solid #000;
        max-width: 900px;
        margin: 3rem auto;
    }}

    h2 {{
        color: #111;
        text-align: center;
        font-weight: 800;
        font-size: 2.2rem;
        margin-bottom: 0.5rem;
    }}

    h3 {{
        color: #333;
        text-align: center;
        font-weight: 600;
        margin-bottom: 2rem;
    }}

    label {{
        color: #222 !important;
        font-weight: 600 !important;
    }}

    input, select {{
        border-radius: 8px !important;
        padding: 0.45rem !important;
    }}

    .stButton>button {{
        background-color: #0066cc;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.2rem;
        font-size: 1rem;
        font-weight: 600;
        transition: 0.2s ease-in-out;
    }}

    .stButton>button:hover {{
        background-color: #004d00;
        transform: scale(1.03);
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

def show_patient_form():
    if "patient_form_submitted" not in st.session_state:
        st.session_state["patient_form_submitted"] = False

    if not st.session_state["patient_form_submitted"]:
        st.markdown('''
        <div class="form-box">
            <h2>🧾 Patient Registration Form</h2>
            <h3>👤 Personal Information</h3>
        ''', unsafe_allow_html=True)

        with st.form("patient_form", clear_on_submit=False):
            col1, col2 = st.columns(2)
            with col1:
                patient_id = st.text_input("🆔 Patient ID")
                full_name = st.text_input("👤 Full Name")
                gender = st.selectbox("🚻 Gender", ["Select", "Male", "Female", "Other"])
                age = st.number_input("🎂 Age", min_value=0, max_value=120)

            with col2:
                blood_group = st.selectbox("🩸 Blood Group", ["Select", "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])
                contact = st.text_input("📞 Contact Number (e.g., +92 300 1234567)")
                email = st.text_input("📧 Email Address (e.g., example@gmail.com)")

            submitted = st.form_submit_button("💾 Submit")

        st.markdown("</div>", unsafe_allow_html=True)

        if submitted:
            import re
            phone_pattern = r'^\+92\s\d{3}\s\d{7}$'
            email_pattern = r'^[\w\.-]+@gmail\.com$'

            def show_warning(msg):
                st.markdown(f"""
                    <div style='
                        background-color: #fef08a;
                        padding: 0.75rem 1.25rem;
                        color: black;
                        border-radius: 10px;
                        font-weight: 500;
                        margin-bottom: 0.5rem;
                    '>{msg}</div>
                """, unsafe_allow_html=True)

            if not any([patient_id, full_name, contact, email]) and gender == "Select" and blood_group == "Select" and age == 0:
                show_warning("⚠️ Please enter patient details first.")
            elif not patient_id:
                show_warning("🆔 Please enter Patient ID.")
            elif not patient_id.isdigit():
                show_warning("🆔 Patient ID must be an integer.")
            elif patients_collection.find_one({"patient_id": patient_id}):
                show_warning("❌ Patient ID already exists. Please use a unique ID.")
            elif not full_name:
                show_warning("👤 Please enter Full Name.")
            elif not full_name.replace(" ", "").isalpha():
                show_warning("👤 Full Name must contain only letters.")
            elif gender == "Select":
                show_warning("🚻 Please select a gender.")
            elif age == 0:
                show_warning("🎂 Age must be greater than 0.")
            elif blood_group == "Select":
                show_warning("🩸 Please select a blood group.")
            elif not contact:
                show_warning("📞 Please enter contact number.")
            elif not re.match(phone_pattern, contact):
                show_warning("📞 Contact must be in format: +92 xxx xxxxxxx")
            elif not email:
                show_warning("📧 Please enter email address.")
            elif not re.match(email_pattern, email):
                show_warning("📧 Email must end with @gmail.com")
            else:
                # Save to MongoDB
                patient_data = {
                    "patient_id": patient_id,
                    "full_name": full_name,
                    "gender": gender,
                    "age": age,
                    "blood_group": blood_group,
                    "contact": contact,
                    "email": email
                }
                patients_collection.insert_one(patient_data)

                st.session_state["patient_form_submitted"] = True
                st.session_state["patient_id"] = patient_id
                st.session_state["full_name"] = full_name
                st.session_state["gender"] = gender
                st.session_state["age"] = age
                st.session_state["blood_group"] = blood_group
                st.session_state["contact"] = contact
                st.session_state["email"] = email
                st.session_state["current_page"] = "upload_mri"

                st.markdown("""<div style='background-color: #bbf7d0; padding: 0.75rem 1.25rem; color: black; border-radius: 10px; font-weight: 500; margin-bottom: 1rem;'>✅ Patient details submitted successfully! You can now proceed to upload MRI images.</div>""", unsafe_allow_html=True)

                st.balloons()
                st.rerun()
    else:
        st.markdown("""<div style='background-color: #bbf7d0; padding: 0.75rem 1.25rem; color: black; border-radius: 10px; font-weight: 500; margin-bottom: 1rem;'>✅ Patient form already submitted. Go to the next step to upload MRI images.</div>""", unsafe_allow_html=True)

def main():
    add_local_background("Image/12.jpg")
    show_patient_form()

if __name__ == "__main__":
    main()