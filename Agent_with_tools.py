from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import Literal
from RAG_tool import rag_tool   
import logging
import json
load_dotenv()
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("langchain")
logger.setLevel(logging.DEBUG)

load_dotenv()



# ---------------- TOOL 1: Database Search ----------------
@tool
def search_database(query: str, limit: int = 10) -> str:
    """Search the customer database for records matching the query.

    Args:
        query: Search terms to look for
        limit: Maximum number of results to return
    """
    print(f" DATABASE TOOL CALLED with query: '{query}', limit: {limit}")
    return f"Found {limit} results for '{query}'"

# ---------------- TOOL 2: Weather Info ----------------
class WeatherInput(BaseModel):
    """Input for weather queries."""
    location: str = Field(description="City name or coordinates")
    units: Literal["celsius", "fahrenheit"] = Field(
        default="celsius",
        description="Temperature unit preference"
    )
    include_forecast: bool = Field(
        default=False,
        description="Include 5-day forecast"
    )

@tool(args_schema=WeatherInput)
def get_weather(location: str, units: str = "celsius", include_forecast: bool = False) -> str:
    """Get current weather and optional forecast."""
    print(f" WEATHER TOOL CALLED for location: '{location}', units: '{units}', forecast: {include_forecast}")
    temp = 24 if units == "celsius" else 75
    result = f"Current weather in {location}: {temp}°{units[0].upper()}"
    if include_forecast:
        result += "\nNext 5 days: Sunny "
    return result



# ---------------- BUFFER HISTORY ----------------

@tool
def simple_math(expression: str) -> str:
    """Perform a simple math calculation."""
    print(f" MATH TOOL CALLED with expression: '{expression}'")
    try:
        result = eval(expression, {"__builtins__": {}})
        return str(result)
    except Exception as e:
        return f"Error in calculation: {e}"
    


# # ---------------- SIMPLE AGENT ----------------
# def create_chat_agent():
#     """Create and return a simple tool-calling agent."""
#     model = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
    
#     # Bind tools to model
#     tools = [search_database, get_weather, simple_math, rag_tool]
#     model_with_tools = model.bind_tools(tools)
    
#     return model_with_tools

# def run_agent(model_with_tools, user_input):
#     """Run the agent with tool calling capability."""
#     system_prompt = "You are an AI assistant that helps users by using tools when needed. Use the appropriate tool for each query and provide helpful responses."
    
#     messages = [
#         SystemMessage(content=system_prompt),
#         HumanMessage(content=user_input)
#     ]
    
#     # Get initial response
#     response = model_with_tools.invoke(messages)
    
#     # Check if tools were called
#     if response.tool_calls:
#         print(f" Calling {len(response.tool_calls)} tool(s)...")
        
#         # Execute each tool call
#         for tool_call in response.tool_calls:
#             tool_name = tool_call["name"]
#             tool_args = tool_call["args"]
            
#             # Find and execute the tool
#             tools_dict = {
#                 "search_database": search_database,
#                 "get_weather": get_weather, 
#                 "simple_math": simple_math,
#                 "rag_tool": rag_tool
#             }
            
#             if tool_name in tools_dict:
#                 try:
#                     result = tools_dict[tool_name].invoke(tool_args)
#                     print(f" {tool_name}: {result[:100]}...")
#                 except Exception as e:
#                     result = f"Error: {e}"
#                     print(f" {tool_name}: {result}")
        
#         # Get final response after tool execution
#         messages.append(response)
#         final_response = model_with_tools.invoke(messages)
#         return final_response.content
#     else:
#         return response.content

# # Main chat loop
# def main():
#     """Main function to run the chat agent."""
#     print(" YOUR ASSISTANT IS READYYYYYYYY! Type 'quit' to exit.")
#     print("Available tools: DBS, Weather, Math, Document Q&A")
#     print("-" * 50)
    
#     try:
#         model_with_tools = create_chat_agent()
        
#         while True:
#             user_input = input("\nYou: ")
            
#             if user_input.lower() in ['quit', 'exit', 'bye']:
#                 print("GOODBYEEEEEEEEEEEEEEE! ")
#                 break
            
#             try:
#                 response = run_agent(model_with_tools, user_input)
#                 print(f"\n: {response}")
#             except Exception as e:
#                 print(f" Error: {e}")
                
#     except Exception as e:
#         print(f" Failed to initialize agent: {e}")
#         print("Please check your configuration and dependencies.")

# if __name__ == "__main__":
#     main()