r"""
Lesson 14 MCP: Interactive CSV Query Agent using MCP

This version uses MCP (Model Context Protocol) to query the CSV file.
Instead of loading the entire CSV into the prompt (high input tokens),
the agent connects to an MCP server that provides tools to query the data.

The LLM only calls the tools it needs, significantly reducing input tokens.


Setup:

Install the dependencies
1. pip3 install "pydantic-ai-slim[mcp]"
2. pip3 install mcp
3. pip3 install dotenv

Run: python lesson14_mcp_has_task.py
"""

import asyncio
from pathlib import Path

from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio
from dotenv import load_dotenv

load_dotenv()

# MCP server that provides CSV query tools
csv_server = MCPServerStdio(
    'python',
    args=['lesson14_mcp_server.py'],
    timeout=30
)

# Create the query agent with MCP toolset
query_agent = Agent(
    'openai:gpt-5.2',
    toolsets=[csv_server],
    instructions="""
    You are a helpful assistant that answers questions about restaurant and menu data in Tampere, Finland.

    You have access to tools that can query a CSV database containing information
    about restaurants, their menu items, prices, categories, dietary tags, cuisine types,
    Google ratings, and addresses.

    Available tools:
    - get_total_records: Get total count of records
    - list_all_restaurants: List all unique restaurant names
    - list_all_categories: List menu item categories with counts
    - list_all_cuisine_types: List cuisine types with counts
    - get_dishes_by_category: Get dishes matching a category
    - get_restaurants_by_cuisine: Get restaurants by cuisine type
    - get_restaurant_details: Get full details for a restaurant
    - get_cheapest_dish: Find the cheapest dish (optionally by category)
    - get_average_price: Get average price (optionally by category)
    - search_menu_items: Search all fields for a term

    Rules:
    - Use the appropriate tool to answer questions
    - Be precise and use tool results accurately
    - If no matching data is found, say so clearly
    - Prices are in EUR
    - Be concise but helpful
    """,
)


async def main():
    print("MCP Query Agent - Token-Efficient CSV Queries")
    print("Using MCP server for on-demand data retrieval")
    print("Ask questions about the restaurant and menu data. Type 'q' to exit.\n")

    # Use async context manager to manage MCP server connection
    async with query_agent:
        while True:
            try:
                # Get user input
                question = input("You: ").strip()

                # Check for exit
                if question.lower() == 'q':
                    print("Goodbye!")
                    break

                # Skip empty input
                if not question:
                    continue

                # Run the agent with the question
                result = await query_agent.run(question)

                print(f"\nAgent: {result.output}")
                print(f"[Tokens: {result.usage().input_tokens} in / {result.usage().output_tokens} out]\n")

            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"\nError: {e}\n")


if __name__ == "__main__":
    asyncio.run(main())

# Ask @lesson14_mcp_server.py for "give me all the data", and ask @lesson13.py for the same question to see the difference in token usage.
# Can you explain why MCP is less token-efficient in this case?

# Your Capstone Project:

# Change the lesson12-async.py to ingest the data to a database of your choice (PostgreSQL, Neo4j, or SQLite).
# Create a web application (FastAPI) in which users can
# - upload images of restaurant menus
# - have the data extracted and enriched
# - store the data in the database
# - query the database via a web interface using natural language (LLM-powered)
# - view performance metrics (tokens, cost, latency)
# Deploy the web application to a cloud platform (vercel, render, railway, etc.)
