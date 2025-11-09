import streamlit as st
st.set_page_config(page_title="Quantification Alzheimer Disease Progression", page_icon="🧠", layout="wide")
from home import set_background
from show_patient import add_local_background

from home import show_home
import cv2
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
import matplotlib.pyplot as plt
import os
import pydicom
import pandas as pd
from fuzzywuzzy import fuzz
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from home import show_home
from MRI_Scan import show_MRI
from Chatbot import show_Chatbot
from hippocampus_size import show_Size
from Tips import show_Tips
from login_manager import LoginManager
from show_patient import show_patient_form
from View_Report import show_view_report_page
from Symptom import alzheimer_symptoms
from PIL import Image






st.markdown("""
    <style>
        .main { background-color: #F9F3FD; }
        h1 { color: #003366; }
        .stButton>button { background-color: #0073e6; color: white; }
    </style>
""", unsafe_allow_html=True)

page_options = ["Dashboard", "Symptom Checker", "MRI Scan", "Hippocampus size", 
                "Chatbot Alzheimer", "View Report", "Healthy Brain Tips"]

if "page" not in st.session_state:
    st.session_state["page"] = "login"

if not st.session_state.get("authenticated", False):
    login_manager = LoginManager()

    if st.session_state.page == "login":
        login_manager.show_login()
    elif st.session_state.page == "signup":
        login_manager.show_signup()

else:
    col1, col2, col3 = st.sidebar.columns([1, 2, 1])
    logo = Image.open("Image/logo1.png")
    col2.image(logo, width=100)

    st.sidebar.markdown(
        "<h1 style='text-align: center; font-size: 22px;'>Quantification Alzheimer Disease Progression</h1>",
        unsafe_allow_html=True
    )

    selected_page = st.sidebar.radio("Go to", page_options, 
                                     index=page_options.index(st.session_state["page"]) 
                                     if st.session_state["page"] in page_options else 0)

    if selected_page != st.session_state["page"]:
        st.session_state["page"] = selected_page
        st.rerun()

    page = st.session_state["page"]

    if page == "Dashboard":
        show_home()

    elif page == "MRI Scan":
        if not st.session_state.get("patient_form_submitted", False):
            add_local_background("Image/12.jpg") 
            show_patient_form()
        else:
            show_MRI()

    elif page == "Healthy Brain Tips":
        show_Tips()

    elif page == "Hippocampus size":
        if not st.session_state.get("patient_form_submitted", False):
            add_local_background("Image/12.jpg") 
            show_patient_form()
        else:
            show_Size()

    elif page == "Chatbot Alzheimer":
        show_Chatbot()

    elif page == "Symptom Checker":
        alzheimer_symptoms()

    elif page == "View Report":
        show_view_report_page()

    if st.sidebar.button("Logout"):
        st.session_state["authenticated"] = False
        st.session_state["page"] = "login"
        st.rerun()