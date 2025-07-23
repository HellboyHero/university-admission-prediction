import streamlit as st
import pandas as pd
from model import predict_admission
from utils import preprocess_input

st.set_page_config(page_title="University Admission Predictor", page_icon="🎓")

def main():
    st.title("🎓 University Admission Prediction")
    st.write("Enter your details to predict admission chances")

    # Input form
    with st.form("prediction_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            gre_score = st.number_input("GRE Score", min_value=260, max_value=340, value=300)
            toefl_score = st.number_input("TOEFL Score", min_value=0, max_value=120, value=100)
            university_rating = st.slider("University Rating", 1, 5, 3)
            
        with col2:
            sop = st.slider("SOP Rating", 1.0, 5.0, 3.0, 0.5)
            lor = st.slider("LOR Rating", 1.0, 5.0, 3.0, 0.5)
            cgpa = st.number_input("CGPA", min_value=0.0, max_value=10.0, value=8.0)
            research = st.selectbox("Research Experience", ["Yes", "No"])

        submitted = st.form_submit_button("Predict Chances")

    if submitted:
        # Prepare input data
        input_data = {
            'GRE Score': gre_score,
            'TOEFL Score': toefl_score,
            'University Rating': university_rating,
            'SOP': sop,
            'LOR': lor,
            'CGPA': cgpa,
            'Research': 1 if research == "Yes" else 0
        }
        
        # Preprocess input
        processed_input = preprocess_input(input_data)
        
        # Get prediction
        prediction = predict_admission(processed_input)
        
        # Display results
        st.subheader("Prediction Results")
        probability = prediction * 100
        
        # Create a progress bar for visualization
        st.progress(probability / 100)
        
        # Display the probability with appropriate color coding
        if probability >= 70:
            st.success(f"Admission Probability: {probability:.2f}%")
        elif probability >= 50:
            st.warning(f"Admission Probability: {probability:.2f}%")
        else:
            st.error(f"Admission Probability: {probability:.2f}%")
            
        # Additional insights
        st.subheader("Analysis")
        insights = []
        
        if gre_score < 300:
            insights.append("Consider retaking GRE to improve your score")
        if toefl_score < 100:
            insights.append("A higher TOEFL score could improve your chances")
        if cgpa < 8.0:
            insights.append("Strong academic performance (CGPA) is important for admissions")
        if research == "No":
            insights.append("Research experience could strengthen your application")
            
        if insights:
            for insight in insights:
                st.info(insight)
        else:
            st.success("Your profile looks strong! Make sure to prepare a compelling application.")

if __name__ == "__main__":
    main()
