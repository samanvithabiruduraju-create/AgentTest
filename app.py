import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from pydantic import BaseModel
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver  
from tools import search, get_user_info
from langchain.agents.structured_output import ToolStrategy
load_dotenv()

class ContactInfo(BaseModel):
    name: str
    email: str
    phone: str


system_prompt = """"
You are an AI assistant that helps employees by answering questions based on the company's internal documents. Based on the query route to the `search_tool`. Use the provided context to give accurate and concise answers.

Follow below examples to understand the expected format and detail level in your responses:
Example 1:
User: "What is onboarding procedure?"
Answer:
"Onboarding includes orientation, document verification, and initial training during the first week."

Example 2:
User: "How many casual leaves are allowed?"
Answer:
"There are 12 casual leaves allowed per year for each employee as per the company policy that can be availed after completing 6 months of service .the leaves should be applied in advance and are subject to approval by the respective manager to ensure smooth workflow within the team and department operations."

Example 3:
User: "Does the company have work-from-home policy?"
Answer: (Single word response)
"NO, the company doesnot have a work-from-home policy as all employees are required to work from the office premises except in case of emergencies or special permissions granted by management as per the company guidelines.they are expected to be present during working hours to ensure collaboration and productivity such that the work culture is maintained effectively. """

try:
    model = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        max_tokens=1000,
        timeout=30
    )
    agent = create_agent(
        model=model, 
        tools=[search, get_user_info],
        system_prompt=system_prompt,
        checkpointer=InMemorySaver()
    )
    # response_format=ToolStrategy(ContactInfo)
    print(" System prompt configured successfully!")
    print(f"Prompt type: Few-shot learning with examples\n")
except Exception as e:
    print(f"Error initializing model or agent: {e}")
    exit() 

if __name__ == "__main__":
    print("Welcome to the Chat Agent with Document Retrieval!")
    print("Type 'exit' or 'quit' to stop\n")

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() in ['exit', 'quit', 'q']:
            print("Goodbye!")
            break

        if not user_input:
            print("Please enter a valid question.\n")
            continue

        try:
            print(f"\nAgent is processing your query: {user_input}\n")
            response = agent.invoke({
                "messages": [{"role": "user", "content": user_input}]
            }, {"configurable": {"thread_id": "gxhjsgdjdhd"}})
            print(f"\n\nAgent: {response['messages'][-1].content}\n")
        except Exception as e:
            print(f"Error processing query: {e}\n")
