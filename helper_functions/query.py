import os
import streamlit as st
import logging
import pandas as pd
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Add this to save periodically
# def save_history():
#     st.session_state.query_history.to_csv('logs/query_history.csv', index=False)

# Call save_history() after modifications

def save_query_to_csv(query_data: dict):
    """Save a single query entry to CSV file"""
    try:
        # Convert to DataFrame
        df = pd.DataFrame([query_data])
        
        # Write to CSV (append mode if file exists)
        df.to_csv('logs/query_history.csv', 
                 mode='a', 
                 header=not os.path.exists('logs/query_history.csv'), 
                 index=False)
        logger.info("Query saved to CSV")
    except Exception as e:
        logger.error(f"Error saving query to CSV: {str(e)}")
        st.error("Failed to save query history")

# Modify your log_query function to use this:
def log_query(query: str, response: str, response_time: float):
    """Log query and response to history and CSV"""
    if st.user.is_logged_in:
        new_entry = {
            'timestamp': datetime.now(),
            'user_email': st.user.email,
            'query': query,
            'response': response[:5000] + '...' if len(response) > 5000 else response,
            'response_time': response_time
        }
    else:
        new_entry = {
            'timestamp': datetime.now(),
            'user_email': st.session_state.user['email'],
            'query': query,
            'response': response[:5000] + '...' if len(response) > 5000 else response,
            'response_time': response_time
        }
    
    # Add to session state
    st.session_state.query_history = pd.concat([
        st.session_state.query_history,
        pd.DataFrame([new_entry])
    ], ignore_index=True)
    
    # Save to CSV
    save_query_to_csv(new_entry)

# def delete_query(timestamp):
#     """Delete query from history"""
#     try:
#         # Convert to datetime if it's a string
#         if isinstance(timestamp, str):
#             timestamp = pd.to_datetime(timestamp)
            
#         # Filter out the matching timestamp
#         mask = st.session_state.query_history['timestamp'] != timestamp
#         st.session_state.query_history = st.session_state.query_history[mask]
        
#         # Save to CSV
#         st.session_state.query_history.to_csv('logs/query_history.csv', index=False)
#         st.toast("Query deleted successfully")
#         return True
#     except Exception as e:
#         st.error(f"Error deleting query: {str(e)}")
#         return False
