import logging
import os
import streamlit as st
#from logics.agents import setup_agents
from datetime import datetime
# Create the RAG pipeline
from langchain.chains import RetrievalQA
# from crewai import Agent, Task, Crew
from logics import agents
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
import pandas as pd
# Add this to your existing imports
from langchain_openai import ChatOpenAI
from streamlit import logout
from helper_functions import llm
from helper_functions.query import log_query


# for streamlit cloud compatibility
# __import__('pysqlite3')
# import sys
# sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def initialize_vectordb():
    """Initialize and return the Chroma vector database"""
    try:
        vectordb = Chroma(
            persist_directory="./imda_vectordb",
            collection_name="imda_accred_companies",
            embedding_function=OpenAIEmbeddings()
        )
        logger.info(f"VectorDB loaded with {vectordb._collection.count()} documents")
        return vectordb
    except Exception as e:
        logger.error(f"Error loading VectorDB: {str(e)}")
        st.error("Failed to load company database. Please check the logs.")
        raise


def display_results():
    st.set_page_config(page_title="Companies Recommendation | Jeron.AI", layout="centered")
    st.title("🔍 Companies Recommendation")
 
    # Initialize vector database
    try:
        vectordb = initialize_vectordb()
    except Exception:
        return  # Stop execution if DB fails to load
    
    # Initialize session state
    if 'last_query_time' not in st.session_state:
        st.session_state.last_query_time = None
    if 'deep_search' not in st.session_state:
        st.session_state.deep_search = False
    # st.text(f"Loaded with {vectordb._collection.count()} companies")
    # Search input with validation
    query = st.text_area("Enter your query/use case:", 
                        placeholder="e.g. I want to find a product that specializing in talent recruitment.")
    
    # if not query:
    #     st.warning("Please enter something to search")
    #     return
    
    # Toggle for deep search
    st.session_state.deep_search = st.checkbox("Enable Deep research", 
                                            value=st.session_state.deep_search)
    
    # Search button
    if st.button("Search", type="primary"):
        start_time = datetime.now()
        
        try:
            if st.session_state.deep_search:
                with st.spinner("🧠 Performing deep analysis using multi-agent..."):
                    result = agents.analyze_use_case(query)
                    
                    #result = "none"
            else:
                with st.spinner("🔍 Searching with LangChain..."):
                    # RAG pipeline
                    RECOMMENDATION_PROMPT_TEMPLATE = """You are an expert business matchmaker specializing in connecting users with the most suitable companies from the IMDA directory. Follow these guidelines carefully:
                    <Context>
                    {context}
                    </Context>

                    <User Query>
                    {question}
                    </User Query>

                    <Response Requirements>
                    1. Always begin with "Based on your needs, here are my recommendations:" 
                    2. For each recommended company, provide:
                    - Company Name (bold)
                    - Match Score (0-100% based on relevance)
                    - Key Matching Factors (bullet points)
                    - Specializations/Capabilities
                    - Contact Method (if available)
                    3. Include 3 recommendations maximum, ordered by relevance, minimum 60% match score
                    4. If no companies match well, explain why and suggest alternative approaches
                    4. If no good matches exist, explain why and suggest alternative approaches
                    5. End with: "Would you like me to refine these recommendations or provide more details on any company?"
                    6. Never hallucinate details - if info isn't in the context, say so
                    </Response Requirements>

                    <Output Format>
                    ##### Recommendation Summary
                    [Concise 2-3 sentence overview of why these companies were selected]

                    ##### Top Recommendations
                    1. **Company Name** (Match Score: XX%)
                    - Key Factors: 
                        - Factor 1
                        - Factor 2
                    - Specializes in: [capabilities]
                    - Website: [URL or Website address if available]

                    2. **Company Name** (Match Score: XX%)
                    ...

                    ##### Next Steps
                    [Actionable next steps for the user]
                    </OutputFormat>

                    Helpful Recommendation:"""

                    QA_CHAIN_PROMPT = PromptTemplate.from_template(RECOMMENDATION_PROMPT_TEMPLATE)
                    
                    rag_chain = RetrievalQA.from_chain_type(
                        llm=ChatOpenAI(model='gpt-4o-mini'),
                        retriever=vectordb.as_retriever(k=4),
                        chain_type_kwargs={"prompt": QA_CHAIN_PROMPT}
                    )
                    response = rag_chain.invoke(query)
                    #response = llm.get_completion_by_messages(query)
                    result = response['result']
                    
            # Calculate duration
            duration = datetime.now() - start_time
            st.session_state.last_query_time = f"{duration.total_seconds():.2f} seconds"
            
            # st.session_state.query_history = pd.concat([
            #     st.session_state.query_history,
            #     pd.DataFrame([], columns=['timestamp', 'user_email', 'query', 'response', 'response_time'])
            # ], ignore_index=True)
            # logger.info(f"Deep search result: {result}")
            # logger.info(f"Query: {query}")
            # logger.info(f"Duration: {duration}")
            log_query(query, result, duration)
            
            # Display results
            st.success(f"Query completed in {st.session_state.last_query_time}")
            
            with st.expander("📄 View Results", expanded=True):
                st.markdown("#### <u>Query:</u>", unsafe_allow_html=True)
                st.markdown(query)
                st.markdown("#### <u>Results:</u>", unsafe_allow_html=True)
                st.markdown(result)
                
                # Query rating system
                # st.markdown("---")
                # col1, col2, col3 = st.columns(3)
                # with col1:
                #     if st.button("👍 Good Response", use_container_width=True):
                #         log_query(query, result, "good", duration)
                #         st.toast("Rating saved - Good response")
                # with col2:
                #     if st.button("👎 Bad Response", use_container_width=True):
                #         log_query(query, result, "bad", duration)
                #         st.toast("Rating saved - Needs improvement")
                # with col3:
                #     if st.button("➖ Neutral", use_container_width=True):
                #         log_query(query, result, "neutral", duration)
                #         st.toast("Rating saved - Neutral")
                        
                # Copy button
                # st.code(result, language='markdown', line_numbers=False)
                # if st.button("📋 Copy Results"):
                #     st.session_state.copied_text = result
                #     st.toast("Results copied to clipboard!", icon="✅")
            
        except Exception as e:
            st.error(f"Error during search: {str(e)}")
            #st.error(f"Unexpected response type: {type(response)}")
            st.session_state.last_query_time = None
        # Display query history in sidebar
    

    
        # st.sidebar.title("📋 Query History")
        # if not st.session_state.query_history.empty:
        #     # Show interactive history table
        #     history_df = st.session_state.query_history.sort_values('timestamp', ascending=False)
            
        #     # Format timestamps
        #     history_df['timestamp'] = history_df['timestamp'].dt.strftime('%Y-%m-%d %H:%M')
            
        #     # Display with expandable details
        #     for _, row in history_df.iterrows():
        #         with st.sidebar.expander(f"{row['timestamp']}: {row['query'][:30]}..."):
        #             st.markdown(f"**Full Query:**\n{row['query']}")
        #             st.markdown("---")
        #             st.markdown(f"**Response:**\n{row['response']}")
        #             st.markdown(f"**Rating:** {row['rating'] or 'Not rated'}")
        #             st.markdown(f"**Response Time:** {row['response_time']}s")
                    
        #             # Quick actions
        #             if st.button("🗑️ Delete", key=f"del_{row['timestamp']}"):
        #                 delete_query(row['timestamp'])
        # else:
        #     st.sidebar.info("No queries yet. Your search history will appear here.")
            
        
    # # Custom styled logout button
    # st.sidebar.markdown("""
    # <style>
    # .logout-btn {
    #     background-color: #ff4b4b;
    #     color: white;
    #     border-radius: 4px;
    # }
    # </style>
    # """, unsafe_allow_html=True)

    # if st.sidebar.button("Logout", key="logout_btn", help="Click to logout", 
    #                     type="primary", use_container_width=True):
    #     logout()

# Add disclaimer section at the very bottom of the page
    # st.markdown("---")
    # st.markdown("""
    # **IMPORTANT NOTICE:**  
    # This web application is a prototype developed for educational purposes only.  
    # The information provided here is NOT intended for real-world usage and should not be relied upon for making any decisions, especially those related to financial, legal, or healthcare matters.  

    # Furthermore, please be aware that the LLM may generate inaccurate or incorrect information. You assume full responsibility for how you use any generated output.  

    # Always consult with qualified professionals for accurate and personalized advice.
    # """)

    # Optional styling for the disclaimer
    st.markdown("""
    <style>
    .disclaimer {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 5px;
        border-left: 4px solid #ff4b4b;
        margin-top: 20px;
        font-size: 0.9em;
    }
    </style>
    <div class="disclaimer">
        <strong>IMPORTANT NOTICE:</strong><br>
        This web application is a prototype developed solely for the AI Champion Bootcamp. <br><br>
        While the data is based on real-world usage, it should be used <strong>for reference purposes only</strong> and <strong>NOT</strong> relied upon for decision-making. 
        Guardrails have been implemented to generate outputs that are as accurate as possible; 
        however, you <strong>must</strong> assume full responsibility for any use of the generated content. <br><br>
        Always consult qualified professionals for advice.
    </div>
    """, unsafe_allow_html=True)
    
    # Show database stats
    st.sidebar.markdown(f"**Database Stats**")
    st.sidebar.markdown(f"Total Companies: {vectordb._collection.count()}")
    st.sidebar.divider()

# Example usage in your main app
if __name__ == "__main__":
    display_results()
    
    
    # <div class="disclaimer">
    #     <strong>IMPORTANT NOTICE:</strong><br>
    #     This web application is a prototype developed for educational purposes only.<br>
    #     The information provided here is NOT intended for real-world usage and should not be relied upon for making any decisions.<br>
    #     LLM may generate inaccurate information. You assume full responsibility for any use of generated output.<br>
    #     Always consult qualified professionals for advice.
    # </div>