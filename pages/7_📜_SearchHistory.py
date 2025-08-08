import streamlit as st
import pandas as pd
from datetime import datetime
import os
import logging
#import helper_functions as query

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize or load history from file
if 'query_history' not in st.session_state:
    try:
        st.session_state.query_history = pd.read_csv('logs/query_history.csv', 
                                                   parse_dates=['timestamp'])
    except:
        st.session_state.query_history = pd.DataFrame(columns=[
            'timestamp', 'query', 'response', 'rating', 'response_time'
        ])

def delete_query(timestamp, user_email):
    """Delete query from history"""
    try:
        # Ensure timestamp is in datetime format
        if not isinstance(timestamp, pd.Timestamp):
            timestamp = pd.to_datetime(timestamp)
            
        # Create mask to KEEP all records EXCEPT the matching timestamp AND email
        mask = ~((st.session_state.query_history['timestamp'] == timestamp) & 
                (st.session_state.query_history['user_email'] == user_email))
        
        st.session_state.query_history = st.session_state.query_history[mask]
        st.session_state.query_history.to_csv('query_history.csv', index=False)
        st.toast("Query deleted successfully")
        return True
    except Exception as e:
        logger.error(f"Error deleting query: {str(e)}")
        st.error(f"Error deleting query: {str(e)}")
        return False

def display_results():
    """Display query history"""
    st.set_page_config(page_title="Search History | Jeron.AI", layout="centered")
    st.title("📋 Your Query History")
    st.session_state.query_history = pd.read_csv('logs/query_history.csv')
    # Filter queries for current user
    # user_queries = st.session_state.query_history[
    #     st.session_state.query_history['user_email'] == st.user.email
    # ].copy()
    # logger.info(f"Displaying {len(user_queries)} queries for user {st.user.email}")
    
    if 'query_history' not in st.session_state:
        st.warning("No search history available")
        return
    
    # Get current user email from either Google auth or session state
    user_email = None
    if hasattr(st, 'user') and st.user.is_logged_in:
        user_email = st.user.email
    elif 'user' in st.session_state:
        user_email = st.session_state.user.get('email')
    
    if not user_email:
        st.warning("Please login to view your search history")
        return
    
    # Filter history for current user
    user_queries = st.session_state.query_history[
        st.session_state.query_history['user_email'] == user_email
    ]
    
    if user_queries.empty:
        st.info("You haven't made any searches yet")
        return
    
    if not user_queries.empty:
        # Ensure proper datetime format
        user_queries.loc[:, 'timestamp'] = pd.to_datetime(user_queries['timestamp'])
        
        for _, row in user_queries.sort_values('timestamp', ascending=False).iterrows():
            # Safely format the timestamp
            try:
                time_str = row['timestamp'].strftime('%m/%d %H:%M')
            except:
                time_str = "Unknown time"
                
            with st.expander(f"🗓️ {time_str}: {str(row['query'])[:50]}..."):
                #st.caption(f"⏱️ {row['response_time']}s")
                st.markdown(f"**Query:** {row['query']}")
                #st.markdown("---")
                st.markdown(f"**Ans:**")
                st.markdown(f"{str(row['response'])}")
                
                # Delete button (only shows for user's own queries)
                if st.button("Delete", key=f"del_{row['timestamp']}"):
                    if delete_query(row['timestamp'], st.user.email):
                        st.rerun()
    else:
        st.info("No queries yet")

if __name__ == "__main__":
    display_results()
