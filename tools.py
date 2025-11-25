
from langchain.tools import tool
from retrieval import VectorRetriever
from pydantic import BaseModel, Field
from typing import Literal


# Initialize retriever
try:
    retriever_instance = VectorRetriever()
except Exception as e:
    print(f"Error initializing retriever: {e}")
    retriever_instance = None

@tool
def search(query: str) -> str:
    """"Tool for searching relevant documents from the vector store."""
    try:
        print(f"SEARCH TOOL CALLED with query: '{query}'")
        if retriever_instance is None:
            return "Retriever not initialized. Cannot search."
        results = retriever_instance.retrieve(query)
        if not results:
            return "No relevant context found."
        return "\n\n".join([item["context"] for item in results])
    except Exception as e:
        print(f"Error in search tool: {e}")
        return f"Error occurred while searching: {str(e)}"

@tool
def get_user_info(query: str) -> str:
    """Get user information based on the query."""
    # Placeholder implementation - customize based on your needs
    return f"Processing user info request: {query}"

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

@tool
def simple_math(expression: str) -> str:
    """Perform a simple math calculation."""
    print(f" MATH TOOL CALLED with expression: '{expression}'")
    try:
        result = eval(expression, {"__builtins__": {}})
        return str(result)
    except Exception as e:
        return f"Error in calculation: {e}"