# import os
# from dotenv import load_dotenv
# from langchain_openai import ChatOpenAI
# from pydantic import BaseModel
# from langchain.agents import create_agent
# from langgraph.checkpoint.memory import InMemorySaver  
# from tools import search, get_user_info
# from langchain.agents.structured_output import ToolStrategy

# load_dotenv()

# AVAILABLE_MODELS = {
#     "model": "gpt-4o-mini",
#     "temprature": 0,
    
# }




# PROMPT_TEMPLATES = {
#     "policy_assistant": f"""
# You are an AI assistant that collects information.
# Ask one question at a time to gather the following details:
# Collect info:
# - Name: {{name}}

# - Age: {{age}}

# - Email: {{email}}

# - Phone: {{phone}}

# Use the `search` tool to fetch exact policy information. Keep answers accurate and concise.
# """,

#     "strict_policy_format": f"""
# You are a strict HR assistant.

# Policy Context: {{context}}

# Every answer must follow this exact format:
# - Summary (2 lines)
# - Policy Reference
# - Action Steps for Employee

# Always call the search tool if information is needed.
# """,

#     "simple_chat": f"""
# You are a friendly HR chatbot interacting with {{employee_name}}.

# Keep responses short and helpful.
# """,
# }


# SYSTEM_PROMPT = PROMPT_TEMPLATES["policy_assistant"].format(
#     name="what is your name?", age="Can I know your age?", email="Share email ID", phone="Can I get mobile number?"
# )

# print("SYSTEM PROMPT CONFIGURED:\n", SYSTEM_PROMPT)



# class PolicyAnswer(BaseModel):
#     summary: str
#     reference: str
#     steps: list[str]

# USE_SCHEMA = False 


# AVAILABLE_TOOLS = {
#     "default": [search],
#     "with_user_info": [search, get_user_info],
#     "no_tools": []
# }

# SELECTED_TOOLS = AVAILABLE_TOOLS["with_user_info"]   


# try:
#     model = ChatOpenAI(
#         model= "gpt-4o-mini",
#         temperature=0,
#         max_tokens=600
#     )

#     if USE_SCHEMA:
#         agent = create_agent(
#             model="gpt-4o-mini",
#             tools=SELECTED_TOOLS,
#             system_prompt=SYSTEM_PROMPT,
#             response_format=ToolStrategy(PolicyAnswer),
#             checkpointer=InMemorySaver()
#         )
#     else:
#         agent = create_agent(
#             tools=SELECTED_TOOLS,   
#             model= "gpt-4o-mini",
#             system_prompt=SYSTEM_PROMPT,
#             checkpointer=InMemorySaver()
#         )

#     print("\n Agent successfully initialized!")
#     print(f"Model: {"gpt-4o-mini"}")
#     print(f"Prompt Template: {SYSTEM_PROMPT[:60]}...")
#     print(f"Tools Enabled: {[t.name for t in SELECTED_TOOLS]}")
#     print(f"Schema Enabled: {USE_SCHEMA}\n")

# except Exception as e:
#     print(f" Error initializing agent: {e}")
#     exit()


# if __name__ == "__main__":
#     print("Welcome to Myyyyyyyyyyyyyyyyy Playground Agent!\n")
#     print("Type 'exit' to quit.\n")

#     while True:
#         user_input = input("You: ").strip()

#         if user_input.lower() in ['exit', 'quit']:
#             print("Goodboiiiiiiiiiiiiiii!")
#             break

#         if not user_input:
#             print("Please enter a question.\n")
#             continue

#         try:
#             print("\n Agent thinking...\n")

#             response = agent.invoke(
#                 {"messages": [{"role": "user", "content": user_input}]},
#                 {"configurable": {"thread_id": "samseervvvvvvvtyssiooonnnnnnnnnnnn"}}
#             )

#             print("Agent:", response["messages"][-1].content, "\n")

#         except Exception as e:
#             print(f" Error: {e}\n")
