import requests
import re
import logging
import os
import streamlit as st
from typing import Dict, List
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
VECTORDB_PATH = "./imda_vectordb"
CHUNK_SIZE = 10000
CHUNK_OVERLAP = 0

def create_vector_db(companies: List[Dict]) -> Chroma:
    """Create and persist vector database"""
    logger.info(f"Entered create_vector_db function with {len(companies)} companies")
    if not companies:
        raise ValueError("No companies data provided")
    
    # if 'vectordb' in st.session_state:
    #     st.session_state.vectordb.delete_collection()
    #     st.session_state.vectordb = None
    #     logger.info("Existing vector collection deleted")
    #logger.info(companies)
    
     # Check and cleanup existing vector DB
    logger.info(f"Checking for existing vector DB at {VECTORDB_PATH}")
    try:
        if os.path.exists(VECTORDB_PATH):
            logger.info(f"Found existing vector DB at {VECTORDB_PATH}, cleaning up...")
            
            # Initialize connection to existing DB
            existing_db = Chroma(
                persist_directory=VECTORDB_PATH,
                collection_name="imda_accred_companies",
                embedding_function=OpenAIEmbeddings()
            )
            
            # Delete collection if exists
            collection_count = existing_db._collection.count()
            if collection_count > 0:
                logger.info(f"Deleting existing collection with {collection_count} documents")
                existing_db.delete_collection()
            
            # # Clean up files
            # for f in os.listdir(VECTORDB_PATH):
            #     os.remove(os.path.join(VECTORDB_PATH, f))
            # logger.info("Existing vector DB cleaned up successfully")
            
    except Exception as e:
        logger.warning(f"Error cleaning up existing vector DB: {str(e)}")
        raise
                    
    texts = []
    metadatas = []
    
    for company in companies:
        # Create document text combining relevant fields
        doc_text = (
            f"Company: {company.get('company_name', '')}\n"
            f"Website: {company.get('website_url', '')}\n"
            f"Description: {company.get('description', '')}\n"
            f"Category: {company.get('category', '')}\n"
            f"Subcategory: {company.get('subcategory', '')}\n"
            f"Tags: {', '.join(company.get('tags', []))}"
        )
        
        # Preserve all metadata
        metadata = {
            'source': company.get('source_url', '') or '',
            'name': company.get('company_name', '') or '',
            'category': company.get('category', '') or '',
            'subcategory': company.get('subcategory', '') or '',
            'contact': company.get('contact_person', '') or '',
            'website': company.get('website_url', '') or '',
            'page': company.get('page_scraped', 0) or '',
            'tags': ', '.join(company.get('tags', [])) or ''# Convert list to comma-separated string
        }
        
        texts.append(doc_text)
        metadatas.append(metadata)
        
    
    # Split documents
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=10000,
        chunk_overlap=0,
        length_function=len
    )
    
    splitted_documents = text_splitter.create_documents(texts, metadatas=metadatas)
    logger.info(splitted_documents)
    # Create vector store
    try:
        embedding_model = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))
        vectordb = Chroma.from_documents(
            collection_name="imda_accred_companies",  # Specify a collection name here if needed
            documents=splitted_documents,
            embedding=embedding_model,
            persist_directory=VECTORDB_PATH
        )
        vectordb.persist()
        logger.info(f"VectorDB created with {len(splitted_documents)} documents")
        logger.info(f"Total vectordb collection count: {vectordb._collection.count()}")
        return vectordb
    except Exception as e:
        logger.error(f"Error creating vector DB: {str(e)}")
        raise