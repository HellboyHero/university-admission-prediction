import pandas as pd
import numpy as np
from typing import Dict, Any

def preprocess_input(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Preprocess the input data before making predictions.
    
    Args:
        input_data: Dictionary containing raw input features
    Returns:
        Dictionary containing preprocessed features
    """
    # Create a copy of the input data
    processed_data = input_data.copy()
    
    # Normalize GRE Score (260-340 range)
    processed_data['GRE Score'] = (input_data['GRE Score'] - 260) / (340 - 260)
    
    # Normalize TOEFL Score (0-120 range)
    processed_data['TOEFL Score'] = input_data['TOEFL Score'] / 120
    
    # University Rating is already in the correct range (1-5)
    
    # SOP and LOR are already in the correct range (1-5)
    
    # Normalize CGPA (0-10 range)
    processed_data['CGPA'] = input_data['CGPA'] / 10
    
    # Research is already binary (0 or 1)
    
    return processed_data

def load_and_preprocess_data(file_path: str) -> pd.DataFrame:
    """
    Load and preprocess the training data.
    
    Args:
        file_path: Path to the CSV file containing the dataset
    Returns:
        Preprocessed DataFrame
    """
    # Load the data
    df = pd.read_csv(file_path)
    
    # Apply the same preprocessing as for single inputs
    df['GRE Score'] = (df['GRE Score'] - 260) / (340 - 260)
    df['TOEFL Score'] = df['TOEFL Score'] / 120
    df['CGPA'] = df['CGPA'] / 10
    
    return df

def validate_input(input_data: Dict[str, Any]) -> bool:
    """
    Validate the input data to ensure all required fields are present and within expected ranges.
    
    Args:
        input_data: Dictionary containing input features
    Returns:
        bool: True if input is valid, False otherwise
    """
    try:
        # Check if all required fields are present
        required_fields = ['GRE Score', 'TOEFL Score', 'University Rating', 
                         'SOP', 'LOR', 'CGPA', 'Research']
        for field in required_fields:
            if field not in input_data:
                return False
        
        # Validate ranges
        if not (260 <= input_data['GRE Score'] <= 340):
            return False
        if not (0 <= input_data['TOEFL Score'] <= 120):
            return False
        if not (1 <= input_data['University Rating'] <= 5):
            return False
        if not (1 <= input_data['SOP'] <= 5):
            return False
        if not (1 <= input_data['LOR'] <= 5):
            return False
        if not (0 <= input_data['CGPA'] <= 10):
            return False
        if input_data['Research'] not in [0, 1]:
            return False
        
        return True
    except:
        return False

def format_prediction_results(prediction: float, input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format the prediction results with additional insights.
    
    Args:
        prediction: The model's prediction (probability of admission)
        input_data: Original input data
    Returns:
        Dictionary containing formatted results and insights
    """
    results = {
        'prediction': prediction,
        'probability_percentage': prediction * 100,
        'insights': []
    }
    
    # Add insights based on the input values
    if input_data['GRE Score'] < 300:
        results['insights'].append({
            'factor': 'GRE Score',
            'message': 'Consider improving your GRE score to increase admission chances'
        })
    
    if input_data['TOEFL Score'] < 100:
        results['insights'].append({
            'factor': 'TOEFL Score',
            'message': 'A higher TOEFL score could strengthen your application'
        })
    
    if input_data['CGPA'] < 8.0:
        results['insights'].append({
            'factor': 'CGPA',
            'message': 'Focus on maintaining a higher CGPA'
        })
    
    if input_data['Research'] == 0:
        results['insights'].append({
            'factor': 'Research',
            'message': 'Getting research experience could significantly improve your chances'
        })
    
    return results
