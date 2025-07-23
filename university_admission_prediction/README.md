# University Admission Prediction Using Google Vertex AI

This project uses Google Vertex AI to predict university admission chances based on various student parameters such as GRE Score, TOEFL Score, University Rating, SOP, LOR, CGPA, and Research Experience.

## Project Structure
- `main.py`: Main application file containing the Streamlit web interface
- `model.py`: Contains the model training and prediction code
- `utils.py`: Utility functions for data preprocessing and handling
- `requirements.txt`: Project dependencies
- `data/`: Directory containing the dataset

## Setup Instructions
1. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Set up Google Cloud credentials:
   - Create a Google Cloud project
   - Enable Vertex AI API
   - Create a service account and download the JSON key
   - Set the environment variable GOOGLE_APPLICATION_CREDENTIALS to point to your key file

3. Run the application:
   ```
   streamlit run main.py
   ```

## Features
- Interactive web interface for predictions
- Real-time prediction using Google Vertex AI
- Data visualization of prediction results
- Support for both single predictions and batch processing

## Model Details
The model is trained on historical university admission data and uses the following features:
- GRE Score
- TOEFL Score
- University Rating
- SOP (Statement of Purpose)
- LOR (Letter of Recommendation)
- CGPA
- Research Experience

## Note
Make sure to handle your Google Cloud credentials securely and never commit them to version control.
