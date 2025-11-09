import streamlit as st
import cv2
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
import os
import pydicom
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from PIL import Image
import io
import base64
from show_patient import show_patient_form
from io import BytesIO
from pymongo import MongoClient
from bson.binary import Binary
from datetime import datetime

client = MongoClient("mongodb://localhost:27017")
db = client["MRI_Scan"]
reports_collection = db["Reports"]

if hasattr(tf, "float8_e4m3b11fnuz"):
    del tf.float8_e4m3b11fnuz

MODEL_PATH = "Quantification_Alzheimer_Disease_Progression.h5"
cnn_model = None
if os.path.exists(MODEL_PATH):
    try:
        cnn_model = load_model(MODEL_PATH)
    except Exception as e:
        st.error(f"⚠️ Error Loading Model: {str(e)}")

class_labels = ["Mild Demented", "Moderate Demented", "Non Demented", "Very Mild Demented"]

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if "patient_form_submitted" not in st.session_state:
    st.session_state["patient_form_submitted"] = False

if "current_page" not in st.session_state:
    st.session_state["current_page"] = "patient_form"

def show_patient_form():
    show_patient_form()

def add_background(image_path: str):
    with open(image_path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{encoded}");
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

def show_MRI():
    st.markdown(
        """
        <div style="text-align: center;">
            <div style="
                background-color: #f0f8ff;
                padding: 20px;
                border-radius: 15px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                margin-bottom: 20px;
                border-left: 6px solid #1f77b4;
                display: inline-block;
            ">
                <h2 style="color: #1f77b4; margin: 0;">🧠 Alzheimer's Disease Detection Using MRI Scans</h2>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    add_background("Image/12.jpg") 
    st.image("Image\\Mri.jpg", use_container_width=True)
    st.write("Upload MRI scan images to predict the Alzheimer stage.")

    if cnn_model is None:
        st.error("⚠️ Model not loaded properly.")
    else:
        uploaded_files = st.file_uploader(
            "Choose MRI images...",
            type=["jpg", "png", "jpeg", "dcm"],
            accept_multiple_files=True
        )

        total_confidence_scores = np.zeros(len(class_labels))
        processed_images = []
        final_class = None
        final_confidence = None

        SAVE_DIR = "UploadedImages"
        os.makedirs(SAVE_DIR, exist_ok=True)

        if uploaded_files:
            if len(uploaded_files) > 20:
                st.warning("⚠️ Please upload only up to 20 images.")
            else:
                columns = st.columns(4)
                from datetime import datetime

                for idx, uploaded_file in enumerate(uploaded_files):
                    try:
                        file_ext = uploaded_file.name.split('.')[-1]
                        unique_filename = f"image_{datetime.now().strftime('%Y%m%d%H%M%S%f')}_{idx}.{file_ext}"
                        save_path = os.path.join(SAVE_DIR, unique_filename)

                        with open(save_path, "wb") as f:
                            f.write(uploaded_file.read())
                        uploaded_file.seek(0)

                        if uploaded_file.name.endswith(".dcm"):
                            ds = pydicom.dcmread(uploaded_file)
                            img = ds.pixel_array
                            img = cv2.normalize(img, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
                            if len(img.shape) == 2:
                                img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
                        else:
                            img = cv2.imdecode(np.frombuffer(uploaded_file.read(), np.uint8), 1)
                            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

                        img_resized = cv2.resize(img, (224, 224))
                        img_batch = np.expand_dims(img_resized, axis=0)

                        predictions = cnn_model.predict(img_batch)
                        confidence_scores = predictions[0]
                        total_confidence_scores += confidence_scores

                        with columns[idx % 4]:
                            st.image(img, caption=f"Image {idx+1}", use_container_width=True)

                        processed_images.append(img_resized)

                    except Exception as e:
                        st.error(f"Error processing image {idx+1}: {str(e)}")

                final_class_index = np.argmax(total_confidence_scores)
                final_class = class_labels[final_class_index]
                final_confidence = total_confidence_scores[final_class_index] / len(uploaded_files)

                st.subheader("Final Prediction:")
                st.markdown(f"<h2 style='color:#d9534f; text-align: center;'>{final_class}</h2>", unsafe_allow_html=True)
                st.markdown(f"<h3>Confidence: {final_confidence:.4f}</h3>", unsafe_allow_html=True)

                fig, ax = plt.subplots(figsize=(8, 5))
                ax.bar(class_labels, total_confidence_scores, color=['blue', 'orange', 'green', 'red'])
                ax.set_ylabel("Total Confidence Score")
                ax.set_xlabel("Alzheimer Stages")
                ax.set_title("Overall Prediction Confidence Across Images")
                st.pyplot(fig)

        col1, col2 = st.columns([1, 1])

        with col1:
            if st.button("Back to Patient Information Form", key="logout_btn"):
                st.session_state["current_page"] = "patient_form"
                st.session_state["patient_form_submitted"] = False
                st.rerun()
        
        with col2:
            if st.button("Generate Report", key="report_btn"):
                if not uploaded_files or final_class is None:
                    st.markdown("""
                        <div style='
                            background-color: #fef08a;
                            padding: 0.75rem 1.25rem;
                            color: black;
                            border-radius: 10px;
                            font-weight: 500;
                            margin-bottom: 1rem;
                        '>
                        ⚠️ Please upload MRI images first to generate report.
                        </div>
                    """, unsafe_allow_html=True)

                else:
                    patient_id = st.session_state.get("patient_id")
                    full_name = st.session_state.get("full_name")
                    gender = st.session_state.get("gender")
                    age = st.session_state.get("age")
                    blood_group = st.session_state.get("blood_group")
                    contact = st.session_state.get("contact")
                    email = st.session_state.get("email")

                    buffer = BytesIO()
                    c = canvas.Canvas(buffer, pagesize=letter)
                    width, height = letter

                    c.setFont("Helvetica-Bold", 20)
                    c.setFillColor(colors.darkblue)
                    c.drawCentredString(width / 2, height - 40, "Quantification Alzheimer Disease Progression")
                    c.setFont("Helvetica", 10)
                    c.setFillColor(colors.black)
                    c.drawCentredString(width / 2, height - 60, "Project Number # 51.")
                    c.drawCentredString(width / 2, height - 75, "Sir Syed University of Engineering and Technology")
                    c.drawCentredString(width / 2, height - 90, "Phone: +92 315 5974603 | Email: se21f-018@suet.edu.pk ")

                    c.setFont("Helvetica-Bold", 16)
                    c.setFillColor(colors.green)
                    c.drawCentredString(width / 2, height - 120, "ALZHEIMER MRI SCAN REPORT")

                    c.setFont("Helvetica-Bold", 14)
                    c.setFillColor(colors.darkred)
                    c.drawString(30, height - 150, "Patient Information:")

                    c.setFont("Helvetica", 11)
                    c.setFillColor(colors.black)
                    c.drawString(30, height - 170, f"Patient ID: {patient_id}")
                    c.drawString(400, height - 170, f"Full Name: {full_name}")
                    c.drawString(30, height - 190, f"Gender: {gender}")
                    c.drawString(400, height - 190, f"Age: {age}")
                    c.drawString(30, height - 210, f"Blood Group: {blood_group}")
                    c.drawString(400, height - 210, f"Contact: {contact}")
                    c.drawString(30, height - 230, f"Email: {email}")

                    c.setFont("Helvetica-Bold", 14)
                    c.setFillColor(colors.darkred)
                    c.drawString(30, height - 260, "Result :")

                    c.setFont("Helvetica", 11)
                    c.setFillColor(colors.black)
                    alzheimer_message = (
                        "No signs of Alzheimer’s Disease"
                        if final_class == "Non Demented"
                        else "Indicates presence of Alzheimer’s Disease"
                    )
                    c.drawString(30, height - 280, f"Prediction: {final_class} ({alzheimer_message})")

                    c.setFont("Helvetica-Bold", 14)
                    c.setFillColor(colors.darkblue)
                    c.drawString(30, height - 310, "MRI Image:")

                    y_offset = height - 475
                    for idx, img in enumerate(processed_images[:3]):
                        image_pil = Image.fromarray(img)
                        image_path = f"temp_img_{idx}.png"
                        image_pil.save(image_path)
                        c.drawImage(image_path, 30, y_offset, width=200, height=150)
                        y_offset += 160
                        os.remove(image_path)

                    c.save()
                    buffer.seek(0)
                    pdf_data = buffer.read()

                    reports_collection.insert_one({
                        "patient_id": patient_id,
                        "full_name": full_name,
                        "gender": gender,
                        "age": age,
                        "blood_group": blood_group,
                        "contact": contact,
                        "email": email,
                        "prediction": final_class,
                        "confidence": round(float(final_confidence), 4),
                        "report_pdf": Binary(pdf_data),
                        "created_at": datetime.now()
                    })

                    b64_pdf = base64.b64encode(pdf_data).decode("utf-8")
                    pdf_download_link = f'<a href="data:application/pdf;base64,{b64_pdf}" download="alzheimer_mri_report.pdf">📄 Download Report</a>'
                    st.markdown(pdf_download_link, unsafe_allow_html=True)

def main():
    if st.session_state["current_page"] == "patient_form":
        show_patient_form()
    elif st.session_state["current_page"] == "upload_mri":
        show_MRI()

if __name__ == "__main__":
    main()