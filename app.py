from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
# from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import asyncio
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv(".env")

# llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
# response = llm.invoke("Hello, Gemini!")
# print(response.content)


model = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    google_api_key=str(os.environ.get("GEMIN_KEY")),
    # convert_system_message_to_human=True,
)


# model = ChatOpenAI(
#     model="gpt-4o-mini", temperature=0, openai_api_key=os.getenv("OPENAI_API_KEY")
# )

server_params = StdioServerParameters(
    command="npx",
    env={
        "FIRECRAWL_API_KEY": os.getenv("FIRECRAWL_KEY"),
    },
    args=["firecrawl-mcp"],
)


async def main():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await load_mcp_tools(session)
            agent = create_react_agent(model, tools)

            # system_prompt = "You are a helpful assistant that can scrape websites, crawl pages, and extract data using Firecrawl tools. Think step by step and use the appropriate tools to help the user."

            messages = [
                {
                    "role": "system",
                    "content": "You are a helpful assistant that can scrape websites, crawl pages, and extract data using Firecrawl tools. Think step by step and use the appropriate tools to help the user.",
                }
            ]

            print("Available Tools -", *[tool.name for tool in tools])
            print("-" * 60)

            while True:
                user_input = input("\nYou: ")
                if user_input == "quit":
                    print("Goodbye")
                    break

                messages.append({"role": "user", "content": user_input[:175000]})

                try:
                    agent_response = await agent.ainvoke({"messages": messages})

                    ai_message = agent_response["messages"][-1].content
                    print("\nAgent:", ai_message)
                except Exception as e:
                    print("Error:", e)


if __name__ == "__main__":
    asyncio.run(main())
