import requests
import httpx
import os  # Import the os module
from semantic_kernel import Kernel, prompt_template
from semantic_kernel.prompt_template.prompt_template_config import PromptTemplateConfig, InputVariable
import asyncio

# --- IMPORTANT SECURITY NOTE ---
# NEVER paste your API keys directly into your code.
# Use environment variables.
#
# How to set environment variables:
#
# In Windows Command Prompt:
# set NEWS_API_KEY=YOUR_KEY_HERE
# set GEMINI_API_KEY=YOUR_NEW_REVOKED_KEY_HERE
#
# In PowerShell:
# $env:NEWS_API_KEY="YOUR_KEY_HERE"
# $env:GEMINI_API_KEY="YOUR_NEW_REVOKED_KEY_HERE"
#
# In macOS/Linux:
# export NEWS_API_KEY='YOUR_KEY_HERE'
# export GEMINI_API_KEY='YOUR_NEW_REVOKED_KEY_HERE'


class AgentTwo:
    def __init__(self, kernel: Kernel):
        self.kernel = kernel
        
        # Load keys securely from environment variables
        self.news_api_key = os.environ.get("NEWS_API_KEY")
        self.gemini_api_key = os.environ.get("GEMINI_API_KEY")

        # Check if keys are loaded
        if not self.news_api_key:
            raise ValueError("NEWS_API_KEY environment variable not set.")
        if not self.gemini_api_key:
            # Remind to revoke the leaked key
            print("--- WARNING ---")
            print("Your previous Gemini API key was exposed in your error log.")
            print("Please make sure you have revoked it and are using a NEW key.")
            print("Set the new key in the 'GEMINI_API_KEY' environment variable.")
            print("---------------")
            raise ValueError("GEMINI_API_KEY environment variable not set.")


        config = prompt_template.PromptTemplateConfig(
            template_format="jinja2",
            description="Summarize combined tech news",
            input_variables=[
                InputVariable(name="news", description="The news to summarize", is_required=True),
            ],
        )
        self.news_doc_template = prompt_template.Jinja2PromptTemplate(
            name="NewsSummaryTemplate",
            template="Summarize the following technology news:\n{{ news }}",
            prompt_template_config=config
        )

    def fetch_newsapi_news(self, query: str) -> str:
        url = f"https://newsapi.org/v2/everything?q={query}&apiKey={self.news_api_key}"
        try:
            response = requests.get(url)
            response.raise_for_status() # Check for HTTP errors
            articles = response.json().get("articles", [])
            if not articles:
                return "No articles found by NewsAPI."
            return "\n".join([f"{a.get('title')}: {a.get('description')}" for a in articles[:3]])
        except requests.exceptions.RequestException as e:
            print(f"Error fetching from NewsAPI: {e}")
            return "Could not retrieve news from NewsAPI."

    async def fetch_gemini_news(self, query: str) -> str:
        
        # *** FIX: This URL is correct. ***
        # It uses 'v1beta' and a valid model 'gemini-1.5-flash'.
        # Your error showed 'v1' and 'gemini-pro', which was incorrect.
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.gemini_api_key}"
        
        headers = {"Content-Type": "application/json"}
        data = {
            "contents": [{
                "parts": [{
                    "text": f"Find recent news about {query}"
                }]
            }]
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, json=data)
                
                # This will now succeed instead of giving a 404
                response.raise_for_status() 
                result = response.json()
                
                # Extract the text from the response
                if 'candidates' in result and result['candidates']:
                    content = result['candidates'][0].get('content', {})
                    if 'parts' in content and content['parts']:
                        return content['parts'][0].get('text', '')
                
                # Handle cases where Gemini returns an empty or unexpected response
                if 'promptFeedback' in result:
                    return f"Gemini API blocked the request: {result['promptFeedback']}"
                return "Could not parse news from Gemini response."
                
        except httpx.HTTPStatusError as e:
            print(f"HTTP error fetching from Gemini: {e}")
            return f"Could not retrieve news from Gemini (HTTP Error: {e.response.status_code})."
        except Exception as e:
            print(f"An unexpected error occurred with Gemini: {e}")
            return "Could not retrieve news from Gemini."

    async def fetch_and_generate_news(self, tech: str) -> str:
        # Run the synchronous fetch_newsapi_news in a separate thread
        # to avoid blocking the asyncio event loop.
        newsapi_news = await asyncio.to_thread(self.fetch_newsapi_news, tech)
        
        gemini_news = await self.fetch_gemini_news(tech)
        
        combined_news = f"--- News from NewsAPI ---\n{newsapi_news}\n\n--- News from Gemini ---\n{gemini_news}"
        
        # Render the template
        return self.news_doc_template.render(self.kernel, {"news": combined_news})