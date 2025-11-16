import asyncio
import os  # Import os to access environment variables
from semantic_kernel import Kernel
from agent_one import AgentOne
from agent_two import AgentTwo
from agent_three import AgentThree
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- HOW TO SET YOUR API KEYS ---
# Before running this file, set your environment variables:
#
# In Windows Command Prompt:
# set NEWS_API_KEY=YOUR_NEWS_KEY_HERE
# set GEMINI_API_KEY=YOUR_NEW_GEMINI_KEY_HERE
#
# In PowerShell:
# $env:NEWS_API_KEY="YOUR_NEWS_KEY_HERE"
# $env:GEMINI_API_KEY="YOUR_NEW_GEMINI_KEY_HERE"
#
# In macOS/Linux:
# export NEWS_API_KEY='YOUR_NEWS_KEY_HERE'
# export GEMINI_API_KEY='YOUR_NEW_GEMINI_KEY_HERE'
#
# (Remember to use your NEW, non-leaked Gemini key)


async def main():
    kernel = Kernel()

    # --- API KEYS ARE REMOVED ---
    # The keys are now loaded securely inside AgentTwo
    # from environment variables.
    
    # Check if keys are set (optional but good practice)
    if not os.environ.get("NEWS_API_KEY") or not os.environ.get("GEMINI_API_KEY"):
        print("Error: NEWS_API_KEY or GEMINI_API_KEY environment variable is not set.")
        print("Please set them before running the script.")
        return

    agent1 = AgentOne()
    
    # *** FIX: AgentTwo now only takes the kernel as an argument ***
    agent2 = AgentTwo(kernel) 
    
    agent3 = AgentThree()

    tech = agent1.ask_user()
    print(f"\nAgent 2: Fetching news for {tech}...")
    
    news_summary = await agent2.fetch_and_generate_news(tech)

    print("\n--- Combined News Summary ---")
    print(news_summary)

    # For simplicity, user document is just the tech name repeated in a statement
    user_doc = f"User requested information for technology: {tech}"

    print("\nAgent 3: Comparing documents and generating visualization...")
    agent3.compare_and_visualize(user_doc, news_summary)
    print("\nVisualization complete. Check the output files.")


if __name__ == "__main__":
    asyncio.run(main())