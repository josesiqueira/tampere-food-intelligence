r"""
Lesson 7: Structured information retrieval with OpenAI

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
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

if not os.getenv('OPENAI_API_KEY'):
    raise RuntimeError('OPENAI_API_KEY not set; check the .env file.')

client = OpenAI()

response = client.responses.create(
    model="gpt-5.2",
    input="What are 5 popular restaurants in Tampere, Finland, and what type of cuisine do they serve?",
    text={
        "format": {
            "type": "json_schema",
            "name": "restaurant_list",
            "schema": {
                "type": "object",
                "properties": {
                    "restaurants": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "cuisine": {"type": "string"},
                                "rating": {"type": "number"}
                            },
                            "required": ["name", "cuisine", "rating"],
                            "additionalProperties": False
                        }
                    }
                },
                "required": ["restaurants"],
                "additionalProperties": False
            }
        }
    }
)

print("printing response:")
print(response)

print("parsed output:")
parsed = json.loads(response.output_text)
print(parsed)

print("Restaurants:")
for restaurant in parsed["restaurants"]:
    print(f"  {restaurant['name']} — {restaurant['cuisine']} (Rating: {restaurant['rating']})")

print("\nUsage:", response.usage)

# First problem, difficult to maintain the JSON schema.

# Now let's make the JSON more maintanable by using pydantic BaseModel

# Second problem: Everytime you run this, the output may vary. What can you do?
