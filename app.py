import streamlit as st
import requests
from datetime import datetime
import joblib

# Load your model
model = joblib.load(r'C:\Users\nehas\OneDrive\Desktop\Projects\LOS-project\model.joblib')


# Group 1: Health-related features
health_features = [
    "blood", "circulatory", "congenital", "digestive", "endocrine", "genitourinary", 
    "infectious", "injury", "mental", "misc", "muscular", "neoplasms", "nervous", 
    "prenatal", "respiratory", "skin"
]


# Group 3: Age
age_features = ["age_days"]

# Group 4: Admission Type, Marital Status, Gender
admission_type_options = [
    "AMBULATORY OBSERVATION", "DIRECT EMER.", "DIRECT OBSERVATION", 
    "EU observation", "Elective", "Emergency", "Observation admit", 
    "Surgical same day admission", "Urgent"
]

marital_status_options = [
    "DIVORCED", "MARRIED", "SEPARATED", "SINGLE", 
    "UNKNOWN (DEFAULT)", "WIDOWED"
]

gender_options = {"Male": 0, "Female": 1}

# Custom CSS for styling
st.markdown(
    """
    <style>
    .reportview-container {
        background-color: #b0e0e6;
    }
    .sidebar .sidebar-content {
        background-color: #b0e0e6;
    }
    .stButton>button {
        background-color: #007bb5;
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("Hospital Length of Stay Prediction")

# Heading for medical events
st.header("Medical Event")

# Create checkboxes for health-related features
health_values = {feature: st.checkbox(f"{feature}", value=False) for feature in health_features}

# Input for Age
age_years = age_years = st.text_input("Age", value="0")
age_years = int(age_years)
age_days = age_years * 365

# Dropdowns for Admission Type, Marital Status, and Gender
selected_admission_type = st.selectbox(
    "Select Admission Type",
    admission_type_options
)
selected_marital_status = st.selectbox(
    "Select Marital Status",
    marital_status_options
)
selected_gender_text = st.selectbox(
    "Select Gender",
    list(gender_options.keys())
)
selected_gender = gender_options[selected_gender_text]

# Submit buttons
submit_predict = st.button("Predict")
submit_explain = st.button("Explain")

# Handling the predict button click
if submit_predict:
    # Convert checkbox values to binary (0 or 1)
    health_values_binary = [int(health_values[feature]) for feature in health_features]
    
    data = {
        "instances": [
            health_values_binary + [age_days, 
                                    selected_admission_type, selected_marital_status, selected_gender]
        ]
    }
    response = requests.post(model, json=data)
    st.write("Prediction Result:")
    st.json(response.json())

# # Handling the explain button click
# if submit_explain:
#     # Convert checkbox values to binary (0 or 1)
#     health_values_binary = [int(health_values[feature]) for feature in health_features]
    
#     data = {
#         "instances": [
#             health_values_binary + [admit_year, dob_year, age_days, 
#                                     selected_admission_type, selected_marital_status, selected_gender]
#         ]
#     }
#     response = requests.post(EXPLAIN_URL, json=data)
#     st.write("Explanation Result:")
#     st.json(response.json())
