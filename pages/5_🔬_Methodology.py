import streamlit as st
from PIL import Image

def methodology_page():
    """Showcasing the methodology and system architecture"""
    
    # Page configuration
    st.set_page_config(layout="centered", page_title="Methodology | Jeron.AI")
    st.title("🔬 Methodology")
    st.markdown("""
    <style>
        .methodology-img {
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            margin: 20px 0;
        }
        .section {
            margin-bottom: 30px;
        }
    </style>
    """, unsafe_allow_html=True)

    # Introduction section
    with st.container():
        st.header("Architecture Overview")
        st.markdown("""
        The diagram below illustrates the architecture of the AI agent for IMDA Accred Coys matching and recommendation. 
        It uses two different techniques to provide close matching with explaination.
        
        - The first technique (Basic retriever) quickly return responses based on the use case provided.
        - The second technique (Advanced retriever) uses a more complex multi-agent system to provide details such as Company's Business value proposition, Technical capabilities and recommendation.
        
        Below are the detailed key components and data flows.
        """)
        
        # Display methodology image
        try:
            methodology_img = Image.open("img/aiagent_methodology_light.png")
            st.image(methodology_img, caption="AI Agent Architecture Diagram", 
                    use_container_width=True)
        except FileNotFoundError:
            st.warning("Methodology image not found at specified path")

    # Data Flow Section
    with st.container():
        st.header("📊 Data Flow Process")
        st.markdown("""
        ### 1. Data Ingestion Layer
        - **Sources**: [IMDA Accred Coys datasets](
          https://www.imda.gov.sg/resources/innovative-tech-companies-directory)
        - **Processing**: Manual Web scraping, extract relevant data such as coy name, industry, contact info, URLs, coy description and TAL readiness.
        - **Storage**: Vectorstore in ChromaDB for efficient retrieval
        """)
        
        st.markdown("""
        ### 2. Processing Layer
        - **Model**: GPT-4o model for query interpretation
        - **Vector Search**: ChromaDB for semantic similarity matching
        - **Business Logic**:
            - **Basic Retriever**: Retrieves top 3 relevant companies above 60% match score
            - **Advanced Retriever**: 
                - **Company Search Agent**: Extracts relevant companies based on use case
                - **Web Research Agent**: Retrieves additional information from online sources
                - **Consultant Agent**: Analyzes and summarizes Business value proposition, Technical capabilities and recommendation
                - **Manager Agent**: Presents in an executive summary format
        """)
        
        st.markdown("""
        ### 3. Output Generation
        - **Response**: Structured answer generation based on prompts templates
        - **Formatting**: Markdown templates for consistent presentation
        - **Logging**: Records of queries and responses for auditing and improvement
        """)

    # Implementation Details
    with st.container():
        st.header("⚙️ Technical Implementation")
        cols = st.columns(2)
        
        with cols[0]:
            st.subheader("Core Technologies")
            st.markdown("""
            - **Frontend**: Streamlit
            - **Backend**: Python & CSS styling
            - **AI Components**:
                - LangChain for RAG pipeline
                - CrewAI for multi-agent systems
                - ChromaDB for Vector storage and retrieval
                - OpenAI embeddings and LLMs
            - **Infrastructure**: Deploy on Streamlit Cloud
            """)
            
        with cols[1]:
            st.subheader("Key Features")
            st.markdown("""
            - Intelligent AI Agent Coys matching and recommendation (Not traditional keyword search)
            - Accelerate time to find relevant IMDA accredited companies without browsing through the directory
            - Ask complex queries and get detailed answers anytime anywhere
            - Free to use (Limited period)
            """)


if __name__ == "__main__":
    methodology_page()
