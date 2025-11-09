import streamlit as st
from PIL import Image
from MRI_Scan import show_MRI
from Chatbot import show_Chatbot
from hippocampus_size import show_Size
from Tips import show_Tips
from View_Report import show_view_report_page
from show_patient import add_local_background
from Symptom import alzheimer_symptoms
import base64
from io import BytesIO

def set_background(image_file):
    with open(image_file, "rb") as image:
        encoded = base64.b64encode(image.read()).decode()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{encoded}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

def apply_advanced_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Montserrat', sans-serif;
    }

    .card {
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.25);
        border-radius: 15px;
        padding: 15px;
        margin: 10px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        text-align: center;
    }

    .card:hover {
        transform: scale(1.02);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4);
    }

    .card img {
        border-radius: 10px;
        width: 100%;
        height: auto;
        margin-bottom: 10px;
    }

    .card-title {
        font-size: 20px;
        font-weight: 600;
        color: #000;
        margin-bottom: 10px;
    }

    .card-desc {
        font-size: 14px;
        color: #333;
        padding: 0 5px;
    }

    .stButton>button {
        background: #0066cc;
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 10px;
        font-size: 14px;
        transition: background 0.3s ease;
        margin-top: 10px;
    }

    .stButton>button:hover {
        background: #1c4e80;
        transform: scale(1.03);
    }

    .welcome-box {
        background: rgba(255, 255, 255, 0.3);
        backdrop-filter: blur(15px);
        padding: 20px;
        border-radius: 25px;
        margin: 40px auto;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.25);
        text-align: center;
        border: 4px solid #000;
        max-width: 900px;
    }

    .welcome-box h1 {
        font-size: 36px;
        color: #000;
        margin: 0;
    }
    </style>
    """, unsafe_allow_html=True)
def show_home():
    import streamlit as st
    st.title("Welcome to the Home Page")
    st.write("This is the homepage of your Alzheimer Detection System.")

    set_background("image/12.jpg")
    apply_advanced_css()

    st.markdown("""<div class="welcome-box"><h1>🧠 Welcome to Dashboard</h1></div>""", unsafe_allow_html=True)

    features = [
        {"title": "Symptom Checker", "image": "image/Symptom Checker.jpg", "description": "Check your symptoms related to Alzheimer’s."},
        {"title": "MRI Scan", "image": "image/Mri.jpg", "description": "View MRI scan results and detailed AI-based brain analysis."},
        {"title": "Hippocampus size", "image": "image/hippocampus.jpg", "description": "Calculate the size of hippocampus from MRI scans."},
        {"title": "Chatbot Alzheimer", "image": "image/chatbot.jpg", "description": "Interact with our AI-powered Alzheimer’s chatbot."},
        {"title": "View Report", "image": "image/report.jpeg", "description": "Access your previous MRI and diagnosis reports."},
        {"title": "Healthy Brain Tips", "image": "image/tips.jpg", "description": "Daily tips to keep your brain healthy and active."}
    ]

    cols = st.columns(3)

    for idx, feature in enumerate(features):
        col = cols[idx % 3]
        with col:
            try:
                img = Image.open(feature["image"])
                resized_img = img.resize((300, 150))
                buffer = BytesIO()
                resized_img.save(buffer, format="JPEG")
                img_str = base64.b64encode(buffer.getvalue()).decode()
                img_html = f'<img src="data:image/jpeg;base64,{img_str}" class="card-img">'
            except:
                img_html = '<p style="color:red;">Image not found</p>'

            card_html = f"""
                <div class="card">
                    <div class="card-title">{feature['title']}</div>
                    {img_html}
                    <div class="card-desc">{feature['description']}</div>
                </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)

            st.markdown('<div style="text-align: center;">', unsafe_allow_html=True)
            if st.button(f"🚀 View {feature['title']}", key=feature["title"]):
                st.session_state["page"] = feature["title"]
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)