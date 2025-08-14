import streamlit as st
import pandas as pd
import pkg_resources
import subprocess

st.set_page_config(layout="centered", page_title="Troubelshooting | Jeron.AI")

def view_auth_logs():
    """Display authentication logs from CSV file with proper error handling"""
    try:
        # Try to read the log file
        logs_df = pd.read_csv('logs/auth_logs.csv')
        
        # Check if dataframe is empty
        if logs_df.empty:
            st.info("No authentication logs available")
        else:
            st.subheader("Authentication Logs for All Users")
            st.dataframe(
                logs_df.sort_values('timestamp', ascending=False),
                use_container_width=True
            )
            
            # Add download button
            csv = logs_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                "Download Full Logs",
                data=csv,
                file_name='auth_logs_export.csv',
                mime='text/csv'
            )
            
    except FileNotFoundError:
        st.info("No authentication logs available - log file not found")
    except pd.errors.EmptyDataError:
        st.info("No authentication logs available - file is empty")
    except Exception as e:
        st.error(f"Error loading logs: {str(e)}")
      
st.subheader("User login profile") 
st.json(st.user)

st.divider()
view_auth_logs()

st.divider()
# Get pip freeze output
try:
    packages = subprocess.check_output(["pip", "freeze"]).decode("utf-8")
    st.code(packages, language="text")
except Exception as e:
    st.error(f"Error getting packages: {e}")