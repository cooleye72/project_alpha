import os
from crewai import Agent, Task, Crew
from crewai.tools import tool
from tavily import TavilyClient
from langchain_community.vectorstores import Chroma
import logging
from langchain_community.embeddings import OpenAIEmbeddings

# __import__('pysqlite3')
# import sys
# sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

# Initialize Tavily client
@tool
def tavily_search(query: str) -> str:
    """Search the internet for current information using Tavily API.
    Ideal for finding company data, market trends, and competitor analysis.
    Returns comprehensive results with sources."""
    tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    results = tavily.search(query=query, search_depth="basic")
    return str(results["results"])  # Return formatted results

# Load your existing vector database
vectordb = Chroma(
    persist_directory="./imda_vectordb",
    collection_name="imda_accred_companies",
    embedding_function=OpenAIEmbeddings()
)

# 1. Research Agent - Finds relevant companies from vector DB
portfolio_agent = Agent(
    role="Tech Research Specialist",
    goal="Identify EXISTING companies from the IMDA directory that best match the user's requirements",
    backstory="Specializes in analyzing and recommending from known company databases",
    verbose=True,
    tools=[],  # Uses vector DB directly
    allow_delegation=False,
    options={
        "strict_mode": True,  # Prevents hallucinations
        "only_use_existing_data": True
    }
)

# 2. Web Researcher Agent - Gathers additional online information
web_researcher = Agent(
    role="Web Research Specialist",
    goal="Find additional information about companies from public sources",
    backstory="Skilled at finding up-to-date information about companies from various online sources",
    verbose=True,
    tools=[tavily_search],
    allow_delegation=False
)

# 3. Management Consultant Agent - Bridges technical and business perspectives
consultant_agent = Agent(
    role="Management Consultant",
    goal="Analyze and present findings in a way that bridges technical and executive perspectives",
    backstory="Experienced consultant who translates technical capabilities into business value propositions",
    verbose=True,
    tools=[],
    allow_delegation=False
)

def company_search(company_data: str, use_case: str):
    """Task to find relevant companies from vector DB"""
    return Task(
        description=f"Identify from {company_data} that match: {use_case}",
        agent=portfolio_agent,
        expected_output="Shortlist most relevant companies with their key details from the IMDA database",
        async_execution=True,
        context=[]
    )

def web_research_task(company_info: str):
    """Task to gather additional online information"""
    return Task(
        description=f"Find recent information about this company: {company_info}",
        agent=web_researcher,
        expected_output="Updated information about the company's products, news, and recent developments",
        async_execution=True,
        context=[]
    )

def consultant_task(company_data: str, web_findings: str):
    """Task to analyze and present findings"""
    return Task(
        description="Analyze the company data and web findings to create an executive summary",
        agent=consultant_agent,
        expected_output="A concise report top 3 recommended IMDA companies with: 1) Company overview 2) Technical capabilities 3) Business value proposition 4) Recommendation 5) Accredited or Spark company status 6) TAL readiness status 7) Website links",
        context=[company_data, web_findings]
    )

def analyze_use_case(use_case: str):
    """Orchestrate the multi-agent analysis"""
    # First find relevant companies from vector DB
    docs = vectordb.similarity_search(use_case, k=5)
    company_info = "\n".join([doc.page_content for doc in docs])
    #logger.info(f"Company_info type: {type(company_info)}")
    #logger.info(f"company info: {company_info}")
    
    # Extract company names from metadata
    company_names = [doc.metadata['name'] for doc in docs if 'name' in doc.metadata]
    #logger.info(f"Found companies: {company_names}")
    
    # # Create tasks
    research_task = company_search(company_info, use_case)
    web_task = web_research_task(company_names)
    #logger.info(f"web_task type: {type(web_task)}")
    consult_task = consultant_task(research_task, web_task)
    
    # # Assemble crew
    crew = Crew(
        agents=[portfolio_agent, web_researcher, consultant_agent],
        tasks=[research_task, web_task, consult_task],
        verbose=True
    )
    
    # # Execute
    result = crew.kickoff()
    return result

# Example usage

# user_query = questions
# analysis_result = analyze_use_case(user_query)
# print("\nFinal Recommendation:")
# print(analysis_result)