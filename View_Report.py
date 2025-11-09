import streamlit as st
import base64
from pymongo import MongoClient
from bson.binary import Binary

client = MongoClient("mongodb://localhost:27017")
db = client["MRI_Scan"]
reports_collection = db["Reports"]

def add_bg_from_local(image_file):
    with open(image_file, "rb") as img_file:
        encoded_img = base64.b64encode(img_file.read()).decode()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{encoded_img}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

def add_custom_style():
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap');

            html, body, .stApp {
                font-family: 'Poppins', sans-serif;
                color: #1e293b;
            }

            h1, h4 {
                color: #1e3a8a;
                text-align: center;
            }

            .main {
                background: transparent !important;
            }

            .report-container {
                border-radius: 20px;
                padding: 25px;
                background: rgba(255, 255, 255, 0.88);
                backdrop-filter: blur(12px);
                margin-bottom: 30px;
                box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
                transition: transform 0.3s ease, box-shadow 0.3s ease;
                border-left: 6px solid #4f46e5;
            }

            .report-container:hover {
                transform: scale(1.01);
                box-shadow: 0 12px 32px rgba(0, 0, 0, 0.15);
            }

            iframe {
                border: 1px solid #ccc;
                border-radius: 10px;
            }

            .stButton>button {
                background-color: #0066cc;
                color: white;
                border-radius: 8px;
                padding: 10px 24px;
                font-weight: 600;
                border: none;
                transition: background-color 0.3s ease;
                margin-top: 10px;
            }

            .stButton>button:hover {
                background-color: #0066cc;
            }

            .stTextInput>div>div>input {
                border-radius: 8px;
                padding: 10px;
                border: 1px solid #ccc;
            }

            .glass-header {
                background-color: rgba(255, 255, 255, 0.8);
                border-radius: 20px;
                padding: 20px 30px;
                margin: 30px 0;
                box-shadow: 0 6px 16px rgba(0,0,0,0.1);
                text-align: center;
            }

            hr {
                border-top: 1px solid #bbb;
            }
        </style>
    """, unsafe_allow_html=True)

def show_pdf(report, index):
    st.markdown(f"""
        <div class="report-container">
            <h4>
                🧾 Report #{index + 1} - 
                <span style="color: #1d4ed8;">{report.get('full_name', '')}</span> 
                ({report.get('patient_id', '')})
            </h4>
    """, unsafe_allow_html=True)

    if "report_pdf" in report:
        pdf_data = report["report_pdf"]
        base64_pdf = base64.b64encode(pdf_data).decode("utf-8")
        pdf_display = f'''
            <div style="overflow: hidden; border-radius: 10px; border: 1px solid #ccc;">
                <iframe src="data:application/pdf;base64,{base64_pdf}#zoom=90" 
                        width="100%" height="800px" 
                        style="border: none; border-radius: 10px;">
                </iframe>
            </div>
        '''

        st.markdown(pdf_display, unsafe_allow_html=True)

        st.download_button(
            label="📥 Download This Report",
            data=pdf_data,
            file_name=f"{report.get('patient_id', 'report')}_alzheimer_report.pdf",
            mime="application/pdf",
            key=f"download_btn_{index}"
        )

    st.markdown("</div>", unsafe_allow_html=True)

def show_view_report_page():
    st.set_page_config(layout="wide")
    add_bg_from_local("Image/12.jpg")
    add_custom_style()

    st.markdown("""
        <div class='glass-header'>
            <h1>🧠 Alzheimer MRI Report Viewer</h1>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🔎 Search for a Specific Report")
    col_center = st.columns([1, 2, 1])
    with col_center[1]:
        search_by = st.selectbox("Search report by:", ["Patient ID", "Full Name"])
        query_value = st.text_input("Enter Search Term")

        search_clicked = st.button("Search", key="search_button")

        st.markdown("""
            <style>
                #search_button button {
                    font-size: 14px !important;
                    padding: 0.3rem 0.7rem !important;
                    border-radius: 8px !important;
                    width: fit-content !important;
                    background-color: #0066cc !important;
                    color: white !important;
                    border: none !important;
                    transition: all 0.2s ease-in-out;
                }

                #search_button button:hover {
                    background-color: #0066cc !important;
                    transform: scale(1.05);
                }
            </style>
        """, unsafe_allow_html=True)

    if query_value and search_clicked:
        if search_by == "Patient ID":
            query = {"patient_id": query_value}
        else:
            query = {"full_name": {"$regex": f"^{query_value}$", "$options": "i"}}

        reports = list(reports_collection.find(query).sort("created_at", -1))

        st.markdown("""
            <div class='glass-header'>
                <h4>🔍 Matching Report(s)</h4>
            </div>
        """, unsafe_allow_html=True)

        if reports:
            for i, report in enumerate(reports):
                show_pdf(report, i)
        else:
            st.markdown("""
                <div style='
                    background-color: #0066cc;
                    padding: 0.75rem 1.25rem;
                    color: black;
                    border-radius: 10px;
                    font-weight: 500;
                    margin-bottom: 1rem;
                '>
                ⚠️ No matching reports found.
                </div>
            """, unsafe_allow_html=True)

    st.markdown("""
        <div class='glass-header'>
            <h4>📑 All Reports</h4>
        </div>
    """, unsafe_allow_html=True)

    all_reports = list(reports_collection.find().sort("created_at", -1))
    if all_reports:
        for i, report in enumerate(all_reports):
            show_pdf(report, i + 1000)
    else:
        st.markdown("""
            <div style='
                background-color: #e0f2fe;
                padding: 0.75rem 1.25rem;
                color: #003366;
                border-radius: 10px;
                font-weight: 500;
                margin-bottom: 1rem;
                border-left: 6px solid #007acc;
            '>
            ℹ️ No reports available in the database.
            </div>
        """, unsafe_allow_html=True)