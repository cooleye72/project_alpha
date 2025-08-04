import requests
import re
import logging
import os
import time
from bs4 import BeautifulSoup
from typing import Dict, List
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

# For website scrapping
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.core.os_manager import ChromeType

# for streamlit cloud compatibility
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager
# from webdriver_manager.core.os_manager import ChromeType

# Configure for Streamlit Cloud
# chrome_options = Options()
# chrome_options.add_argument("--headless")
# chrome_options.add_argument("--no-sandbox")
# chrome_options.add_argument("--disable-dev-shm-usage")
# chrome_options.add_argument("--disable-gpu")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

# Configuration
#BASE_URL = "https://www.imda.gov.sg/resources/innovative-tech-companies-directory"

# Function to get number of pages in the website
def get_page_range_selenium(url: str) -> Dict[str, int]:
    """Extract pagination info using Selenium (for JavaScript-rendered pages)"""
    
    #Set up Chrome options
    options = Options()
    options.add_argument("--disable-gpu")
    options.add_argument("--headless")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),
                                  options=options)
    logger.info(f"DEBUG:DRIVER:{driver}")
    # chrome_options = Options()
    # chrome_options.add_argument("--headless")
    # chrome_options.add_argument("--disable-gpu")
    
    # # Initialize browser with Service
    # service = Service(ChromeDriverManager().install())
    # driver = webdriver.Chrome(service=service, options=chrome_options)
    #driver = get_driver()
    try:
        driver.get(url)
        
        # Wait for pagination to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".pagination.innovative-tech-listing__pagination"))
        )
        
        # Extract page numbers using JavaScript
        pages = driver.execute_script("""
            const items = Array.from(document.querySelectorAll('.pagination__list li'));
            const numbers = items.map(li => {
                const link = li.querySelector('a');
                return link ? parseInt(link.dataset.page) : null;
            }).filter(Boolean);
            
            return {
                first: numbers[0] || 1,
                last: numbers[numbers.length - 2] || 1 
            };
        """)
        
        return {
            "first_page": pages['first'],
            "last_page": pages['last']
        }
        
    except Exception as e:
        logger.error(f"Selenium pagination error: {str(e)}")
        return {"first_page": 1, "last_page": 1}
    finally:
        driver.quit()

# Function to extract company URLs from the page
def extract_company_urls(target_url: str) -> list:
    # Set up Chrome options
    options = Options()
    options.add_argument("--headless")  # Run in background
    options.add_argument("--disable-gpu")
    
    # Initialize browser
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        # Load the page
        logger.info(f"Loading page: {target_url}")
        driver.get(target_url)
        
        # Wait for company links to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'a.teaser-card__link'))
        )
        
        # Find all company link elements
        company_links = driver.find_elements(By.CSS_SELECTOR, 'a.teaser-card__link')
        urls = [link.get_attribute('href') for link in company_links if link.get_attribute('href')]
        #logger.info(urls)
        logger.info(f"Extracted {len(urls)} company URLs")
        return urls
    
    except Exception as e:
        logger.error(f"Error extracting URLs from {target_url}: {str(e)}")
        return []
    finally:
        driver.quit()
        logger.info("Browser session ended")
        
    
# Function to extract company data from HTML
def extract_company_details(html_content):
    """Extract company details from IMDA company page HTML"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 1. Extract Company Name
    company_name = soup.find('h1', class_='page-title').get_text(strip=True) if soup.find('h1', class_='page-title') else None
    
    # Find the main article container
    article = soup.find('article', class_='detail-content')
    
    # Initialize all fields with None as default
    website_url = None
    contact_person = None
    contact_number = None
    contact_email = None
    category = None
    subcategory = None
    description = ""
    tags = []

    if article:
        # 2. Extract Website URL
        website_link = article.find('a', class_='link__external')
        if website_link and 'href' in website_link.attrs:
            website_url = website_link['href'].strip()
        
        # 3. Extract Contact Information
        contact_div = article.find('div', class_='highlight-card__text--main__contact')
        if contact_div:
            contact_text = contact_div.get_text(' ', strip=True)
            
            # Extract contact person (case-insensitive)
            contact_match = re.search(r'contact\s*person:([^+0-9\n]+)', contact_text, re.IGNORECASE)
            if contact_match:
                contact_person = contact_match.group(1).strip()
            
            # Extract contact number
            phone_match = re.search(r'(\+?\d[\d\s\-\(\)]{7,}\d)', contact_text)
            if phone_match:
                contact_number = phone_match.group(1).strip()
            
            # Extract email
            email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', contact_text)
            if email_match:
                contact_email = email_match.group(0).strip()
        
        # 4. Extract Category and Subcategory
        category_div = article.find('div', class_='highlight-card__text--category')
        if category_div:
            category_ps = category_div.find_all('p')
            for p in category_ps:
                text = p.get_text(' ', strip=True)
                if 'category:' in text.lower():
                    category = text.split(':')[-1].strip()
                elif 'sub-category:' in text.lower():
                    subcategory = text.split(':')[-1].strip()
        
        # 5. Extract Description
        rte_div = article.find('div', class_='rte')
        if rte_div:
            description = ' '.join([
                p.get_text(' ', strip=True) 
                for p in rte_div.find_all('p')
                if p.get_text(strip=True)
            ]).strip()
        
        # 6. Extract Tags
        tags_div = article.find('div', class_='tags-list__title')
        if tags_div:
            tags_list = tags_div.find_next('ul', class_='tags-list__list')
            if tags_list:
                tags = [
                    a.get_text(strip=True) 
                    for a in tags_list.find_all('a', class_='pill')
                    if a.get_text(strip=True)
                ]

    return {
        'company_name': company_name,
        'website_url': website_url,
        'contact_person': contact_person,
        'contact_number': contact_number,
        'contact_email': contact_email,
        'category': category,
        'subcategory': subcategory,
        'description': description,
        'tags': tags
    }

def process_all_pages(base_url: str) -> List[Dict]:
    """Process all pages of company directory with URL logging"""
    try:
        # Get # of pages using Selenium
        page_info = get_page_range_selenium(base_url)
        logger.info(f"Found pages: {page_info['first_page']} to {page_info['last_page']}")
        
        all_companies = []
     
        # Get all company URLs from each page                         
        for page in range(page_info["first_page"], page_info["last_page"] + 1):
            url = f"{base_url}?page={page}"
            logger.info(f"🔄 Processing page URL: {url}")  # Added URL logging
            
            try:
                # Get company URLs from this page
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                companies_urls = extract_company_urls(url)
                #all_companies.extend(companies_urls)
                logger.info(f"✅ Processed page {page}/{page_info['last_page']} - {len(companies_urls)} companies")
                
                for companies_url in companies_urls:
                    try:
                        # Extract detailed company info
                        #company_html = driver.page_source
                        logger.info(f"[Process_all_pages] Passing company URL: {companies_url}")
                        response = requests.get(companies_url, timeout=10)
                        if response.status_code == 200:
                            company_data = extract_company_details(response.text)
                            logger.info(f"[Process_all_pages] Extracting data: {company_data}")
                            all_companies.append(company_data)
                            #print(company_data)
                        else:
                            print(f"Failed to fetch page. Status code: {response.status_code}")
                        
                    except Exception as e:
                        logger.error(f"⚠️ Error processing company page {companies_url}: {str(e)}")
                        continue
                    
            except Exception as e:
                logger.error(f"⚠️ Error processing {url}: {str(e)}")
                continue
        
        # Final log before returning
        logger.info(f"Total companies collected: {len(all_companies)}")
        #logger.debug(f"Sample company data: {all_companies[0] if all_companies else 'No data'}")
        
        #logger.info(all_companies)    
        return all_companies

        # Process each page and extract company data
    except Exception as e:
        logger.error(f"❌ Fatal error in processing: {str(e)}")
        return []
