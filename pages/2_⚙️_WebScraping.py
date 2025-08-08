import streamlit as st
import time
import logging
from datetime import datetime
from logics.websitescrapping import process_all_pages
from logics.vectordb import create_vector_db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.set_page_config(
    layout="centered",
    page_title="Webpage Scrapping"
)

# if st.button("Start Scrapping", type="primary"):
#     st.write("Scraping in progress...") 
#     companies = process_all_pages(BASE_URL)
    
def scrape_companies(BASE_URL):
    """Simulate scraping process - replace with your actual scraping function"""
    # Replace this with your actual scraping code from process_all_pages()
    scraped_companies = process_all_pages(BASE_URL)
    time.sleep(3)  # Simulate scraping delay
    #scraped_companies = 125  # Replace with len(companies) from your scraping
    return scraped_companies

def main():
    st.set_page_config(page_title="Website Scraping | Jeron.AI", layout="centered")
    st.header("IMDA Accreditation Company Scraper")
    BASE_URL = st.text_input("URL to extract companies", "https://www.imda.gov.sg/resources/innovative-tech-companies-directory", disabled=True)
    # Initialize session state for tracking
    if 'scraping_status' not in st.session_state:
        st.session_state.scraping_status = "ready"  # ready, in_progress, completed
        st.session_state.vectordb_status = "ready"
        st.session_state.companies_scraped = 0
        st.session_state.start_time = None
        
    # Button to start scraping
    if st.button(
        "Start Scraping", 
        disabled=st.session_state.scraping_status == "in_progress",
        type="primary"
    ):
        st.session_state.scraping_status = "in_progress"
        st.session_state.start_time = datetime.now()
        st.session_state.last_scrape_time = datetime.now()
        st.rerun()  # Force immediate UI update
        
    # Status display container
    status_container = st.empty()
    
    # # Button to start scraping
    # if st.button("Start Scraping", disabled=st.session_state.scraping_status == "in_progress"):
    #     st.session_state.scraping_status = "in_progress"
    #     st.session_state.start_time = datetime.now()
    #     st.session_state.last_scrape_time = datetime.now()
    #     #st.rerun()  # Force immediate UI update
        
        # Display initial status
    # Handle the scraping process
    if st.session_state.scraping_status == "in_progress":
        with status_container:
            with st.status("Scraping in progress...", expanded=True) as status:
                st.write("Connecting to IMDA website...")
                time.sleep(1)  # Simulate connection time
                
                # Run the actual scraping
                try:
                    st.write("Extracting company data...")
                    st.session_state.companies_scraped = scrape_companies(BASE_URL)
                    st.session_state.companies_scraped_count = len(st.session_state.companies_scraped)  
                    st.session_state.scraping_status = "completed"
                    
                    # Update VectorDB
                    st.write("🛠️ Updating Vector Database...")
                    logger.info(f"Creating vector DB with {st.session_state.companies_scraped_count} companies")
                    st.session_state.vectordb = create_vector_db(st.session_state.companies_scraped)
                    st.session_state.vectordb_status = "updated"
                    
                    # Calculate duration
                    duration = datetime.now() - st.session_state.start_time
                    st.write(f"✅ Completed! Scraped {st.session_state.companies_scraped_count} companies")
                    st.write(f"⏱️ Duration: {duration.total_seconds():.1f} seconds")
                    status.update(label="Scraping complete!", state="complete", expanded=False)

                except Exception as e:
                    st.session_state.scraping_status = "error"
                    st.error(f"Scraping failed: {str(e)}")
                    status.update(label="Scraping failed", state="error")
        st.rerun() # Update UI after completion
    
    # Display current status
    if st.session_state.scraping_status == "completed":
        st.success(f"""
        **Scraping Results**  
        📊 Companies Processed: {st.session_state.companies_scraped_count}  
        🗄️ VectorDB Status: {st.session_state.vectordb_status.upper()}  
        🕒 Last Run: {st.session_state.last_scrape_time.strftime('%Y-%m-%d %H:%M:%S')}  
        """)
        #🕒 Duration Taken: {duration.total_seconds():.1f seconds}  
    elif st.session_state.scraping_status == "in_progress":
        st.warning("Scraping in progress... Please wait")
    elif st.session_state.scraping_status == "error":
        st.error("An error occurred during scraping")
###############################

    
# def main():
#     st.title("IMDA Company Directory Scraper")
#     BASE_URL = st.text_input("URL to scrap", "https://www.imda.gov.sg/resources/innovative-tech-companies-directory")
#     # Initialize session state
#     if 'scraping' not in st.session_state:
#         st.session_state.scraping = False
#         st.session_state.companies_scraped = 0
#         st.session_state.last_scrape_time = None

#     # Status display container
#     status_container = st.empty()
    
#     # Scrape button with dynamic disabled state
#     if st.button(
#         "🚀 Start Scraping",
#         disabled=st.session_state.scraping,
#         key="scrape_button",
#         help="Click to begin scraping IMDA company directory" if not st.session_state.scraping else "Scraping in progress..."
#     ):
#         try:
#             # Update state
#             st.session_state.scraping = True
#             st.session_state.last_scrape_time = datetime.now()
#             st.rerun()  # Force immediate UI update
            
#             # Show progress
#             with status_container:
#                 with st.status("🔄 Scraping IMDA website...", expanded=True) as status:
#                     st.write("🔍 Extracting company listings...")
                    
#                     # Execute scraping (replace with your function)
#                     st.session_state.companies_scraped = scrape_companies(BASE_URL)
                    
#                     # Show completion
#                     duration = datetime.now() - st.session_state.last_scrape_time
#                     st.write(f"✅ Successfully scraped {st.session_state.companies_scraped} companies")
#                     st.write(f"⏱️ Completed in {duration.total_seconds():.1f} seconds")
#                     status.update(label="Scraping Complete", state="complete", expanded=False)
            
#             # Reset button state
#             st.session_state.scraping = False
            
#             # Rerun to update UI
#             st.rerun()
            
#         except Exception as e:
#             st.session_state.scraping = False
#             status.update(label="Scraping Failed", state="error")
#             st.error(f"Error occurred: {str(e)}")
#             st.rerun()

#     # Display results after completion
#     if st.session_state.companies_scraped > 0 and not st.session_state.scraping:
#         st.success(f"""
#         **Scraping Results**  
#         📊 Companies Collected: {st.session_state.companies_scraped}  
#         🕒 Last Run: {st.session_state.last_scrape_time.strftime('%Y-%m-%d %H:%M:%S')}
#         """)
        
if __name__ == "__main__":
    main()
