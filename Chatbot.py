import streamlit as st
import requests
import json
import base64
import requests.exceptions

def show_Chatbot():
    API_KEY = "AIzaSyDazQY4nfRluyRqYl1wG09DIKewhXHu6SQ"
    API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"

    background_image_path = "Image/12.jpg"
    with open(background_image_path, "rb") as img:
        encoded_image = base64.b64encode(img.read()).decode()

    st.markdown(f"""
        <style>
            .stApp {{
                background-image: url("data:image/jpg;base64,{encoded_image}");
                background-size: cover;
                background-position: center;
                background-attachment: fixed;
            }}
            .main-title {{
                text-align: center;
                color: white;
                font-size: 36px;
                font-weight: bold;
                margin-top: 20px;
                text-shadow: 1px 1px 3px #000000aa;
            }}
            .chat-input textarea {{
                font-size: 16px !important;
                background-color: #ffffffdd;
                border-radius: 10px;
                padding: 12px;
            }}
            .stButton > button {{
                background-color: #0066cc;
                color: white;
                padding: 10px 24px;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                margin-top: 10px;
            }}
            .stButton > button:hover {{
                background-color: #0052a3;
            }}
            .response-box {{
                background-color: #ffffffcc;
                border-left: 5px solid #0066cc;
                border-radius: 10px;
                padding: 15px;
                margin-top: 20px;
                color: #000;
                white-space: pre-wrap;
                font-size: 16px;
            }}
        </style>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div style='
            background: linear-gradient(135deg, #e0f2ff, #b3d9ff);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.3);
            border-radius: 20px;
            padding: 0px;
            margin: 40px auto 30px auto;
            width: 85%;
            box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15);
            text-align: center;
        '>
            <h1 style='
                font-size: 36px;
                color: #004080;
                text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.2);
                margin: 0;
                font-family: "Segoe UI", sans-serif;
            '>🧠 Alzheimer Disease Chatbot</h1>
    """, unsafe_allow_html=True)

    st.markdown("<p style='text-align: center; color: black;'>Ask any question related to Alzheimer's Disease.</p>", unsafe_allow_html=True)

    st.markdown("<div class='chat-input'>", unsafe_allow_html=True)
    user_input = st.text_area("Enter your message:", height=150, key="input")
    st.markdown("</div>", unsafe_allow_html=True)

    if st.button("Send"):
        if user_input.strip() == "":
            st.markdown("""
                <div style='
                    background-color: #fef08a;
                    padding: 0.75rem 1.25rem;
                    color: black;
                    border-radius: 10px;
                    font-weight: 500;
                    margin-bottom: 1rem;
                '>
                 Please enter a question.
                </div>
            """, unsafe_allow_html=True)
        else:
            st.session_state["last_input"] = user_input
            st.session_state["send_request"] = True

    if st.session_state.get("send_request", False):
        st.session_state["send_request"] = False

        headers = {"Content-Type": "application/json"}
        data = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": f"You are a medical assistant focused on Alzheimer's Disease. Answer concisely and professionally.\n\nUser's question: {st.session_state['last_input']}"
                        }
                    ]
                }
            ]
        }

        try:
            response = requests.post(API_URL, headers=headers, data=json.dumps(data), timeout=10)

            if response.status_code == 200:
                try:
                    result = response.json()
                    output_text = result['candidates'][0]['content']['parts'][0]['text']
                    st.markdown(f"<div class='response-box'>{output_text}</div>", unsafe_allow_html=True)
                except Exception:
                    st.markdown("""
                        <div style='
                            background-color: #dc2626;
                            padding: 0.75rem 1.25rem;
                            color: white;
                            border-radius: 10px;
                            font-weight: 500;
                            margin-bottom: 1rem;
                        '>
                        ❌ Failed to parse Gemini's response.
                        </div>
                    """, unsafe_allow_html=True)
                    st.json(result)
            else:
                st.error(f"❌ API Request Failed: {response.status_code}")
                try:
                    st.json(response.json())
                except:
                    st.write(response.text)

        except requests.exceptions.RequestException:
            st.markdown("""
                <div style='
                    background-color: #dc2626;
                    padding: 0.75rem 1.25rem;
                    color: white;
                    border-radius: 10px;
                    font-weight: 500;
                    margin-bottom: 1rem;
                '>
                ❌ Internet connection is unavailable. Please check your connection.
                </div>
            """, unsafe_allow_html=True)