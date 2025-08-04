import os
import streamlit as st
from crewai import Agent, Task, Crew
from dotenv import load_dotenv
from st_oauth import st_google_oauth
from redisvl.extensions.cache.llm import SemanticCache
from redisvl.utils.vectorize import OpenAIVectorizer
        
# --- Redis Cache Setup ---
class RecommendationCache:
    def __init__(self):
        self.cache = SemanticCache(
            name="crewai_cache",
            redis_url=os.getenv("REDIS_URL"),
            vectorizer=OpenAIVectorizer(
                model="text-embedding-3-large",
                api_key=os.getenv("OPENAI_API_KEY")
            )
        )
    
    def check(self, query: str):
        return self.cache.check(query)
    
    def store(self, query: str, response: str):
        self.cache.store(query, response)