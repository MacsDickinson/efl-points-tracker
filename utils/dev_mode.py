import os
import streamlit as st
from urllib.parse import parse_qs

# Secure dev token - in production this should be set via environment variable
DEV_TOKEN = "f8c7d9e6-3b2a-4e5f-9a1c-8d2e9b3f7c4d"

def is_dev_mode():
    """Check if dev mode is enabled via environment variable and URL parameter"""
    # Check environment variable
    env_dev_mode = os.getenv('FOOTBALL_DASHBOARD_ENV', '').lower() == 'dev'
    if not env_dev_mode:
        return False
    
    # Get URL parameters from Streamlit's query parameters
    query_params = st.experimental_get_query_params()
    dev_token = query_params.get('devtoken', [None])[0]
    
    # Both conditions must be true for dev mode
    return env_dev_mode and dev_token == DEV_TOKEN

def log_error(error_message: str, error: Exception = None):
    """Log error details to console and return user-friendly message"""
    if error:
        print(f"ERROR: {error_message} - Details: {str(error)}")
    else:
        print(f"ERROR: {error_message}")
    
    if is_dev_mode():
        return f"Developer Error: {error_message}\n{str(error) if error else ''}"
    else:
        return "An error occurred while connecting to the database. Please try again later."
