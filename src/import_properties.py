#!/usr/bin/env python3
"""
Import properties from CSV and generate JavaScript code for the site.
Usage: python src/import_properties.py data/properties.csv
"""

import csv
import json
import sys
from pathlib import Path

def parse_pipe_list(s):
    """Parse pipe-separated list into array."""
    if not s or s.strip() == "":
        return []
    return [item.strip() for item in s.split("|")]

def load_property_images(images_csv_path):
    """Load image mappings from CSV file."""
    images = {}
    if not Path(images_csv_path).exists():
        return images

    with open(images_csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            images[row['property_id']] = {
                'path': row['image_path'],
                'caption': row.get('caption', '')
            }
    return images

def load_properties_from_csv(csv_path):
    """Load properties from CSV file and return as list of dicts."""
    properties = []

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Parse numeric fields
            price = int(row['price']) if row['price'] else 0
            rent = int(row['rent']) if row['rent'] else 0
            beds = int(row['beds']) if row['beds'] else 0
            baths = int(row['baths']) if row['baths'] else 0
            sqm = int(row['sqm']) if row['sqm'] else 0
            floor = int(row['floor']) if row['floor'] else 0
            land = int(row['land']) if row['land'] else 0

            # Determine median price (simplified - should be based on area)
            deal = row['deal']
            if deal == 'rent':
                med = int(rent * 1.15) if rent else 0
            else:
                med = int(price * 1.1) if price else 0

            # Determine art (illustration type) based on property type
            prop_type = row['type']
            art_map = {
                'Condo': 'tower',
                'Villa': 'villa',
                'House': 'villa',
                'Business': 'shop',
                'Land': 'land',
            }
            art = art_map.get(prop_type, 'tower')

            prop = {
                'id': row['id'],
                'ref': row['id'],  # Use ID as reference for now
                't': row['title'],
                'area': row['area'],
                'type': prop_type,
                'deal': deal,
                'price': price,
                'rent': rent,
                'med': med,
                'beds': beds,
                'baths': baths,
                'sqm': sqm,
                'floor': floor,
                'land': land,
                'project': row['project'],
                'art': art,
                'd': row['description'],
                'feat': parse_pipe_list(row['features']),
                'why': parse_pipe_list(row['selling_points']),
            }
            properties.append(prop)

    return properties

def generate_js_code(properties, images=None):
    """Generate JavaScript const P = [...] code."""
    if images is None:
        images = {}
    lines = ["const P = ["]

    for i, prop in enumerate(properties):
        # Format each property as a JS object literal
        lines.append(" {")
        lines.append(f'  id:"{prop["id"]}", ref:"{prop["ref"]}", t:"{prop["t"]}",')
        lines.append(f'  area:"{prop["area"]}", type:"{prop["type"]}", deal:"{prop["deal"]}", ')

        # Price/rent line
        price_line = f'  price:{prop["price"]}, ' if prop["price"] else '  '
        if prop["rent"]:
            price_line += f'rent:{prop["rent"]}, '
        price_line += f'med:{prop["med"]},'
        lines.append(price_line)

        # Dimensions
        lines.append(f'  beds:{prop["beds"]}, baths:{prop["baths"]}, sqm:{prop["sqm"]}, ' +
                    f'floor:{prop["floor"]}, land:{prop["land"]}, project:"{prop["project"]}", art:"{prop["art"]}",')

        # Image path (if available)
        if prop["id"] in images:
            img = images[prop["id"]]
            lines.append(f'  img:"{img["path"]}", imgcap:"{img["caption"]}",')

        # Description
        desc = prop["d"].replace('"', '\\"')
        lines.append(f'  d:"{desc}",')

        # Features array
        feat_str = '", "'.join(prop["feat"])
        lines.append(f'  feat:["{feat_str}"],')

        # Why array
        why_str = '", "'.join(prop["why"])
        comma = ',' if i < len(properties) - 1 else ''
        lines.append(f'  why:["{why_str}"]' + comma + '}')
        lines.append('')

    lines.append("];")
    return "\n".join(lines)

def main():
    if len(sys.argv) < 2:
        print("Usage: python src/import_properties.py data/properties.csv")
        print("\nThis will generate JavaScript code for properties.")
        sys.exit(1)

    csv_path = Path(sys.argv[1])

    if not csv_path.exists():
        print(f"Error: {csv_path} not found")
        sys.exit(1)

    try:
        properties = load_properties_from_csv(csv_path)
        # Load images if the mapping file exists
        images_csv = csv_path.parent / 'property-images.csv'
        images = load_property_images(images_csv)
        js_code = generate_js_code(properties, images)

        # Output to stdout
        print("// Generated from CSV - replace const P = [...] in index.html")
        print(js_code)

        print("\n// JSON format for reference:", file=sys.stderr)
        print(json.dumps(properties, indent=2), file=sys.stderr)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
