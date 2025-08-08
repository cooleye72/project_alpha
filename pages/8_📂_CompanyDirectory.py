import streamlit as st
from langchain.vectorstores import Chroma
from langchain_community.embeddings import OpenAIEmbeddings
import logging
import pandas as pd

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

def get_company_data(vectordb):
    """Retrieve all company data from ChromaDB"""
    try:
        # Get all documents with metadata
        results = vectordb._collection.get(
            include=["metadatas", "documents"]
        )
        
        # Build DataFrame
        companies = []
        for idx, meta in enumerate(results["metadatas"]):
            # Safely extract metadata with fallbacks
            companies.append({
                "Company Name": meta.get("name", "N/A"),
                "Website": meta.get("website", "N/A"),
                "Tags": meta.get("tags", "N/A"),
            })
        
        return pd.DataFrame(companies)
    
    except Exception as e:
        logger.error(f"Error retrieving company data: {str(e)}")
        return pd.DataFrame()

def main():
    st.set_page_config(page_title="Company Directory | Jeron.AI", layout="centered")
    st.title("📂 Accredited Companies Directory")
    
    # Initialize vector DB
    try:
        vectordb = initialize_vectordb()
        company_df = get_company_data(vectordb)
        
        if company_df.empty:
            st.warning("No company data found in the database")
            return
    except:
        return
    
    # Initialize session state for pagination
    if 'page' not in st.session_state:
        st.session_state.page = 1
        
    # Search and filter section
    st.sidebar.header("Search & Filter")
    
    # Text search
    search_term = st.sidebar.text_input("Search companies")
    st.sidebar.divider()
    # Category filter
    # all_categories = ["All"] + sorted(company_df["Main Category"].unique().tolist())
    # selected_category = st.sidebar.selectbox("Filter by category", all_categories)
    
    # Apply filters
    filtered_df = company_df.copy()
    if search_term:
        filtered_df = filtered_df[
            filtered_df["Company Name"].str.contains(search_term, case=False)
        ]
        # Handle empty search results
        if filtered_df.empty:
            st.info(f"No companies found matching '{search_term}'")
            st.markdown("""
            <div style="margin-top: 1rem; padding: 1rem; background: #f8f9fa; border-radius: 0.5rem;">
                <p>Try these suggestions:</p>
                <ul>
                    <li>Check your spelling</li>
                    <li>Use fewer keywords</li>
                    <li>Browse all companies instead</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            return
    
    # if selected_category != "All":
    #     filtered_df = filtered_df[filtered_df["Main Category"] == selected_category]
    
    # Display results
    st.subheader(f"Showing {len(filtered_df)} companies")
    
    # Pagination settings
    items_per_page = 10
    total_pages = max(1, (len(filtered_df) // items_per_page) + 
                     (1 if len(filtered_df) % items_per_page else 0))
    
    # Calculate display range
    start_idx = (st.session_state.page - 1) * items_per_page
    end_idx = start_idx + items_per_page

    # Display the paginated table with improved styling
    st.dataframe(
        filtered_df.iloc[start_idx:end_idx],
        column_config={
            "Company Name": st.column_config.TextColumn(width="medium"),
            "Description": st.column_config.TextColumn(width="large")
        },
        hide_index=True,
        use_container_width=True
    )
    
    # Show item range info
    st.caption(f"Showing items {start_idx+1}-{min(end_idx, len(filtered_df))} of {len(filtered_df)}")
     
    # Previous/Next arrows
    if total_pages > 1:
        prev_col, _, next_col = st.columns([1, 8, 1])
        
        with prev_col:
            if st.button("◀", disabled=(st.session_state.page == 1), 
                        help="Previous page", key="prev_page"):
                st.session_state.page = max(1, st.session_state.page - 1)
        
        with next_col:
            if st.button("▶", disabled=(st.session_state.page == total_pages), 
                        help="Next page", key="next_page"):
                st.session_state.page = min(total_pages, st.session_state.page + 1)
        
    # Show database stats
    
    st.sidebar.markdown(f"**Database Stats**")
    st.sidebar.markdown(f"Total Companies: {len(company_df)}")
    st.sidebar.divider()

    # st.sidebar.markdown(f"Categories: {len(company_df['Main Category'].unique())}")

if __name__ == "__main__":
    main()