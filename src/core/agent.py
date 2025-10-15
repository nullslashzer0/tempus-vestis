"""
Agent implementation for TempusVestis.

This module creates a LangChain Agent Executor that dynamically selects
and uses tools to provide weather-based wardrobe recommendations.
"""

import os
from typing import Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from tools.date_ops import get_current_date, calculate_future_date
from tools.weather_api import get_weather_forecast
from core.prompts import (
    WARDROBE_CONSULTANT_SYSTEM_PROMPT,
    CLARIFICATION_PROMPT,
    WEATHER_ERROR_PROMPT
)


def create_wardrobe_agent(
    model_name: str = "gpt-4o-mini",
    temperature: float = 0.7,
    verbose: bool = True
) -> AgentExecutor:
    """
    Create a wardrobe consultant agent with dynamic tool selection.
    
    Args:
        model_name: The OpenAI model to use
        temperature: The temperature for LLM responses
        verbose: Whether to show verbose output
        
    Returns:
        An AgentExecutor configured with the wardrobe consultant tools
    """
    # Initialize the LLM
    llm = ChatOpenAI(
        model=model_name,
        temperature=temperature,
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    # Define the tools available to the agent
    tools = [
        get_current_date,
        calculate_future_date,
        get_weather_forecast,
    ]
    
    # Create the prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", WARDROBE_CONSULTANT_SYSTEM_PROMPT),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    
    # Create the agent
    agent = create_openai_functions_agent(llm, tools, prompt)
    
    # Create and return the agent executor
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=verbose,
        handle_parsing_errors=True,
        max_iterations=10,
        return_intermediate_steps=True,
    )
    
    return agent_executor


def run_agent(
    query: str,
    agent: Optional[AgentExecutor] = None,
    verbose: bool = True
) -> Dict[str, Any]:
    """
    Run the agent with a user query.
    
    Args:
        query: The user's question or request
        agent: An existing agent executor (if None, creates a new one)
        verbose: Whether to show verbose output
        
    Returns:
        A dictionary containing the agent's output and intermediate steps
    """
    if agent is None:
        agent = create_wardrobe_agent(verbose=verbose)
    
    try:
        result = agent.invoke({"input": query})
        
        # Check if any errors occurred in tool calls
        if "intermediate_steps" in result:
            for action, observation in result["intermediate_steps"]:
                # Check for error patterns in observations
                if isinstance(observation, str):
                    if "error" in observation.lower() or "exception" in observation.lower():
                        # Inject error handling context
                        result["has_errors"] = True
                        
        return result
    except KeyError as e:
        # Handle missing location or ambiguous input
        if "properties" in str(e) or "forecast" in str(e):
            return {
                "output": f"{WEATHER_ERROR_PROMPT}\n\nError details: {str(e)}",
                "error": str(e),
                "error_type": "weather_api",
                "intermediate_steps": []
            }
        return {
            "output": f"{CLARIFICATION_PROMPT}\n\nI need more specific information to help you. Could you provide more details about your destination and travel dates?",
            "error": str(e),
            "error_type": "clarification",
            "intermediate_steps": []
        }
    except Exception as e:
        error_message = str(e).lower()
        
        # Check for specific error types
        if "location" in error_message or "coordinates" in error_message:
            return {
                "output": f"{WEATHER_ERROR_PROMPT}",
                "error": str(e),
                "error_type": "location",
                "intermediate_steps": []
            }
        elif "date" in error_message or "time" in error_message:
            return {
                "output": f"{CLARIFICATION_PROMPT}\n\nI'm not sure about the dates you mentioned. Could you provide a specific date or number of days from now?",
                "error": str(e),
                "error_type": "date",
                "intermediate_steps": []
            }
        else:
            return {
                "output": f"I encountered an error while processing your request. Please try rephrasing with more specific details about your destination and travel dates.\n\nError: {str(e)}",
                "error": str(e),
                "error_type": "general",
                "intermediate_steps": []
            }


def get_agent_response(
    query: str,
    verbose: bool = False
) -> str:
    """
    Convenience function to get just the text response from the agent.
    
    Args:
        query: The user's question or request
        verbose: Whether to show verbose output
        
    Returns:
        The agent's text response
    """
    result = run_agent(query, verbose=verbose)
    return result.get("output", "I'm sorry, I couldn't process that request.")


class WardrobeAgent:
    """
    A wrapper class for the wardrobe consultant agent.
    
    This provides a cleaner interface for using the agent in applications.
    """
    
    def __init__(
        self,
        model_name: str = "gpt-4o-mini",
        temperature: float = 0.7,
        verbose: bool = False
    ):
        """
        Initialize the wardrobe agent.
        
        Args:
            model_name: The OpenAI model to use
            temperature: The temperature for LLM responses
            verbose: Whether to show verbose output
        """
        self.agent = create_wardrobe_agent(
            model_name=model_name,
            temperature=temperature,
            verbose=verbose
        )
        self.verbose = verbose
    
    def ask(self, query: str) -> str:
        """
        Ask the agent a question and get a text response.
        
        Args:
            query: The user's question or request
            
        Returns:
            The agent's text response
        """
        result = self.agent.invoke({"input": query})
        return result.get("output", "I'm sorry, I couldn't process that request.")
    
    def get_detailed_response(self, query: str) -> Dict[str, Any]:
        """
        Get a detailed response including intermediate steps.
        
        Args:
            query: The user's question or request
            
        Returns:
            A dictionary with the output and intermediate steps
        """
        return self.agent.invoke({"input": query})
    
    def explain_reasoning(self, query: str) -> None:
        """
        Run the agent and print detailed reasoning steps.
        
        Args:
            query: The user's question or request
        """
        result = self.get_detailed_response(query)
        
        print("=" * 80)
        print("QUERY:", query)
        print("=" * 80)
        
        if "intermediate_steps" in result:
            print("\nREASONING STEPS:")
            for i, (action, observation) in enumerate(result["intermediate_steps"], 1):
                print(f"\nStep {i}:")
                print(f"  Tool: {action.tool}")
                print(f"  Input: {action.tool_input}")
                print(f"  Output: {observation}")
        
        print("\n" + "=" * 80)
        print("FINAL RESPONSE:")
        print("=" * 80)
        print(result.get("output", "No response generated."))
        print("=" * 80)

