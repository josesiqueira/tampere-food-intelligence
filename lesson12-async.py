r"""
Lesson 12: Pydantic AI agent framework - Extracting structured information from an image, in an agentic way with watch folder.
This time with 2 agents.
The first agent is doing the extraction of the structured information from the image.
The second agent is doing a web search for the restaurant details (rating, address, cuisine type).

# async version.

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

import asyncio
import csv
from pathlib import Path
from datetime import datetime

from pydantic import BaseModel
from pydantic_ai import Agent, BinaryContent, WebSearchTool
from dotenv import load_dotenv
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent

load_dotenv()

# Configuration
WATCH_FOLDER = Path("images_watchfolder")
CSV_OUTPUT = Path("menus-async.csv")
IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.webp'}


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


class RestaurantEnrichment(BaseModel):
    """Enriched information about a restaurant from web search"""
    google_rating: float | None = None
    address: str
    cuisine_type: str


class EnrichedMenuExtraction(BaseModel):
    """Menu extraction with enriched restaurant information"""
    restaurant_name: str
    cuisine_type: str
    google_rating: float | None = None
    address: str
    items: list[MenuItem]


# Agent 1: Extract menu info from images
extraction_agent = Agent(
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

# Agent 2: Enrich restaurant info with Google rating, address, and cuisine type via web search
enrichment_agent = Agent(
    'openai-responses:gpt-5.2',
    output_type=RestaurantEnrichment,
    builtin_tools=[WebSearchTool()],
    instructions="""
    You are given a restaurant name in Tampere, Finland. Use web search to find information about the restaurant.
    Find:
    - The Google Maps rating (e.g., 4.5 out of 5)
    - The full street address in Tampere
    - The cuisine type (e.g., "Finnish", "Italian", "Asian Fusion", "Specialty Coffee", "Fast Food")
    If you cannot find the information, use "Unknown" for text fields and None for the rating.
    """,
)


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


def initialize_csv():
    """Create the CSV file with headers if it doesn't exist"""
    if not CSV_OUTPUT.exists():
        with open(CSV_OUTPUT, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['timestamp', 'source_image', 'restaurant_name', 'dish_name', 'price', 'category', 'dietary_tags', 'cuisine_type', 'google_rating', 'address'])
        print(f"Created {CSV_OUTPUT}")


def append_to_csv(source_image: str, extraction: EnrichedMenuExtraction):
    """Append extracted menu data to the CSV file"""
    timestamp = datetime.now().isoformat()

    with open(CSV_OUTPUT, 'a', newline='') as f:
        writer = csv.writer(f)
        for item in extraction.items:
            writer.writerow([
                timestamp,
                source_image,
                extraction.restaurant_name,
                item.dish_name,
                item.price,
                item.category,
                ';'.join(item.dietary_tags) if item.dietary_tags else '',
                extraction.cuisine_type,
                extraction.google_rating or '',
                extraction.address
            ])

    print(f"   Saved to {CSV_OUTPUT}")


async def enrich_restaurant(restaurant_name: str) -> RestaurantEnrichment:
    """Enrich a restaurant with rating, address, and cuisine info (runs async)"""
    print(f"   Agent 2: Searching web for '{restaurant_name}' info...")

    # Use the enrichment agent to get restaurant details
    enrichment_result = await enrichment_agent.run(
        f"Find the Google rating, address, and cuisine type for the restaurant: {restaurant_name} in Tampere, Finland"
    )

    # Print results
    print(f"   Restaurant: {restaurant_name}")
    print(f"      Rating: {enrichment_result.output.google_rating}")
    print(f"      Address: {enrichment_result.output.address}")
    print(f"      Cuisine: {enrichment_result.output.cuisine_type}")

    return enrichment_result.output


async def process_image(image_path: Path):
    """Process a single image and extract menu information"""
    if image_path.suffix.lower() not in IMAGE_EXTENSIONS:
        return

    print(f"\nProcessing: {image_path.name}")

    try:
        # Wait a moment to ensure file is fully written
        await asyncio.sleep(0.5)

        # Read image and send to extraction agent
        image_data = image_path.read_bytes()
        media_type = get_media_type(image_path)

        print("   Agent 1: Extracting menu info from image...")
        extraction_result = await extraction_agent.run([
            "Extract all menu information from this image.",
            BinaryContent(data=image_data, media_type=media_type),
        ])

        restaurant_name = extraction_result.output.restaurant_name

        # Deduplicate items by dish name (keep first occurrence)
        unique_items: dict[str, MenuItem] = {}
        for item in extraction_result.output.items:
            item_key = item.dish_name.strip().lower()
            if item_key not in unique_items:
                unique_items[item_key] = item

        deduplicated_items = list(unique_items.values())

        # Enrich the restaurant in parallel (single restaurant per image, but async)
        print(f"   Agent 2: Enriching restaurant '{restaurant_name}' in parallel...")
        enrichment = await enrich_restaurant(restaurant_name)

        # Create enriched extraction result
        enriched_extraction = EnrichedMenuExtraction(
            restaurant_name=restaurant_name,
            cuisine_type=enrichment.cuisine_type,
            google_rating=enrichment.google_rating,
            address=enrichment.address,
            items=deduplicated_items
        )

        # Print enriched results
        for item in enriched_extraction.items:
            tags_str = f" [{', '.join(item.dietary_tags)}]" if item.dietary_tags else ""
            print(f"      {item.dish_name}: €{item.price:.2f} — {item.category}{tags_str}")

        # Save to CSV
        append_to_csv(image_path.name, enriched_extraction)

    except Exception as e:
        print(f"   Error processing {image_path.name}: {e}")


class ImageHandler(FileSystemEventHandler):
    """Handler for new image files in the watch folder"""

    def on_created(self, event: FileCreatedEvent):
        if event.is_directory:
            return

        image_path = Path(event.src_path)
        if image_path.suffix.lower() in IMAGE_EXTENSIONS:
            asyncio.run(process_image(image_path))


async def main():
    # Check that watch folder exists
    if not WATCH_FOLDER.exists():
        raise FileNotFoundError(f"Folder '{WATCH_FOLDER}' not found")

    print(f"Watching folder: {WATCH_FOLDER.absolute()}")

    # Initialize CSV
    initialize_csv()

    # Process any existing images in the folder first (in parallel)
    existing_images = [f for f in WATCH_FOLDER.iterdir()
                       if f.suffix.lower() in IMAGE_EXTENSIONS]
    if existing_images:
        print(f"\nProcessing {len(existing_images)} existing image(s) in parallel...")
        await asyncio.gather(*[process_image(image_path) for image_path in existing_images])

    # Set up the watchdog observer
    event_handler = ImageHandler()
    observer = Observer()
    observer.schedule(event_handler, str(WATCH_FOLDER), recursive=False)
    observer.start()

    print(f"\nAgent is now watching for new images. Press Ctrl+C to stop.\n")

    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping watcher...")
        observer.stop()

    observer.join()
    print("Done!")


if __name__ == "__main__":
    asyncio.run(main())
