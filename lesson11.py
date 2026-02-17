r"""
Lesson 11: Pydantic AI agent framework - Extracting structured information from an image, in an agentic way with watch folder
Not using database, just a CSV file, it is appending at the end of the file, every time a new image is processed.

Is this already an AI agent?

This is NOT an AI agent. An agent would have:
- Temporal continuity (a loop running over time)
- Tools/actuators (search, database, filesystem, etc.)
- State/memory across steps
- Goal-directed behavior

We will see that in the next lesson.

Setup:

Always create a virtual environment
1. python -m venv venv
2. source venv/bin/activate # On Windows use `venv\Scripts\activate`
3. deactivate # To exit the virtual environment

Install the dependencies
1. pip3 install pydantic_ai
2. pip3 install dotenv
3. pip3 install watchdog

You can, however, install dependencies through pip freeze and a requirements.txt file:
1. pip3 freeze > requirements.txt
2. pip3 install -r requirements.txt
"""

import csv
import time
from pathlib import Path
from datetime import datetime

from pydantic import BaseModel
from pydantic_ai import Agent, BinaryContent
from dotenv import load_dotenv
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent

load_dotenv()

# Configuration
WATCH_FOLDER = Path("images_watchfolder")
CSV_OUTPUT = Path("menus.csv")
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
            writer.writerow(['timestamp', 'source_image', 'restaurant_name', 'dish_name', 'price', 'category', 'dietary_tags'])
        print(f"Created {CSV_OUTPUT}")


def append_to_csv(source_image: str, extraction: MenuExtraction):
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
                ';'.join(item.dietary_tags) if item.dietary_tags else ''
            ])

    print(f"   Saved to {CSV_OUTPUT}")


def process_image(image_path: Path):
    """Process a single image and extract menu information"""
    if image_path.suffix.lower() not in IMAGE_EXTENSIONS:
        return

    print(f"\nProcessing: {image_path.name}")

    try:
        # Wait a moment to ensure file is fully written
        time.sleep(0.5)

        # Read image and send to agent
        image_data = image_path.read_bytes()
        media_type = get_media_type(image_path)

        result = agent.run_sync([
            "Extract all menu information from this image.",
            BinaryContent(data=image_data, media_type=media_type),
        ])

        # Print results
        print(f"   Restaurant: {result.output.restaurant_name}")
        for item in result.output.items:
            tags_str = f" [{', '.join(item.dietary_tags)}]" if item.dietary_tags else ""
            print(f"      {item.dish_name}: €{item.price:.2f} — {item.category}{tags_str}")

        # Save to CSV
        append_to_csv(image_path.name, result.output)

    except Exception as e:
        print(f"   Error processing {image_path.name}: {e}")


class ImageHandler(FileSystemEventHandler):
    """Handler for new image files in the watch folder"""

    def on_created(self, event: FileCreatedEvent):
        if event.is_directory:
            return

        image_path = Path(event.src_path)
        if image_path.suffix.lower() in IMAGE_EXTENSIONS:
            process_image(image_path)


def main():
    # Check that watch folder exists
    if not WATCH_FOLDER.exists():
        raise FileNotFoundError(f"Folder '{WATCH_FOLDER}' not found")

    print(f"Watching folder: {WATCH_FOLDER.absolute()}")

    # Initialize CSV
    initialize_csv()

    # Process any existing images in the folder first
    existing_images = [f for f in WATCH_FOLDER.iterdir()
                       if f.suffix.lower() in IMAGE_EXTENSIONS]
    if existing_images:
        print(f"\nProcessing {len(existing_images)} existing image(s)...")
        for image_path in existing_images:
            process_image(image_path)

    # Set up the watchdog observer
    event_handler = ImageHandler()
    observer = Observer()
    observer.schedule(event_handler, str(WATCH_FOLDER), recursive=False)
    observer.start()

    print(f"\nAgent is now watching for new images. Press Ctrl+C to stop.\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping watcher...")
        observer.stop()

    observer.join()
    print("Done!")


if __name__ == "__main__":
    main()

# Can I have two agents? A second one adding more information about the restaurants?
