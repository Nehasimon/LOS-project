import streamlit as st
import boto3
import joblib 
import os 

# AWS S3 client setup
s3 = boto3.client(
    's3',
    aws_access_key_id= "AKIAX2NXUVDJM3YW6FGM",
    aws_secret_access_key= "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",
    region_name='us-east-1'
)

 # Function to load the model from S3
def load_model_from_s3(bucket_name, model_key):
     local_model_path = '/tmp/model.joblib'
     os.makedirs(os.path.dirname(local_model_path), exist_ok=True)
     s3.download_file(bucket_name, model_key, local_model_path)
     with open(local_model_path, 'rb') as model_file:
         model = joblib.load(model_file)
     return model

# Streamlit app setup
st.set_page_config(page_title="Hospital Length of Stay Prediction", page_icon=":hospital:", layout="wide")

st.markdown(
    """
    <style>
    .reportview-container {
        background-color: #fff; /* Lighter blue background */
    }
    .sidebar .sidebar-content {
        background-color: #e0f7fa;
    }
    .stButton>button {
        background-color: #007bb5;
        color: white;
    }
    .stSelectbox div, .stTextInput div, .stCheckbox div {
        color: #007bb5; /* Set text color to blue */
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.image('https://via.placeholder.com/800x200?text=Hospital+Length+of+Stay+Prediction', use_column_width=True)

st.title("Hospital Length of Stay Prediction")

# S3 bucket and model key
bucket_name = 'med-aifactory'
model_key = 'tabular/model/model.joblib'

# Load the model from S3
model = load_model_from_s3(bucket_name, model_key)

# Define feature lists
health_categories = {
    "Hematological Concerns": ["blood"],
    "Circulatory Concerns": ["circulatory"],
    "Congenital Conditions": ["congenital"],
    "Digestive Concerns": ["digestive"],
    "Endocrine Concerns": ["endocrine"],
    "Genitourinary Concerns": ["genitourinary"],
    "Infectious Diseases": ["infectious"],
    "Injury Concerns": ["injury"],
    "Mental Health": ["mental"],
    "Miscellaneous Conditions": ["misc"],
    "Muscular Concerns": ["muscular"],
    "Neoplasms (Tumors)": ["neoplasms"],
    "Nervous System Concerns": ["nervous"],
    "Prenatal Conditions": ["prenatal"],
    "Respiratory Concerns": ["respiratory"],
    "Skin Conditions": ["skin"]
}

admission_type_options = ["Select",
    "AMBULATORY OBSERVATION", "DIRECT EMER.", "DIRECT OBSERVATION", 
    "EU observation", "Elective", "Emergency", "Observation admit", 
    "Surgical same day admission", "Urgent"
]

marital_status_options = ["Select",
    "DIVORCED", "MARRIED", "SEPARATED", "SINGLE", 
    "UNKNOWN (DEFAULT)", "WIDOWED"
]

gender_options = {"Male": 0, "Female": 1}

insurance_options = ["Select","Medicaid", "Medicare", "Private", "Other"]
religion_options = ["Select", "RELIGIOUS", "UNOBTAINABLE","NOT SPECIFIED"]
ethnicity_options = ["Select","BLACK/AFRICAN AMERICAN", "HISPANIC/LATINO", "ASIAN", "WHITE", "UNKNOWN"]

ethnicity_mapping = {option: index for index, option in enumerate(ethnicity_options)}

# Streamlit UI
with st.container():
    st.header("Patient Information")
    selected_admission_type = st.selectbox("Select Admission Type", admission_type_options, index=0)
    selected_marital_status = st.selectbox("Select Marital Status", marital_status_options, index=0)
    selected_gender_text = st.selectbox("Select Gender", list(gender_options.keys()), index=0)
    selected_gender = gender_options[selected_gender_text]
    selected_insurance = st.selectbox("Select Insurance Type", insurance_options, index=0)
    selected_religion = st.selectbox("Select Religion", religion_options, index=0)

# Process ethnicity selection
selected_ethnicity = st.multiselect("Select Ethnicity", ethnicity_options, default=[])
if "ASIAN" in selected_ethnicity:
    selected_ethnicity = [e for e in selected_ethnicity if e != "ASIAN"]
    selected_ethnicity.append("UNKNOWN")

ethnicity_encoded_values = [ethnicity_mapping.get(e, 4) for e in selected_ethnicity]
ethnicity_encoded_value = ethnicity_encoded_values[0] if ethnicity_encoded_values else 4

# Input for Age
age_years = st.text_input("Age", value="")
try:
    age_years = int(age_years) if age_years else 0
except ValueError:
    st.error("Please enter a valid number for Age.")
    age_years = 0
age_days = age_years * 365


# Initialize health_values dictionary
health_values = {category: False for category in health_categories}

# Checklist for health-related categories in two columns
st.header("Medical Diagnosis")
col1, col2 = st.columns(2)

with col1:
    for category in list(health_categories.keys())[:8]:
        health_values[category] = st.checkbox(category, value=False)

with col2:
    for category in list(health_categories.keys())[8:]:
        health_values[category] = st.checkbox(category, value=False)

# Convert category selections to feature vector
health_values_binary = [int(health_values[category]) for category in health_categories]


# Convert categorical inputs to numerical values
admission_type_encoded = admission_type_options.index(selected_admission_type) if selected_admission_type != "Select" else 0
marital_status_encoded = marital_status_options.index(selected_marital_status) if selected_marital_status != "Select" else 0
insurance_encoded = insurance_options.index(selected_insurance) if selected_insurance != "Select" else 0
religion_encoded = religion_options.index(selected_religion) if selected_religion != "Select" else 0

# Combine features
input_features = health_values_binary + [age_days, ethnicity_encoded_value, religion_encoded, 
                                         insurance_encoded, admission_type_encoded, 
                                         marital_status_encoded, selected_gender]

input_features += [0] * (48 - len(input_features))  # Ensure the feature vector has 48 elements

# Submit button
submit_predict = st.button("Predict")

if submit_predict:
    # Make a prediction using the model
    prediction = model.predict([input_features])[0]
    st.write(f"Your estimated stay in the hospital is: {prediction} Days.")
