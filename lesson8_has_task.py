r"""
Lesson 8: Structured information retrieval with OpenAI + Pydantic BaseModel

Setup:

Always create a virtual environment
1. python -m venv venv
2. source venv/bin/activate # On Windows use `venv\Scripts\activate`
3. deactivate # To exit the virtual environment

Install the dependencies
1. pip3 install pydantic_ai
2. pip3 install dotenv

You can, however, install dependencies through pip freeze and a requirements.txt file:
1. pip3 freeze > requirements.txt
2. pip3 install -r requirements.txt
"""
import os
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel

load_dotenv()

if not os.getenv('OPENAI_API_KEY'):
    raise RuntimeError('OPENAI_API_KEY not set; check the .env file.')

class Restaurant(BaseModel):
    name: str
    cuisine: str
    rating: float

class RestaurantList(BaseModel):
    restaurants: list[Restaurant]

client = OpenAI()

response = client.responses.parse(
    model="gpt-5.2",
    input="What are 5 popular restaurants in Tampere, Finland, and what type of cuisine do they serve? Include a rating out of 5.",
    text_format=RestaurantList
)

restaurants = response.output_parsed

print("Restaurants:")
for restaurant in restaurants.restaurants:
    print(f"  {restaurant.name} — {restaurant.cuisine} (Rating: {restaurant.rating})")

# Problem : What if you need to change the Model?

# First task - Retrieve the top 5 rated restaurants in Tampere from Google Maps and then include the web search to search only in google.com.

# Second task:
# Implement in a similar fashion a script that displays the top 10 lunch spots in Tampere,
# including: restaurant name, cuisine type, average lunch price (EUR), Google rating, and address.
# Use Pydantic BaseModel to structure the output.
# Use OpenAI Responses API with web search tool call to get the most accurate information.
