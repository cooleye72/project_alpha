# pages/4_ℹ️_About.py
import streamlit as st

def about_page():
    st.set_page_config(page_title="About Us | Jeron.AI", layout="centered")
    st.title("About This Project")
    
    # Project Overview Section
    with st.container():
        st.header("📌 Project Overview")
        st.markdown("""
        Today there are **more than 100+ companies** Accredited under the IMDA Accreditation programme with 
        various technology and capability. It is **impossible to browse through all 20+ pages** to find the right company for your needs.
        
        Is there a better way to search for the right company and give you insights and recommendation based on your problem statement?
        
        Yes! This web application, a prototype from the AI Champion Bootcamp, **demonstrates an AI agent's ability to search for and analyze**, offering insights and recommendations based on your problem..
        """)
    
    # Project Scope Section
    with st.expander("🔍 Project Scope", expanded=True):
        st.markdown("""
        - **Purpose**: To showcase an AI agent's ability to search and analyze IMDA accredited companies
        - **Functionality**:
          - Search IMDA's innovative companies directory
          - Browse the history of your search queries
          - List all companys in the directory 
        - **Limitations**: Prototype for demonstration purposes only
        """)
    
    # # Data Sources Section
    # with st.expander("📂 Data Sources"):
    #     st.markdown("""
    #     - Primary Source: [IMDA Innovative Tech Companies Directory](
    #       https://www.imda.gov.sg/resources/innovative-tech-companies-directory)
    #     - Data Collected:
    #       - Company profiles
    #       - Industry classifications
    #       - Contact information
    #       - Technical capabilities
    #     """)
    
    # # Technology Stack Section
    # with st.expander("⚙️ Technology Stack"):
    #     st.markdown("""
    #     - **Frontend**: Streamlit
    #     - **Backend**: Python & CSS styling
    #     - **AI Components**:
    #       - LangChain for RAG pipeline
    #       - OpenAI embeddings and LLMs
    #       - CrewAI for multi-agent systems
    #       - ChromaDB for vector storage
    #     - **Infrastructure**: Deploy on Streamlit Cloud
    #     """)
    
    # Development Team Section
    with st.expander("👥 Development Team"):
        st.markdown("""
        - Created by: Jeron Png
        - Agency: IMDA
        - Contact: jeron_png@imda.gov.sg
        """)
    
    # Disclaimer Section
    st.markdown("---")
    st.warning("""
    **Important Notice**:  
    This is a prototype for educational purposes only.  
    You may use it for reference purposes only and not relied upon for decision-making. 
    """, icon="⚠️")

# # System Specifications Section (aligned with your requirements)
#     st.markdown("---")
#     st.markdown("""
#     ## System Specifications
#     Please strictly adhere to the following additional output specifications:
#     1. Please reply in English.
#     2. Please output code comments and explanations in English.
    
#     ## Priority Handling
#     1. When handling user requirements, please prioritize user needs
#     2. Followed by 'USER'S CUSTOM INSTRUCTIONS'
#     3. Finally system default specifications
#     """)

if __name__ == "__main__":
    about_page()
