import streamlit as st
import requests
from datetime import datetime
import joblib

# Load your model
model = joblib.load('x.joblib')

# Group 1: Health-related features
health_features = [
    "blood", "circulatory", "congenital", "digestive", "endocrine", "genitourinary", 
    "infectious", "injury", "mental", "misc", "muscular", "neoplasms", "nervous", 
    "prenatal", "respiratory", "skin"
]

# Other categorical options
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

insurance_options = ["Medicaid", "Medicare", "Other", "Private"]
religion_options = ["NOT SPECIFIED", "RELIGIOUS", "UNOBTAINABLE"]
ethnicity_options = ["BLACK/AFRICAN AMERICAN", "HISPANIC/LATINO", "OTHER/UNKNOWN", "UNKNOWN", "WHITE"]

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
age_years = st.text_input("Age", value="0")
age_years = int(age_years)
age_days = age_years * 365

# Dropdowns for Admission Type, Marital Status, Gender, Insurance, Religion, Ethnicity
selected_admission_type = st.selectbox("Select Admission Type", admission_type_options)
selected_marital_status = st.selectbox("Select Marital Status", marital_status_options)
selected_gender_text = st.selectbox("Select Gender", list(gender_options.keys()))
selected_gender = gender_options[selected_gender_text]

selected_insurance = st.selectbox("Select Insurance Type", insurance_options)
selected_religion = st.selectbox("Select Religion", religion_options)
selected_ethnicity = st.selectbox("Select Ethnicity", ethnicity_options)

# Submit buttons
submit_predict = st.button("Predict")

# Handling the predict button click
if submit_predict:
    # Convert checkbox values to binary (0 or 1)
    health_values_binary = [int(health_values[feature]) for feature in health_features]
    
    # Map categorical inputs to numerical values
    admission_type_mapping = {option: index for index, option in enumerate(admission_type_options)}
    marital_status_mapping = {option: index for index, option in enumerate(marital_status_options)}
    insurance_mapping = {option: index for index, option in enumerate(insurance_options)}
    religion_mapping = {option: index for index, option in enumerate(religion_options)}
    ethnicity_mapping = {option: index for index, option in enumerate(ethnicity_options)}

    # Encode the categorical values
    admission_type_encoded = admission_type_mapping.get(selected_admission_type, 0)  # Default to 0 if not selected
    marital_status_encoded = marital_status_mapping.get(selected_marital_status, 0)  # Default to 0 if not selected
    insurance_encoded = insurance_mapping.get(selected_insurance, 0)  # Default to 0 if not selected
    religion_encoded = religion_mapping.get(selected_religion, 0)  # Default to 0 if not selected
    ethnicity_encoded = ethnicity_mapping.get(selected_ethnicity, 0)  # Default to 0 if not selected

    # Combine all input features
    input_features = health_values_binary + [age_days, ethnicity_encoded, religion_encoded, 
                                             insurance_encoded, admission_type_encoded, 
                                             marital_status_encoded, selected_gender]

    # Pad the input features list with zeros if fewer than 48 features are provided
    input_features += [0] * (48 - len(input_features))

    # Prepare data for API request
    data = {
        "instances": [
            input_features  # All features combined
        ]
    }

    # Model Prediction
    prediction = model.predict([input_features])[0]
    prediction = round(prediction)
    st.write(f"Your estimated stay in the hospital is: {prediction}")

    # # External API Prediction
    # api_endpoint = model # Replace with your actual API endpoint
    # try:
    #     response = requests.post(api_endpoint, json=data)
    #     response.raise_for_status()  # Raise an error for bad responses
    #     api_prediction = response.json()
    #     st.write("API Prediction Result:")
    #     st.json(api_prediction)
    # except requests.exceptions.RequestException as e:
    #     st.error(f"API request failed: {e}")

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
