import streamlit as st
import os
import logging
from datetime import datetime, timezone
from pytz import timezone as tz

# --- Configure logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# timezone for Singapore
singapore_tz = tz('Asia/Singapore')

# --- Log authentication actions to CSV file ---
def log_auth_action(email: str, action: str):
    """Log authentication actions (login/logout) with timestamp directly to CSV file.
    Creates new file if it doesn't exist, otherwise appends to existing file.
    
    Args:
        email (str): User's email address
        action (str): Either 'login' or 'logout'
    """
    import os
    from datetime import datetime
    import pandas as pd
    
    # Create new log entry
    new_log = {
        'timestamp': datetime.now(singapore_tz),
        'user_email': email,
        'action': action
    }
    
    # Convert to DataFrame
    new_log_df = pd.DataFrame([new_log])
    
    # File path
    log_file = 'logs/auth_logs.csv'
    
    try:
        if os.path.exists(log_file):
            # Append to existing file
            existing_logs = pd.read_csv(log_file)
            updated_logs = pd.concat([existing_logs, new_log_df], ignore_index=True)
            updated_logs.to_csv(log_file, index=False)
        else:
            # Create new file
            new_log_df.to_csv(log_file, index=False)
    except Exception as e:
        print(f"Error writing to log file: {str(e)}")