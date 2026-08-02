#!/usr/bin/env python3
"""
HEB Aisle Finder
Reads a YAML grocery list and outputs items sorted by aisle number.

Usage:
    python3 aisle_finder.py grocery_list.yaml

YAML format:
    items:
      - peanut butter
      - coffee
      - chips
      - bread
"""

import sys
import re
import yaml


# Store guide data for HEB San Antonio Store #623
# Parsed from the official HEB store guide PDF
STORE_GUIDE = {
    "air conditioner filters": "Left Wall by 51",
    "air freshener": "51",
    "aluminum foil": "50",
    "appliances": "Kitchen",
    "asian foods": "6",
    "automotive supplies": "27",
    "baby accessories": "28-32",
    "baby food": "28",
    "baby formula": "28",
    "baby medication": "30",
    "baby wipes": "31",
    "bags/wrap": "50",
    "bakeware": "Kitchen",
    "band-aids": "63",
    "barbecue sauce": "4",
    "bath soap": "1-2, 59-60",
    "bath tissue": "49",
    "batteries": "46",
    "beans (canned)": "8",
    "beans (dry)": "5",
    "beer": "Beer & Wine",
    "bird seed": "55",
    "biscuit mix": "10",
    "bleach": "52",
    "boxed dinners": "8",
    "bread": "3",
    "cake mixes": "10",
    "candles": "Cards & Party",
    "candy": "14",
    "canned chili": "7",
    "canned fish": "7",
    "canned fruit": "10",
    "canned meat": "7",
    "canned tomatoes": "8",
    "canned vegetables": "8",
    "canning supplies": "Kitchen",
    "cat food": "56",
    "cat litter": "Left Wall by 56",
    "cereal": "11",
    "cereal (hot)": "11",
    "charcoal": "24-25",
    "chips": "13",
    "cleaners/cleansers": "51",
    "closet items": "Left Wall by 52",
    "coffee": "15",
    "coffee creamer": "15",
    "coffee filters": "15",
    "condiments": "4",
    "cookies": "15",
    "cosmetics": "58",
    "cotton balls": "58",
    "cough & cold": "62",
    "crackers": "15",
    "dental/oral care": "61",
    "deodorant": "59-60",
    "diapers": "32",
    "diet aids": "64",
    "dish soap": "51",
    "dog food": "53-54",
    "dried fruit": "10",
    "electrical needs": "27",
    "eye care": "63",
    "fabric softener": "52",
    "facial care": "59",
    "facial tissue": "49",
    "feminine hygiene": "Left Wall by 59",
    "first aid": "63",
    "floor wax": "51",
    "flour": "9",
    "foil bakeware": "10",
    "foot care": "59",
    "fruit snacks": "12",
    "gift cards": "36",
    "gift wrap": "35",
    "goya": "5",
    "glue": "44",
    "gravy mixes": "7",
    "greeting cards": "Cards & Party",
    "hair accessories": "57",
    "hair care": "57, 60",
    "hair color": "57",
    "hardware": "27",
    "honey": "10",
    "hosiery": "Apparel",
    "hot cocoa": "11",
    "incontinence": "59",
    "insecticides": "Left Wall by 49",
    "instant breakfast": "11",
    "jam/jelly": "10",
    "jell-o": "10",
    "juice": "12",
    "ketchup": "4",
    "kitchen gadgets": "Kitchen",
    "kool-aid": "19",
    "laundry detergent": "52",
    "laxatives": "62",
    "light bulbs": "27",
    "lotion/cream": "1-2, 59-60",
    "macaroni & cheese": "8",
    "marshmallows": "10",
    "matches": "24-25",
    "mayonnaise": "4",
    "men's toiletries": "60",
    "microwaveable food": "7",
    "milk (canned/powdered)": "10",
    "mixers": "Beer & Wine",
    "mops/brooms": "51",
    "mustard": "4",
    "napkins": "50",
    "nutritional aids/bars": "62",
    "nuts (baking)": "10",
    "nuts (snacking)": "14",
    "oil/shortening": "9",
    "olives": "4",
    "pancake mix": "12",
    "paper towels": "49",
    "party supplies": "Cards & Party",
    "pasta (canned)": "7",
    "pasta (dry)": "6",
    "pastries": "3",
    "peanut butter": "10",
    "pet supplies": "53-56",
    "picante sauce": "4",
    "pickles": "4",
    "pimentos": "8",
    "plates/cups": "50",
    "pop tarts": "11",
    "popcorn": "14",
    "potatoes/stuffing": "8",
    "pudding/pie filling": "10",
    "q-tips": "63",
    "religious candles": "Cards & Party",
    "rice": "5",
    "rice cakes": "3",
    "salad dressing": "4",
    "salsa": "4",
    "salt": "10",
    "school supplies": "44-45",
    "seasonal items": "46-48",
    "sewing needs": "52",
    "shampoo/conditioner": "57",
    "shaving needs": "59-60",
    "skin care": "20-21, 59-60",
    "snacks": "14",
    "sodas": "17",
    "soup": "7",
    "spices": "9",
    "sports drinks": "16",
    "starch": "52",
    "sugar": "9",
    "syrup": "12",
    "tea": "16",
    "toaster pastries": "12",
    "toothpicks": "50",
    "tortillas": "3",
    "toys": "36-40",
    "trash bags": "50",
    "vinegar": "4",
    "vitamins": "2",
    "water": "17-19",
    "wine": "Beer & Wine",
}


def find_aisle(item: str) -> tuple[str, str]:
    """
    Find the aisle for a given item. Uses fuzzy matching:
    1. Exact match
    2. Item is a substring of a store guide key
    3. Store guide key is a substring of the item
    4. Any word in the item matches a key
    """
    item_lower = item.lower().strip()

    # Exact match
    if item_lower in STORE_GUIDE:
        return item, STORE_GUIDE[item_lower]

    # Item is substring of a key (e.g., "chips" matches "chips")
    for key, aisle in STORE_GUIDE.items():
        if item_lower in key:
            return item, aisle

    # Key is substring of item (e.g., "peanut butter" found in "crunchy peanut butter")
    for key, aisle in STORE_GUIDE.items():
        if key in item_lower:
            return item, aisle

    # Word-level matching (e.g., "tortilla" matches "tortillas")
    item_words = item_lower.split()
    for key, aisle in STORE_GUIDE.items():
        key_words = key.split()
        for word in item_words:
            if len(word) > 3:  # skip short words like "a", "the"
                for kw in key_words:
                    if word in kw or kw in word:
                        return item, aisle

    return item, "NOT FOUND"


def sort_key(aisle: str) -> tuple[int, str]:
    """
    Sort aisles numerically. Non-numeric aisles (like 'Kitchen', 'Beer & Wine')
    go at the end.
    """
    # Extract the first number from the aisle string
    match = re.search(r'\d+', aisle)
    if match:
        return (0, int(match.group()))
    # Non-numeric aisles sort to the end
    return (1, aisle)


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 aisle_finder.py <grocery_list.yaml>")
        print("\nYAML format:")
        print("  items:")
        print("    - peanut butter")
        print("    - coffee")
        print("    - chips")
        sys.exit(1)

    yaml_file = sys.argv[1]

    try:
        with open(yaml_file, 'r') as f:
            data = yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Error: File '{yaml_file}' not found.")
        sys.exit(1)

    items = data.get('items', [])
    if not items:
        print("No items found in YAML. Use format:\n  items:\n    - item1\n    - item2")
        sys.exit(1)

    # Find aisles for all items
    results = []
    for item in items:
        item_name, aisle = find_aisle(item)
        results.append((item_name, aisle))

    # Group items by aisle
    aisle_groups = {}
    not_found = []
    for item_name, aisle in results:
        if aisle == "NOT FOUND":
            not_found.append(item_name)
        else:
            if aisle not in aisle_groups:
                aisle_groups[aisle] = []
            aisle_groups[aisle].append(item_name)

    # Sort aisles numerically
    sorted_aisles = sorted(aisle_groups.keys(), key=lambda a: sort_key(a))

    # Print results
    print()
    for aisle in sorted_aisles:
        items_str = ", ".join(aisle_groups[aisle])
        print(f"{items_str}: Aisle {aisle}")

    if not_found:
        print()
        for item in not_found:
            print(f"{item}: NOT FOUND")
    print()


if __name__ == "__main__":
    main()
