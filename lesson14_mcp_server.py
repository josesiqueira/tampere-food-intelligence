r"""
Lesson 14 MCP Server: CSV Query Tools

This MCP server exposes tools for querying the menus-async.csv file.
Instead of passing all CSV data to the LLM, the LLM calls these tools
to retrieve only the specific data it needs, saving input tokens.

Run directly: python lesson14_mcp_server.py (for testing)
Used by: lesson14_mcp_has_task.py via MCPServerStdio
"""

import csv
from pathlib import Path
from collections import Counter
from mcp.server.fastmcp import FastMCP

# Create the MCP server
mcp = FastMCP('CSV Query Server')

CSV_FILE = Path("menus-async.csv")


def _load_rows() -> list[dict]:
    """Load CSV rows as list of dicts"""
    if not CSV_FILE.exists():
        return []
    with open(CSV_FILE, 'r', newline='') as f:
        return list(csv.DictReader(f))


@mcp.tool()
def get_total_records() -> str:
    """Get the total number of records in the CSV database"""
    rows = _load_rows()
    return f"Total records: {len(rows)}"


@mcp.tool()
def list_all_restaurants() -> str:
    """List all unique restaurant names in the database"""
    rows = _load_rows()
    restaurants = sorted(set(row.get('restaurant_name', '') for row in rows if row.get('restaurant_name')))
    return f"Restaurants ({len(restaurants)}): {', '.join(restaurants)}"


@mcp.tool()
def list_all_categories() -> str:
    """List all unique menu item categories in the database with counts"""
    rows = _load_rows()
    categories = Counter(row.get('category', 'Unknown') for row in rows if row.get('category'))
    result = [f"{category}: {count}" for category, count in categories.most_common()]
    return f"Categories:\n" + "\n".join(result)


@mcp.tool()
def list_all_cuisine_types() -> str:
    """List all unique cuisine types in the database with counts"""
    rows = _load_rows()
    cuisines = Counter(row.get('cuisine_type', 'Unknown') for row in rows if row.get('cuisine_type'))
    result = [f"{cuisine}: {count}" for cuisine, count in cuisines.most_common()]
    return f"Cuisine types:\n" + "\n".join(result)


@mcp.tool()
def get_dishes_by_category(category: str) -> str:
    """Get all dishes of a specific category (case-insensitive partial match)"""
    rows = _load_rows()
    category_lower = category.lower()
    matches = [row for row in rows if category_lower in row.get('category', '').lower()]
    if not matches:
        return f"No dishes found with category matching '{category}'"
    results = []
    for row in matches:
        results.append(f"- {row.get('dish_name')} (€{row.get('price')}) at {row.get('restaurant_name')}")
    return f"Dishes in category '{category}' ({len(matches)}):\n" + "\n".join(results)


@mcp.tool()
def get_restaurants_by_cuisine(cuisine: str) -> str:
    """Get all restaurants of a specific cuisine type (case-insensitive partial match)"""
    rows = _load_rows()
    cuisine_lower = cuisine.lower()
    matches = [row for row in rows if cuisine_lower in row.get('cuisine_type', '').lower()]
    if not matches:
        return f"No restaurants found with cuisine matching '{cuisine}'"
    restaurants = sorted(set(row.get('restaurant_name', '') for row in matches))
    return f"Restaurants with cuisine '{cuisine}' ({len(restaurants)}): {', '.join(restaurants)}"


@mcp.tool()
def get_restaurant_details(restaurant_name: str) -> str:
    """Get all details for a specific restaurant (case-insensitive partial match)"""
    rows = _load_rows()
    name_lower = restaurant_name.lower()
    matches = [row for row in rows if name_lower in row.get('restaurant_name', '').lower()]
    if not matches:
        return f"No restaurant found matching '{restaurant_name}'"
    results = []
    # Get restaurant-level info from first match
    first = matches[0]
    results.append(f"Restaurant: {first.get('restaurant_name')}")
    results.append(f"Cuisine: {first.get('cuisine_type')}")
    results.append(f"Rating: {first.get('google_rating')}")
    results.append(f"Address: {first.get('address')}")
    results.append(f"Menu items ({len(matches)}):")
    for row in matches:
        tags = f" [{row.get('dietary_tags')}]" if row.get('dietary_tags') else ""
        results.append(f"  - {row.get('dish_name')}: €{row.get('price')} ({row.get('category')}){tags}")
    return "\n".join(results)


@mcp.tool()
def get_cheapest_dish(category: str = "") -> str:
    """Get the cheapest dish(es). Optionally filter by category (case-insensitive partial match)."""
    rows = _load_rows()
    if category:
        category_lower = category.lower()
        rows = [row for row in rows if category_lower in row.get('category', '').lower()]
    if not rows:
        return f"No dishes found" + (f" in category '{category}'" if category else "")
    # Parse prices and find minimum
    priced = []
    for row in rows:
        try:
            price = float(row.get('price', 0))
            priced.append((price, row))
        except ValueError:
            continue
    if not priced:
        return "No valid prices found"
    priced.sort(key=lambda x: x[0])
    cheapest_price = priced[0][0]
    cheapest = [(p, r) for p, r in priced if p == cheapest_price]
    results = [f"Cheapest dish(es) (€{cheapest_price:.2f}):"]
    for price, row in cheapest:
        results.append(f"- {row.get('dish_name')} at {row.get('restaurant_name')} ({row.get('category')})")
    return "\n".join(results)


@mcp.tool()
def get_average_price(category: str = "") -> str:
    """Get the average price of menu items. Optionally filter by category (case-insensitive partial match)."""
    rows = _load_rows()
    if category:
        category_lower = category.lower()
        rows = [row for row in rows if category_lower in row.get('category', '').lower()]
    if not rows:
        return f"No dishes found" + (f" in category '{category}'" if category else "")
    prices = []
    for row in rows:
        try:
            prices.append(float(row.get('price', 0)))
        except ValueError:
            continue
    if not prices:
        return "No valid prices found"
    avg = sum(prices) / len(prices)
    return f"Average price: €{avg:.2f} (from {len(prices)} items)" + (f" in category '{category}'" if category else "")


@mcp.tool()
def search_menu_items(search_term: str) -> str:
    """Search all fields for a term (case-insensitive). Returns matching records."""
    rows = _load_rows()
    term_lower = search_term.lower()
    matches = []
    for row in rows:
        for value in row.values():
            if term_lower in str(value).lower():
                matches.append(row)
                break
    if not matches:
        return f"No records found containing '{search_term}'"
    results = [f"Found {len(matches)} record(s) containing '{search_term}':"]
    for row in matches[:10]:  # Limit to 10 results
        tags = f" [{row.get('dietary_tags')}]" if row.get('dietary_tags') else ""
        results.append(f"- {row.get('dish_name')}: €{row.get('price')} at {row.get('restaurant_name')}{tags}")
    if len(matches) > 10:
        results.append(f"... and {len(matches) - 10} more")
    return "\n".join(results)


if __name__ == '__main__':
    mcp.run()
