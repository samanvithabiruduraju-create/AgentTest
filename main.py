import os
import uuid
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver  
from pydantic import BaseModel
from langchain.agents.structured_output import ToolStrategy
from tools import search, get_user_info, simple_math, get_weather, search_database
from fastapi import FastAPI, HTTPException
from typing import Optional

load_dotenv()

# FastAPI app
app = FastAPI(title="Tour Guide Agent API")

# Store active agent sessions
sessions = {}


#   SCHEMA
class TourPlan(BaseModel):
    name: str
    country: str
    passport_id: str
    phone: str
    email: str
    destination: str


class GuideAgent:
    """A class-based Tour Guide Agent with automatic thread ID generation."""
    
    SYSTEM_PROMPT_WITHOUT_STRUCTURED = """
You are a helpful, intelligent, and professional assistant.
Your goal is to guide the user through a conversation, ask clarifying questions when needed, and provide accurate, concise, and helpful responses.

Maintain a natural, friendly, and supportive tone throughout the conversation.
If the user’s request is unclear, ask a clarifying question rather than making assumptions.
If information provided by the user is incomplete, prompt them gently to fill in missing details.

TOOL USAGE RULES:
- call ``search`` tool to find information about company polcies.
- call ``get_user_info`` tool to retrieve user details.
- call ``simple_math`` tool to perform basic calculations.
- call ``get_weather`` tool to provide weather updates.
- call ``search_database`` tool to query the internal database.

CONVERSATION FLOW:
- When a tool is needed, call it directly and do not add unnecessary commentary.
- When no tool is needed, respond with a clear, helpful answer in natural language.
- If the user changes the topic or direction, adapt smoothly and continue assisting without breaking conversational flow.

Your overall objective is to provide reliable assistance, decide intelligently between tool calls and normal responses, and make the interaction feel seamless and natural at all times.
"""

    SYSTEM_PROMPT_WITH_STRUCTURED = """
You are a professional voice-based travel planning assistant. You start asking and engaging user after greetings.
Your role is to interact with the user, ask questions one at a time, and collect all the necessary details required to plan their tour.

Your primary objective is to gather the following information clearly and accurately:

1. Name: what is your name?
2. Country of Residence: Which country are you from?
3. Passport ID: Can you share your passport ID?
4. Phone Number: Camn I know your contact number?
5. Email Address: What is your email ID?
6. Preferred Travel Destination: Where would you like to travel?

Guidelines:
1. Speak politely and professionally.
2. Ask only one question at a time to avoid overwhelming the user.
3. Confirm details if they seem unclear or incomplete.
4. Do not proceed to the next question until the current detail has been fully provided.
5. If the user asks a question unrelated to collecting details, respond briefly and guide them back to the information collection process.

Once all details are collected, summarize the information in a clean format and ask for final confirmation.
"""

    TOOLS = [search, get_user_info, simple_math, get_weather, search_database]
    
    def __init__(self, use_schema=True):
        """
        Initialize the Tour Guide Agent.
        
        Args:
            use_schema (bool): Whether to use structured output with TourPlan schema
        """
        self.use_schema = use_schema
        self.thread_id = self._generate_thread_id()
        self.agent = None
        self.model = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
            max_tokens=600
        )
        
        print(f"SYSTEM PROMPT: {self.SYSTEM_PROMPT_WITH_STRUCTURED if use_schema else self.SYSTEM_PROMPT_WITHOUT_STRUCTURED}")
        print(f"Thread ID: {self.thread_id}\n")
        
        self._initialize_agent()
    
    def _generate_thread_id(self):
        """Generate a unique thread ID for the session."""
        return f"tour-guide-{uuid.uuid4().hex[:16]}"
    
    def _initialize_agent(self):
        """Initialize the agent with appropriate configuration."""
        try:
            if self.use_schema:
                print("Initializing Tour Guide Agent with Structured Output...\n")
                self.agent = create_agent(
                    model="gpt-4o-mini",
                    system_prompt=self.SYSTEM_PROMPT_WITH_STRUCTURED,
                    response_format=ToolStrategy(TourPlan),
                    checkpointer=InMemorySaver()
                )
            else:
                print("Initializing Tools with agent without Structured Output...\n")
                self.agent = create_agent(
                    model="gpt-4o-mini",
                    tools=self.TOOLS,
                    system_prompt=self.SYSTEM_PROMPT_WITHOUT_STRUCTURED,
                    checkpointer=InMemorySaver()
                )
            
            print("Tour Guide Agent Initialized Successfully!")
            print(f"Tools Enabled: {[t.name for t in self.TOOLS]}")
            print(f"Schema Enabled: {self.use_schema}\n")
            
        except Exception as e:
            print(f"Error initializing agent: {e}")
            raise
    
    def get_response(self, user_input):
        """
        Invoke the agent with user input.
        
        Args:
            user_input (str): The user's message
            
        Returns:
            str: The agent's response
        """
        try:
            response = self.agent.invoke(
                {"messages": [{"role": "user", "content": user_input}]},
                {"configurable": {"thread_id": self.thread_id}}
            )
            return response["messages"][-1].content
        except Exception as e:
            raise Exception(f"Error during agent invocation: {e}")
    
    def run(self):
        """Run the interactive chat loop."""
        print("Welcome to the SAM Tour Guide!")
        print("Ask me about any destination!")
        print("Type 'exit' to quit.\n")
        
        while True:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ["exit", "quit"]:
                print("Safe travels! Goodbye!")
                break
            
            if not user_input:
                print("Please enter a question.\n")
                continue
            
            try:
                print("\nThinking like a Travel Expert...\n")
                response = self.get_response(user_input)
                print(f"Agent: {response}\n")
                
            except Exception as e:
                print(f"Error: {e}\n")


# FastAPI Request/Response Models
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    use_schema: bool = False


class ChatResponse(BaseModel):
    response: str
    session_id: str
    thread_id: str


class SessionResponse(BaseModel):
    session_id: str
    thread_id: str
    use_schema: bool


# FastAPI Endpoints
@app.get("/")
def read_root():
    """Welcome endpoint"""
    return {
        "message": "Welcome to SAM Tour Guide API",
        "endpoints": {
            "/chat": "POST - Send a message to the agent",
            "/session/new": "POST - Create a new session",
            "/session/{session_id}": "GET - Get session info",
            "/sessions": "GET - List all active sessions",
            "/docs": "GET - Interactive API documentation"
        }
    }


@app.post("/session/new", response_model=SessionResponse)
def create_session(use_schema: bool = True):
    """Create a new agent session with a unique thread ID"""
    session_id = str(uuid.uuid4())
    agent = GuideAgent(use_schema=use_schema)
    sessions[session_id] = agent
    
    return {
        "session_id": session_id,
        "thread_id": agent.thread_id,
        "use_schema": use_schema
    }


@app.get("/session/{session_id}", response_model=SessionResponse)
def get_session(session_id: str):
    """Get information about a specific session"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    agent = sessions[session_id]
    return {
        "session_id": session_id,
        "thread_id": agent.thread_id,
        "use_schema": agent.use_schema
    }


@app.get("/sessions")
def list_sessions():
    """List all active sessions"""
    return {
        "active_sessions": len(sessions),
        "sessions": [
            {
                "session_id": "sam",
                "thread_id": agent.thread_id,
                "use_schema": agent.use_schema
            }
            for s, agent in sessions.items()
        ]
    }


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """
    Send a message to the agent.
    If session_id is not provided, a new session will be created.
    """
    session_id = request.session_id
    
    # Create new session if not provided
    if not session_id or session_id not in sessions:
        session_id = str(uuid.uuid4())
        agent = GuideAgent(use_schema=request.use_schema)
        sessions[session_id] = agent
    else:
        agent = sessions[session_id]
    
    try:
        # Get response from agent
        response = agent.get_response(request.message)
        
        return {
            "response": response,
            "session_id": session_id,
            "thread_id": agent.thread_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.delete("/session/{session_id}")
def delete_session(session_id: str):
    """Delete a specific session"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    del sessions[session_id]
    return {"message": f"Session {session_id} deleted successfully"}


#   MAIN ENTRY POINT
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)