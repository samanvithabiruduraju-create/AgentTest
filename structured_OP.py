from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
import os



class Movie(BaseModel):
    """A movie with details."""
    title: str = Field(..., description="The title of the movie")
    year: int = Field(..., description="The year the movie was released")
    director: str = Field(..., description="The director of the movie")
    rating: float = Field(..., description="The movie's rating out of 10")

model = ChatOpenAI(model="gpt-4o-mini", temperature=0.2, max_tokens=512, timeout=30)

try:
    model_with_structure = model.with_structured_output(schema=Movie, include_raw=True)
    response = model_with_structure.invoke("Provide details about the movie intestellar")
    
    print(" Structured Output Working!")
    print("Structured Output:")
    print(response)
    print("\nRaw JSON:")
    print(response["raw"].content)
    
    # Access the parsed movie object
    movie = response["parsed"]
    print(f"\n Movie Details:")
    print(f"Title: {movie.title}")
    print(f"Year: {movie.year}")
    print(f"Director: {movie.director}")
    print(f"Rating: {movie.rating}/10")
    
except Exception as e:
    print(f" Error: {e}")
    print("Structured output is NOT working properly")