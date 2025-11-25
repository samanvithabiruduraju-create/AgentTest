import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver  
from tools import search

load_dotenv()


model = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0
)


TOOLS = [search]


agent = create_agent(
    model="gpt-4o-mini",
    tools=TOOLS,
    system_prompt="You are a simple helpful assistant. Use tools when needed.",
    checkpointer=InMemorySaver()
)

print("Simple Agent Initialized!\n")


if __name__ == "__main__":
    print("Type 'exit' to quit.\n")

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break

        try:
            response = agent.invoke(
                {"messages": [{"role": "user", "content": user_input}]},
                {"configurable": {"thread_id": "abcd123"}}
            )

            print("Agent:", response["messages"][-1].content, "\n")

        except Exception as e:
            print("Error:", e)
            print()
