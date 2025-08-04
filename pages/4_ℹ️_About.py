# pages/4_ℹ️_About.py
import streamlit as st

def about_page():
    st.title("About This Project")
    
    # Project Overview Section
    with st.container():
        st.header("📌 Project Overview")
        st.markdown("""
        This web application is a prototype developed as part of the AI Champion Bootcamp, 
        designed to demonstrate the capabilities of AI-powered company search and analysis.
        """)
    
    # Project Scope Section
    with st.expander("🔍 Project Scope", expanded=True):
        st.markdown("""
        - **Purpose**: Educational demonstration of RAG (Retrieval-Augmented Generation) systems
        - **Functionality**:
          - Search IMDA's innovative companies directory
          - AI-powered analysis of company profiles
          - Multi-agent processing for complex queries
        - **Limitations**: Prototype for demonstration purposes only
        """)
    
    # Data Sources Section
    with st.expander("📂 Data Sources"):
        st.markdown("""
        - Primary Source: [IMDA Innovative Tech Companies Directory](
          https://www.imda.gov.sg/resources/innovative-tech-companies-directory)
        - Data Collected:
          - Company profiles
          - Industry classifications
          - Contact information
          - Technical capabilities
        """)
    
    # Technology Stack Section
    with st.expander("⚙️ Technology Stack"):
        st.markdown("""
        - **Frontend**: Streamlit
        - **Backend**: Python
        - **AI Components**:
          - LangChain for RAG pipeline
          - OpenAI embeddings and LLMs
          - CrewAI for multi-agent systems
          - ChromaDB for vector storage
        - **Infrastructure**: Deploy on Streamlit Cloud
        """)
    
    # Development Team Section
    with st.expander("👥 Development Team"):
        st.markdown("""
        - Created by: Jeron Png
        - Organization: IMDA AI Champion Bootcamp Participant
        - Contact: [jeron_png@imda.gov.sg]
        - GitHub: [github.com/your-repo]
        """)
    
    # Disclaimer Section
    st.markdown("---")
    st.warning("""
    **Important Notice**:  
    This is a prototype for educational purposes only.  
    Not intended for real-world decision making.  
    LLM outputs may be inaccurate - verify critical information.  
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
