import streamlit as st
from PIL import Image
import base64
import os
import time
import logging
from streamlit.components.v1 import html

# --- Configure logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Custom Layout Configuration ---
def set_login_layout():
    """Set wide layout only for login page"""
    st.set_page_config(page_title="Login | Jeron.AI", layout="wide")

def set_standard_layout():
    """Set standard layout for all other pages"""
    st.set_page_config(page_title="Jeron.AI", layout="centered")

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
        'timestamp': datetime.now(),
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

# --- Show Google user profile picture ---
def show_user_profile():
    # Custom CSS for the profile dropdown
    st.markdown("""
    <style>
        .profile-container {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 20px;
        }
        .profile-pic {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            object-fit: cover;
            cursor: pointer;
            transition: transform 0.3s;
        }
        .show {display: block;}
    </style>
    """, unsafe_allow_html=True)
        # JavaScript for dropdown toggle
        
    # Sidebar profile section
    with st.sidebar:
        # Handle Google profile
        if hasattr(st, 'user') and st.user.is_logged_in:
            st.markdown(f"""
            <div class="profile-container">
                <img src="{st.user.get('picture', '')}" 
                    class="profile-pic" 
                    alt="Profile">
                <div>{st.user.get('name', 'User')}</div>
            </div>
            """, unsafe_allow_html=True)
        # Handle email/password profile
        if 'user' in st.session_state:
            st.markdown(f"""
            <div class="profile-container">
                <div>{st.session_state.user.get('name', 'User')}</div>
            </div>
            """, unsafe_allow_html=True)

# --- Show Logout button in the sidebar after login ---        
def show_logout_button():
    # Sidebar logout section
    with st.sidebar:
        
        if st.button("Logout", help="Click to logout", type="primary", use_container_width=True):
            # Handle Google logout
            if hasattr(st, 'user') and st.user.is_logged_in:
                log_auth_action(st.user.email, 'logout')  # Log the logout
                st.logout()  # Streamlit's native logout
            
            # Handle email/password logout
            if 'user' in st.session_state:
                log_auth_action(st.session_state.user['email'], 'logout')  # Log the logout
                st.session_state.pop('user')  # Clear session
            
            # Force full page reload to reset state completely
            st.rerun()  # Or st.switch_page("app.py") in newer versions

# --- Authentication Functions ---
def handle_google_login():
    if not st.user.is_logged_in:
        st.markdown("""
        <style>
            .google-login-btn {
                background-color: #4285F4 !important;
                color: white !important;
                border: none !important;
            }
            .google-login-btn:hover {
                background-color: #3367D6 !important;
            }
        </style>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([3, 2, 2.5])  # Middle column is wider
        with col2:
            if st.button("Sign in Google", type="secondary", key="google_login"):
                st.login("google")
                st.rerun()  # Refresh to check auth status
    #else:
    #    main_app_page()  # User is logged in, show main app

def handle_email_login():
    """Email/password login form"""
    with st.form("email_login"):
        email = st.text_input("Email Address")
        password = st.text_input("Password", type="password")
        
        if st.form_submit_button("Sign In"):
            try:
                for user in st.secrets["users"]:
                    creds = st.secrets["users"][user]
                    if email == creds["email"] and password == creds["password"]:
                        st.session_state.user = {
                            "email": email,
                            "name": creds.get("name", "User"),
                            "is_logged_in": True,
                            "role": user
                        }
                        log_auth_action(email, 'login')
                        st.success(f"Welcome {creds.get('name', 'User')}!")
                        st.rerun()
                
                st.error("Invalid credentials")
            except Exception as e:
                st.error("Login service unavailable")
                logger.error(f"Login error: {str(e)}")
                         
# --- Navigation Pages after Login---
def main_app_page():
    set_standard_layout()
    
    # Define your navigation pages
    search = st.Page("pages/1_🔍_Search.py", title="Search")
    searchhistory = st.Page("pages/7_📜_SearchHistory.py", title="Search History")
    setup = st.Page("pages/2_⚙️_Configuration.py", title="Setup")
    about = st.Page("pages/4_ℹ️_About.py", title="About")
    methodology = st.Page("pages/5_🔬_Methodology.py", title="Methodology")
    troubleshooting = st.Page("pages/6_🛠️_Troubleshooting.py", title="Troubleshooting")
    
    # Show navigation only when logged in
    #if st.user.is_logged_in or 'user' in st.session_state:
    if st.user.is_logged_in:
        pg = st.navigation(
            {
                #"Account": [logout_page],
                # "Reports": [dashboard, bugs, alerts],
                "Tools": [search, searchhistory],
                "Info": [about, methodology],
                "Troubleshoot": [troubleshooting]
                
            }
        )
       
        # st.navigation([
        #     ("Tools", [search, history]),
        #     ("Settings", [settings])
        # ]).run()
    elif 'user' in st.session_state:
        pg = st.navigation(
            {
                #"Account": [logout_page],
                # "Reports": [dashboard, bugs, alerts],
                "Tools": [search, searchhistory],
                "Info": [about, methodology],
                "Admin": [setup, troubleshooting]
            }
        )
    pg.run()
    
    show_user_profile()
    show_logout_button()


# --- Main Login Page ---
def login_page():
    #logging.info("At login_page()")
    set_login_layout()
    
    with st.container():
        col1, col2 = st.columns([2, 3])
        
        with col1:
            st.markdown("""
            <div style="max-width: 400px; margin: 0 auto; text-align: center;">
                <h1 style="font-size: 2rem;">Welcome to Jeron.AI</h1>
                <p style="color: #666; margin-bottom: 2rem;">Sign in to access your account</p>
            """, unsafe_allow_html=True)
            
            handle_google_login()
            
            st.markdown("""
            <div style="display:flex; align-items:center; margin:20px 0;">
                <div style="flex:1; border-top:1px solid #ddd;"></div>
                <span style="padding:0 10px; color:#777;">OR</span>
                <div style="flex:1; border-top:1px solid #ddd;"></div>
            </div>
            """, unsafe_allow_html=True)
            
            handle_email_login()
            
            st.markdown("""
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            # Your banner image section - using use_container_width instead
            st.image("img/banner.jpg", width=550)
        
        with st.sidebar:
            st.markdown("""
            <div style="text-align: center; padding: 20px;">
                <h2>About Jeron.AI</h2>
                <p>Jeron.AI is your AI-powered assistant for all things related to IMDA accredited companies.</p>
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    if not (st.user.is_logged_in or st.session_state.get("user", {}).get("is_logged_in")):
        #logging.info("User is not logged in, showing login app page")
        pg = st.navigation([login_page])
        pg.run()
    else:
        #logging.info("User is logged in, showing main app page")
        main_app_page()