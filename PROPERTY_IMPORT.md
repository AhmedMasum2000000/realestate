# Property Import & Image Management

Guide for importing real property listings and images into the pattayahomepro.com site.

## Quick Start

```bash
# 1. Update property listings
# Edit data/properties.csv with your property data

# 2. Map property images
# Edit data/property-images.csv to link properties to images

# 3. Copy/add new property images
cp /path/to/new/images/*.jpg assets/properties/

# 4. Deploy to site
bin/deploy-properties

# 5. Verify changes
git diff site/index.html | head -50
```

## CSV Format

### data/properties.csv

Required columns:
- `id` - Unique property identifier (e.g., "jomtien-seaview-2bed")
- `title` - Property title/heading
- `area` - Geographic area (Jomtien, Pratumnak, Central Pattaya, North Pattaya, Naklua, Bang Saray)
- `type` - Property type (Condo, Villa, House, Business, Land)
- `deal` - Deal type (sale, rent, business)
- `price` - Sale price in THB (0 if renting)
- `rent` - Monthly rent in THB (0 if selling)
- `beds` - Number of bedrooms (0 for land/business)
- `baths` - Number of bathrooms
- `sqm` - Building area in square meters (0 for land-only)
- `floor` - Floor number (0 if not applicable)
- `land` - Land area in square meters (0 if none)
- `project` - Development/project name (empty string if independent)
- `description` - Full property description (1-2 sentences)
- `features` - Amenities (pipe-separated: "Feature 1|Feature 2|Feature 3")
- `selling_points` - Why this property is compelling (pipe-separated: "Point 1|Point 2|Point 3")

### data/property-images.csv

Columns:
- `property_id` - Must match an `id` in properties.csv
- `image_path` - Path to image file (e.g., "assets/properties/1.jpg")
- `caption` - Image caption/alt text (e.g., "Jomtien Sea-view Condo")

## Property Data Structure

After running `deploy-properties`, the site's `index.html` contains a JavaScript array of properties:

```javascript
const P = [
  {
    id: "jomtien-seaview-2bed",
    ref: "jomtien-seaview-2bed",
    t: "Sea-view two-bed high floor",
    area: "Jomtien",
    type: "Condo",
    deal: "sale",
    price: 4200000,
    med: 4620000,  // Calculated median price for area
    beds: 2,
    baths: 2,
    sqm: 74,
    floor: 21,
    land: 0,
    project: "Sample Beach Residence",
    art: "tower",  // Fallback illustration type
    img: "assets/properties/1.jpg",  // Image path (if mapped)
    imgcap: "Jomtien Sea-view Condo",  // Image caption (if mapped)
    d: "South-facing on the twenty-first floor...",
    feat: ["Sea view", "Foreign freehold", "Pool", "Gym", "Covered parking"],
    why: ["Quota available...", "Below building average per sqm", "Rental history on file"]
  },
  // ... more properties
];
```

## Image Guidelines

**Specifications:**
- Format: JPEG or PNG
- Minimum width: 1200px (for high-DPI displays)
- Aspect ratio: 4:3 recommended (will be cropped with `object-fit: cover`)
- File size: Keep under 500KB for fast loading
- Compression: Use appropriate compression without quality loss

**Naming:**
- Use descriptive names: `1.jpg`, `2.jpg`, etc. (optional, doesn't need to match property IDs)
- Place all images in `assets/properties/` directory

**Mapping:**
- Create rows in `data/property-images.csv` linking property_id to image_path
- Multiple properties can share the same image if needed

## Area Medians

The import script automatically calculates median prices for each area:
- For sale properties: median = property price × 1.1 (10% buffer)
- For rentals: median = monthly rent × 1.15 (15% buffer)

The "Area median" display on property cards only appears when the property is below this calculated median, highlighting value.

## Troubleshooting

### Image not appearing in cards

1. Check `data/property-images.csv` has a row for that property_id
2. Verify image file exists at the path specified
3. Run `bin/deploy-properties` again
4. Hard-refresh browser (Ctrl+Shift+R) to bypass cache

### Property data not updating

1. Ensure CSV files have correct column names (case-sensitive)
2. Check for pipe characters `|` properly used in feature/selling_points lists
3. Verify property_id in images.csv matches an `id` in properties.csv exactly
4. Check for UTF-8 encoding in CSV files

### Prices showing incorrectly

1. Verify `price` or `rent` columns contain only numbers (no ฿ symbol)
2. For rentals, price column should be 0; for sales, rent column should be 0
3. Check deal type matches: "sale", "rent", or "business"

## Automation

To regenerate site data after CSV updates:

```bash
# One-time update
bin/deploy-properties

# Watch for CSV changes and auto-deploy (requires `watchdog`)
pip install watchdog
while true; do
  inotifywait -e modify data/*.csv && bin/deploy-properties
done
```

## Next Steps

1. Prepare your real property data in CSV format
2. Gather high-quality property images
3. Create the image mapping CSV
4. Run the deploy script
5. Push changes to git
6. Deploy site to live domain with `git push`

See README.md for full build and deployment instructions.
