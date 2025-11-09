import streamlit as st
import base64

def add_bg_from_local(image_file):
    with open(image_file, "rb") as img_file:
        encoded_img = base64.b64encode(img_file.read()).decode()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{encoded_img}");
            background-size: cover;
            background-attachment: fixed;
            background-repeat: no-repeat;
            background-position: center;
        }}
        .glass-box {{
            background: rgba(255, 255, 255, 1);
            border-radius: 16px;
            padding: 0px 0px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
            border: 8px solid #000;
            max-width: 900px;
            margin: 3rem auto;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

def show_Tips():
    add_bg_from_local("Image/12.jpg")
    st.markdown("<div class='glass-box'><h1 style='text-align: center;'>🧠 Healthy Brain Tips</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>Follow these proven lifestyle tips to keep your brain healthy and reduce the risk of Alzheimer’s disease</h3>", unsafe_allow_html=True)

    tips = [
        ("Healthy Diet", "Image/healthy_diet.jpeg", 
        """The Mediterranean diet is one of the best diets for brain health.

🟢 Eat more vegetables, fruits, fish, olive oil, and nuts.  
🟢 Avoid processed foods, excessive sugar, and saturated fats.  
🟢 These healthy foods help reduce inflammation and support brain function.
"""),

        ("Exercise", "Image/exercise.jpeg", 
        """Regular physical activity improves memory and cognitive health.

🟢 Try brisk walking, yoga, cycling, or swimming.  
🟢 At least 30 minutes of light to moderate exercise daily is recommended.  
🟢 It boosts blood flow and keeps the brain active.
"""),

        ("Mental Activity", "Image/mental_activity.jpeg", 
        """Keeping your mind busy helps slow down cognitive decline.

🟢 Solve puzzles, read books, learn a new language or play chess.  
🟢 Learn new skills to challenge your brain.  
🟢 Mental stimulation builds new brain connections.
"""),

        ("Social Interaction", "Image/social.jpeg", 
        """Staying socially active reduces loneliness and depression.

🟢 Spend time with family and friends.  
🟢 Join social clubs or participate in group activities.  
🟢 Social bonds help reduce stress and keep the brain healthy.
"""),

        ("Sleep", "Image/sleep.jpeg", 
        """Proper sleep is essential for brain repair and memory.

🟢 Aim for 7 to 8 hours of quality sleep every night.  
🟢 Good sleep removes harmful toxins from the brain.  
🟢 Sleep disorders can increase the risk of Alzheimer’s.
"""),

        ("Stress Control", "Image/stress.jpeg", 
        """Chronic stress harms brain cells and affects memory.

🟢 Try meditation, deep breathing, and relaxing hobbies like gardening.  
🟢 Practice mindfulness to stay calm and focused.  
🟢 Lowering stress supports overall brain health.
"""),

        ("Avoid Smoking & Alcohol", "Image/no_smoking.jpeg", 
        """Smoking and excessive alcohol damage brain cells.

🟢 Smoking reduces oxygen supply to the brain.  
🟢 Alcohol affects memory and increases Alzheimer risk.  
🟢 Avoiding these habits protects your brain.
"""),

        ("Regular Medical Checkups", "Image/medical.jpeg", 
        """Health conditions like diabetes or high blood pressure affect the brain.

🟢 Keep blood sugar, blood pressure, and cholesterol under control.  
🟢 Visit your doctor regularly for memory checkups if needed.  
🟢 Early detection can help prevent serious issues.
""")
    ]

    for title, img, desc in tips:
        col1, col2 = st.columns([1, 1])
        with col1:
            st.subheader(f"🔹 {title}")
            st.write(desc)
        with col2:
            st.image(img, use_container_width=True)
        st.markdown("---")

    st.markdown('</div>', unsafe_allow_html=True)