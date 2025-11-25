import os
import uuid
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver  
from pydantic import BaseModel
from langchain.agents.structured_output import ToolStrategy
from tools import search, get_user_info, simple_math, get_weather, search_database

load_dotenv()

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
You are a professional voice-based travel planning assistant. Ask by default the following questions.
Ask one by one to collect user information for travel planning.

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

Once all details are collected, then respond with "collected" to indicate completion.
"""

    TOOLS = [search, get_user_info, simple_math, get_weather, search_database]
    
    def __init__(self, use_schema):
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

            print("Initializing Tools with agent without Structured Output...\n")
            self.agent = create_agent(
                model="gpt-4o-mini",
                tools=self.TOOLS,
                system_prompt=self.SYSTEM_PROMPT_WITH_STRUCTURED,
                checkpointer=InMemorySaver()
            )
        
            print("Tour Guide Agent Initialized Successfully!")
            print(f"Tools Enabled: {[t.name for t in self.TOOLS]}") 
            print(f"Schema Enabled: {self.use_schema}\n")
            
        except Exception as e:
            print(f"Error initializing agent: {e}")
            raise

    
    def structured_op(self, collected_info):
        """
        Generate structured travel details using the TourPlan schema
        by the LLM's structured output..
        """
        try:
            # Create the LLM wrapper that enforces TourPlan structured output
            llm_structured = self.model.with_structured_output(TourPlan)

            # Prepare the prompt for the structured model
            prompt = f"""
The following information has been collected from the user during conversation.
Please extract and format it into the TourPlan structured schema.

Collected Information:
{collected_info}

Return ONLY the structured schema output.
"""

            # LLM returns a validated TourPlan object
            structured_plan: TourPlan = llm_structured.invoke(prompt)

            # Return formatted JSON output
            return structured_plan.model_dump_json(indent=2)

        except Exception as e:
            return f"Error generating structured output: {e}"

    
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
            final_response = response["messages"][-1].content
            if "collected" in final_response.lower():
                response = self.structured_op(collected_info=final_response)
                return response
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


#   MAIN ENTRY POINT
if __name__ == "__main__":
    # Create and run the agent
    # Set use_schema=True for structured output, False for tool-based agent
    agent_app = GuideAgent(use_schema=True)
    agent_app.run()
