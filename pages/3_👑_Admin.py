# pages/3_👑_Admin.py
import streamlit as st
# from database import UserDB

# db = UserDB()

st.title("Admin Portal")

# tab1, tab2 = st.tabs(["User Management", "System Config"])

# with tab1:
#     users = db.get_all_users()
#     selected = st.selectbox("Select User", users)
#     new_role = st.selectbox("Set Role", ["user", "admin"])
#     if st.button("Update Role"):
#         db.update_role(selected, new_role)

# with tab2:
#     st.file_uploader("Upload Company Data", type=["csv", "json"])
#     st.text_input("Company API Endpoint")