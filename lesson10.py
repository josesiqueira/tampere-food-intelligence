r"""
Lesson 10: Pydantic AI agent framework - Extracting structured information from an image

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

from pathlib import Path
from pydantic import BaseModel
from pydantic_ai import Agent, BinaryContent
from dotenv import load_dotenv

load_dotenv()


class MenuItem(BaseModel):
    dish_name: str
    price: float
    currency: str = "EUR"
    category: str
    dietary_tags: list[str] = []
    portion_size: str | None = None
    is_daily_special: bool = False


class MenuExtraction(BaseModel):
    restaurant_name: str
    items: list[MenuItem]


def get_media_type(filepath: Path) -> str:
    """Get the MIME type based on file extension"""
    suffix = filepath.suffix.lower()
    media_types = {
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.gif': 'image/gif',
        '.webp': 'image/webp',
    }
    return media_types.get(suffix, 'image/jpeg')


folder = Path("images")

if not folder.exists():
    raise FileNotFoundError(f"Folder '{folder}' not found")

# Collect all results
all_items: dict[str, list[MenuItem]] = {}
"""
Process all images in the folder and return a dict where:
- key = restaurant name
- value = list of MenuItem objects (dish_name, price, category, dietary_tags, etc.)
"""

# Supported image extensions
image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.webp'}

for image_path in folder.iterdir():
    if image_path.suffix.lower() not in image_extensions:
        continue

    print(f"Processing: {image_path.name}")

    # Read image and send to agent
    image_data = image_path.read_bytes()
    media_type = get_media_type(image_path)

    agent = Agent(
    'openai:gpt-5.2',
    output_type=MenuExtraction,
    instructions="""
    Extract menu information from the image.
    For each item visible on the menu, extract:
    - The dish or drink name
    - The price (as a number, in EUR unless stated otherwise)
    - The currency (default EUR)
    - The category (e.g., "Lunch", "Hot Drinks", "Dessert", "Appetizer", "Main Course", "Beverage")
    - Any dietary tags visible (e.g., "V" for vegan, "VE" for vegetarian, "GF" for gluten-free, "L" for lactose-free)
    - Portion size if visible (e.g., "16cl", "0.5L")
    - Whether it's a daily/weekly special
    Also extract the restaurant or café name if visible.
    If any information is unclear or missing, use reasonable defaults.
    If the restaurant name is not visible, use "Unknown Restaurant".
    """,
)

    result = agent.run_sync([
        "Extract all menu information from this image.",
        BinaryContent(data=image_data, media_type=media_type),
    ])

    # Merge results into our dictionary
    restaurant_name = result.output.restaurant_name
    if restaurant_name not in all_items:
        all_items[restaurant_name] = []
    all_items[restaurant_name].extend(result.output.items)

# Pretty print results
for restaurant, items in all_items.items():
    print(f"\nRestaurant: {restaurant}")
    for item in items:
        tags_str = f" [{', '.join(item.dietary_tags)}]" if item.dietary_tags else ""
        size_str = f" ({item.portion_size})" if item.portion_size else ""
        special_str = " *DAILY SPECIAL*" if item.is_daily_special else ""
        print(f"   {item.dish_name}: €{item.price:.2f} — {item.category}{tags_str}{size_str}{special_str}")
