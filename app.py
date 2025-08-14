import streamlit as st
from PIL import Image
import base64
import os
import time
import logging
from streamlit.components.v1 import html
from helper_functions.logauth import log_auth_action


# for streamlit cloud compatibility
# __import__('pysqlite3')
# import sys
# sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

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
                # logger.info("user clicked Google login")

                # st.rerun()  # Refresh to check auth status
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
    webscraping = st.Page("pages/2_⚙️_WebScraping.py", title="Web Scraping (Admin Only)")
    about = st.Page("pages/4_ℹ️_About.py", title="About")
    methodology = st.Page("pages/5_🔬_Methodology.py", title="Methodology (Admin Only)")
    troubleshooting = st.Page("pages/6_🛠️_Troubleshooting.py", title="Troubleshooting")
    companydirectory = st.Page("pages/8_📂_CompanyDirectory.py", title="Company Directory")
    
    # Show navigation only when logged in
    #if st.user.is_logged_in or 'user' in st.session_state:
    if st.user.is_logged_in:
        if "login_logged" not in st.session_state:
            log_auth_action(st.user.email, 'login')
            logger.info(f"User {st.user.email} logged in successfully")
            st.session_state.login_logged = True  # Prevent duplicate logging
        
        pg = st.navigation(
            {
                #"Account": [logout_page],
                # "Reports": [dashboard, bugs, alerts],
                "Tools": [search, searchhistory, companydirectory],
                "Info": [about],
                "Troubleshoot": [troubleshooting]
                
            }
        )
       
    elif 'user' in st.session_state:
        pg = st.navigation(
            {
                #"Account": [logout_page],
                # "Reports": [dashboard, bugs, alerts],
                "Tools": [search, searchhistory, companydirectory],
                "Info": [about, methodology],
                "Admin": [webscraping, troubleshooting]
            }
        )
    pg.run()
    
    # st.markdown("""
    # ![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=cooleye72_project_alpha&metric=alert_status)
    # """, unsafe_allow_html=True)
    # st.markdown("""
    # ![SonarQube Cloud](https://sonarcloud.io/images/project_badges/sonarcloud-highlight.svg)
    # """, unsafe_allow_html=True)
    # st.divider()
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
                <p>Jeron.AI is your AI-powered assistant that helps you find and connect with technology solutions provided by IMDA accredited companies.</p>
                <p>This platform has no affiliation with IMDA and is built for educational purposes.</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            ![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=cooleye72_project_alpha&metric=alert_status)
            """, unsafe_allow_html=True)
            
            st.markdown("""
            ![SonarQube Cloud](https://sonarcloud.io/images/project_badges/sonarcloud-highlight.svg)
            """, unsafe_allow_html=True)
            

if __name__ == "__main__":
    if not (st.user.is_logged_in or st.session_state.get("user", {}).get("is_logged_in")):
        #logging.info("User is not logged in, showing login app page")
        pg = st.navigation([login_page])
        pg.run()
    else:
        #logging.info("User is logged in, showing main app page")
        main_app_page()
