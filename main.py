"""
TempusVestis - AI-Powered Wardrobe Consultant

This is the main CLI application that orchestrates the agent and RAG system
using a sequential chain approach.
"""

import os
import sys
from dotenv import load_dotenv
from typing import Dict, Any

from core.constants import APP_NAME
from core.agent import WardrobeAgent
from core.rag import WardrobeRAG

# Load environment variables
load_dotenv()


def print_banner():
    """Print the application banner."""
    banner = f"""
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║                     TEMPUS VESTIS                        ║
║            AI-Powered Wardrobe Consultant                ║
║                                                          ║
║    Your intelligent packing assistant for weather-       ║
║         based wardrobe recommendations                   ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
"""
    print(banner)


def print_help():
    """Print usage instructions."""
    help_text = """
USAGE:
  Simply describe your travel plans, and I'll help you pack!

EXAMPLES:
  • "What should I pack for Chicago in 7 days?"
  • "I'm going to Miami next weekend, what should I wear?"
  • "Help me pack for San Francisco 10 days from now"
  
NOTE: Currently supports US locations only (National Weather Service API)

COMMANDS:
  help  - Show this help message
  quit  - Exit the application
  exit  - Exit the application
"""
    print(help_text)


def run_sequential_chain(query: str, verbose: bool = False) -> str:
    """
    Run the sequential chain: Agent (tools) → RAG (recommendations)
    
    Step 1: Agent retrieves weather data using tools
    Step 2: RAG uses weather data + wardrobe knowledge for final recommendations
    
    Args:
        query: User's query
        verbose: Whether to show verbose output
        
    Returns:
        Final wardrobe recommendations
    """
    print("\n🔍 Analyzing your request...")
    
    # Step 1: Use Agent to get weather data
    agent = WardrobeAgent(verbose=verbose)
    
    try:
        result = agent.get_detailed_response(query)
        
        # Check for errors
        if "error" in result:
            return result["output"]
        
        # Extract weather data from intermediate steps
        weather_data = None
        for action, observation in result.get("intermediate_steps", []):
            if action.tool == "get_weather_forecast":
                weather_data = observation
                break
        
        # If we have weather data, use RAG for enhanced recommendations
        if weather_data:
            print("🌤️  Weather data retrieved successfully")
            print("📚 Consulting wardrobe knowledge base...")
            
            # Step 2: Use RAG to generate recommendations
            rag = WardrobeRAG()
            
            recommendations = rag.get_recommendations(query, weather_data)
            
            return recommendations
        else:
            # No weather data, return agent's response
            return result.get("output", "I couldn't process that request.")
            
    except Exception as e:
        return f"An error occurred: {str(e)}\n\nPlease try rephrasing your request with specific location and dates."


def interactive_mode():
    """Run the application in interactive mode."""
    print_banner()
    print_help()
    
    while True:
        try:
            # Get user input
            print("\n" + "="*60)
            user_input = input("\n💬 You: ").strip()
            
            # Handle commands
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit']:
                print("\n👋 Thanks for using TempusVestis! Safe travels!")
                break
            
            if user_input.lower() == 'help':
                print_help()
                continue
            
            # Process the query
            print("\n🤖 TempusVestis:")
            response = run_sequential_chain(user_input, verbose=False)
            print("\n" + response)
            
        except KeyboardInterrupt:
            print("\n\n👋 Thanks for using TempusVestis! Safe travels!")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            print("Please try again.")


def single_query_mode(query: str):
    """Run a single query and exit."""
    print_banner()
    print(f"\n💬 Query: {query}")
    print("\n🤖 TempusVestis:")
    
    response = run_sequential_chain(query, verbose=False)
    print("\n" + response)


def main():
    """Main entry point for the application."""
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ ERROR: OPENAI_API_KEY not found in environment variables.")
        print("Please create a .env file with your OpenAI API key.")
        sys.exit(1)
    
    # Check if a query was provided as command-line argument
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        single_query_mode(query)
    else:
        interactive_mode()


if __name__ == "__main__":
    main()