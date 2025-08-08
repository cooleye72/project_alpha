import os
from crewai import Agent, Task, Crew
from crewai.tools import tool
from tavily import TavilyClient
from langchain_community.vectorstores import Chroma
import logging
from langchain_community.embeddings import OpenAIEmbeddings

# for streamlit cloud compatibility
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

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
# portfolio_agent = Agent(
#     role="Tech Analaysis Specialist",
#     goal="Identify EXISTING companies from the IMDA directory that best match the user's requirements",
#     backstory="Specializes in analyzing and recommending from known company databases",
#     verbose=True,
#     tools=[],  # Uses vector DB directly
#     allow_delegation=False,
#     options={
#         "strict_mode": True,  # Prevents hallucinations
#         "only_use_existing_data": True
#     }
# )
portfolio_agent = Agent(
    role="Tech Analysis Specialist",
    goal="""Identify the most semantically relevant companies from the IMDA directory 
    based on the user's requirements using advanced vector search techniques""",
    backstory="""An expert in semantic search and company matching with deep understanding 
    of vector similarity and business domain knowledge""",
    verbose=True,
    tools=[],
    allow_delegation=False,
    options={
        "strict_mode": True,
        "semantic_search": True,  # Enable enhanced semantic processing
        "similarity_threshold": 0.8  # Minimum match score
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
                #Identify from {company_data} that match: {use_case}
        description=f"""
        Perform semantic search to identify companies that best match: "{use_case}"
        
        Follow these steps:
        1. Analyze the user's query for key intent
        2. Map these intent to relevant company capabilities in the vectorstore
        3. Apply similarity scoring with threshold of 0.8
        4. Return only highly relevant matches with explanations
        
         Available company data: {company_data}
        """,
        agent=portfolio_agent,
        expected_output="Shortlist above 80% relevancy match score companies with their key details from the IMDA database",
        async_execution=True,
        context=[]
    )
# def company_search(company_data: str, use_case: str):
#     """Enhanced task for semantic company matching"""
#     return Task(
#         description=f"""
#         Perform semantic search to identify companies that best match: "{use_case}"
        
#         Follow these steps:
#         1. Analyze the user's query for key concepts and intent
#         2. Map these concepts to company capabilities in the vector space
#         3. Apply similarity scoring with threshold of 0.8
#         4. Return only highly relevant matches with explanations
        
#         Available company data: {company_data[:1000]}... [truncated]
#         """,
#         agent=portfolio_agent,
#         expected_output="""
#         ## Semantic Match Results (Score ≥70%)
        
#         For each matching company provide:
#         - **Company Name**: [name]
#         - **Match Score**: XX% (formatted to 2 decimal places)
#         - **Matching Factors**: 
#           - Primary matching concept: [concept] 
#           - Secondary factors: [factor1], [factor2]
#         - **Relevance Explanation**: 1-2 sentences explaining why this matches
#         - **Key Capabilities**: Bullet points of relevant capabilities
        
#         Format:
#         ### 1. [Company Name] (Match Score: XX%)
#         - **Matching Factors**: [factors]
#         - **Relevance**: [explanation]
#         - **Capabilities**:
#           - [Capability 1]
#           - [Capability 2]
#         """,
#         async_execution=True,
#         context=[]
#     )
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
        expected_output="""
        A concise report of recommended IMDA companies with: 
            1) Company overview (relevant match score) 
            2) Technical capabilities 
            3) Business value proposition 
            4) Recommendation 
            5) Accredited or Spark company status 
            6) TAL readiness status (If there is TAL Ready, please indicate else put Not applicable) 
            7) Website URL Link from IMDA directory
            
        You may include additional insight that offer relevant technologies beneficial to the user. Just indicate the Company Name and Website URL Link only.
        """,
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