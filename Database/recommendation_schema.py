import sqlite3
import pandas as pd

# Connect to SQLite database
conn = sqlite3.connect('recommendation.db')
cursor = conn.cursor()

# Enable foreign key support
cursor.execute('PRAGMA foreign_keys = ON;')

# Drop existing tables
cursor.execute("DROP TABLE IF EXISTS InvoiceItems")
cursor.execute("DROP TABLE IF EXISTS Invoices")
cursor.execute("DROP TABLE IF EXISTS Customers")
cursor.execute("DROP TABLE IF EXISTS Items")
cursor.execute("DROP TABLE IF EXISTS Compatibility")
cursor.execute("DROP TABLE IF EXISTS Recommendations")

# Create schema
schema = """
CREATE TABLE Customers (
    customer_id TEXT PRIMARY KEY,
    customer_contact_info TEXT,
    billing_address TEXT
);

CREATE TABLE Invoices (
    invoice_id TEXT PRIMARY KEY,
    date TEXT,
    customer_id TEXT,
    salesperson TEXT,
    FOREIGN KEY (customer_id) REFERENCES Customers(customer_id)
);

CREATE TABLE Items (
    item_id TEXT PRIMARY KEY,
    item_description TEXT,
    unit_price REAL
);

CREATE TABLE InvoiceItems (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_id TEXT,
    part_number TEXT,
    item_description TEXT,
    variant_group TEXT,
    quantity INTEGER,
    unit_price REAL,
    total_amount REAL,
    FOREIGN KEY (invoice_id) REFERENCES Invoices(invoice_id),
    FOREIGN KEY (part_number) REFERENCES Items(item_id)
);

CREATE TABLE Compatibility (
    core_item TEXT,
    related_item TEXT,
    PRIMARY KEY (core_item, related_item),
    FOREIGN KEY (core_item) REFERENCES Items(item_id),
    FOREIGN KEY (related_item) REFERENCES Items(item_id)
);

CREATE TABLE Recommendations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id TEXT,
    recommended_item TEXT,
    cosine_similarity REAL
);

ALTER TABLE Items ADD COLUMN short_description TEXT;

"""
cursor.executescript(schema)

# Load CSV data
invoice_df = pd.read_csv("../data/generated_invoices_updated.csv")
compatibility_df = pd.read_csv("../data/compatibility.csv")

# Insert Customers
customers_df = (
    invoice_df[["customer_id", "customer_contact_info", "billing_address"]]
    .dropna(subset=["customer_id"])
    .drop_duplicates(subset=["customer_id"])
)
customers_df.to_sql("Customers", conn, if_exists="append", index=False)
print(f"Inserted {len(customers_df)} customers")

# Insert Invoices
invoices_df = (
    invoice_df[["invoice_id", "date", "customer_id", "salesperson"]]
    .dropna(subset=["invoice_id"])
    .drop_duplicates(subset=["invoice_id"])
)
invoices_df.to_sql("Invoices", conn, if_exists="append", index=False)
print(f"Inserted {len(invoices_df)} invoices")

# Insert Items (including unit_price)
items_df = (
    invoice_df[["part_number", "item_description", "unit_price"]]
    .dropna(subset=["part_number"])
    .drop_duplicates(subset=["part_number"])
    .rename(columns={"part_number": "item_id"})
)

# Make sure unit_price is numeric
items_df["unit_price"] = pd.to_numeric(items_df["unit_price"], errors="coerce").fillna(0)

items_df.to_sql("Items", conn, if_exists="append", index=False)
print(f"Inserted {len(items_df)} items with unit prices")

cursor.executescript("""
UPDATE Items SET short_description = 'A premium-grade kitchen faucet crafted from stainless steel. Features smooth rotation, controlled water flow, and a sleek, modern finish.' WHERE item_id = 'FA102';
UPDATE Items SET short_description = 'A deep stainless steel sink with a noise-absorbing coating. Designed for modern kitchens and daily heavy use with easy maintenance.' WHERE item_id = 'SI102';
UPDATE Items SET short_description = 'Spacious wooden cabinet designed for kitchen storage. Built with high-quality plywood and hydraulic hinges for smooth operation.' WHERE item_id = 'CA102';
UPDATE Items SET short_description = 'Compact and efficient single-bowl sink ideal for apartments or compact kitchen spaces. Features an anti-scratch matte finish.' WHERE item_id = 'SI103';
UPDATE Items SET short_description = 'Sliding window with double-layer tempered glass and noise reduction technology. Weather-sealed for durability.' WHERE item_id = 'WI103';
UPDATE Items SET short_description = 'Durable metal frame suitable for mounting windows or doors. Rust-resistant finish ensures long-term stability.' WHERE item_id = 'FR102';
UPDATE Items SET short_description = 'Heavy-duty hinge that allows smooth, quiet door movement. Built for long-lasting performance.' WHERE item_id = 'HI101';
UPDATE Items SET short_description = 'Secure locking mechanism with anti-corrosion finish and precision key design. Ideal for both interior and exterior doors.' WHERE item_id = 'LO103';
UPDATE Items SET short_description = 'Solid wood interior door with a polished surface and durable core. Ensures both elegance and strength.' WHERE item_id = 'DO103';
UPDATE Items SET short_description = 'Sleek stainless lock with dual-turn mechanism. Ideal for modern home security needs.' WHERE item_id = 'LO102';
UPDATE Items SET short_description = 'High-flow floor drain equipped with anti-clog technology. Suitable for bathrooms and utility areas.' WHERE item_id = 'DR102';
UPDATE Items SET short_description = 'Compact wall cabinet with soft-close doors and elegant matte finish coating.' WHERE item_id = 'CA101';
UPDATE Items SET short_description = 'Classic double-pane window designed for homes needing natural light and insulation.' WHERE item_id = 'WI101';
UPDATE Items SET short_description = 'Weatherproof protective screen with reinforced corners. Ideal for ventilation and insect protection.' WHERE item_id = 'SC101';
UPDATE Items SET short_description = 'Energy-efficient window with UV protection and noise-reduction coating.' WHERE item_id = 'WI102';
UPDATE Items SET short_description = 'Double-basin sink with smooth rounded edges and scratch-resistant finish.' WHERE item_id = 'SI101';
UPDATE Items SET short_description = 'Heavy-duty bathroom drain designed for fast water drainage with anti-odor protection.' WHERE item_id = 'DR101';
UPDATE Items SET short_description = 'Multi-purpose cabinet featuring adjustable shelves and premium laminate coating.' WHERE item_id = 'CA103';
UPDATE Items SET short_description = 'Elegant faucet combining ergonomic design and superior water efficiency. Built with a brushed metal finish.' WHERE item_id = 'FA103';
UPDATE Items SET short_description = 'Lightweight aluminum frame with corrosion-resistant coating, suitable for indoor and outdoor installation.' WHERE item_id = 'FR103';
UPDATE Items SET short_description = 'Classic door lock with precision key design. Provides sturdy and reliable security for home use.' WHERE item_id = 'LO101';
UPDATE Items SET short_description = 'Polished metal knob with ergonomic contour for easy grip. Ideal for drawers and cabinets.' WHERE item_id = 'KN101';
UPDATE Items SET short_description = 'Premium front door crafted from treated hardwood. Features a protective laminate surface and long-lasting durability.' WHERE item_id = 'DO101';
UPDATE Items SET short_description = 'Fine mesh insect screen that fits snugly into window frames. Designed for improved airflow and pest protection.' WHERE item_id = 'SC102';
UPDATE Items SET short_description = 'Industrial-grade hinge designed to support heavy doors while allowing smooth movement.' WHERE item_id = 'HI102';
UPDATE Items SET short_description = 'Modern laminated door featuring a strong frame and smooth finish. Ideal for both residential and office interiors.' WHERE item_id = 'DO102';
UPDATE Items SET short_description = 'Flexible aluminum screen for both windows and balconies. Provides ventilation while blocking insects.' WHERE item_id = 'SC103';
UPDATE Items SET short_description = 'Round decorative knob with brushed nickel finish. Adds elegance to cabinets and wardrobes.' WHERE item_id = 'KN102';
UPDATE Items SET short_description = 'Black handle crafted from high-grade aluminum alloy. Ideal for contemporary-styled doors and drawers.' WHERE item_id = 'HA103';
UPDATE Items SET short_description = 'Curved metal handle designed for comfort and grip. Scratch-resistant matte coating provides long-lasting finish.' WHERE item_id = 'HA102';
UPDATE Items SET short_description = 'Compact stainless drain with odor trap. Perfect for bathroom and kitchen applications.' WHERE item_id = 'DR103';
UPDATE Items SET short_description = 'Stylish bathroom faucet with rust-resistant coating and smooth-flow technology.' WHERE item_id = 'FA101';
UPDATE Items SET short_description = 'Reinforced structural frame that blends durability with a clean, modern profile.' WHERE item_id = 'FR101';
UPDATE Items SET short_description = 'Solid stainless handle with brushed finish. Combines strength with modern design.' WHERE item_id = 'HA101';
UPDATE Items SET short_description = 'Minimalist door knob built from zinc alloy. Combines a simple design with lasting durability.' WHERE item_id = 'KN103';
UPDATE Items SET short_description = 'Outdoor hinge with stainless finish. Combines strength and weather resistance for long-term use.' WHERE item_id = 'HI103';
""")

# Insert Invoice Items
invoice_items_df = invoice_df[
    [
        "invoice_id",
        "part_number",
        "item_description",
        "variant_group",
        "quantity",
        "unit_price",
        "total_amount",
    ]
]

valid_invoice_ids = set(invoices_df["invoice_id"])
valid_item_ids = set(items_df["item_id"])

before_count = len(invoice_items_df)
invoice_items_df = invoice_items_df[
    invoice_items_df["invoice_id"].isin(valid_invoice_ids)
]
invoice_items_df = invoice_items_df[
    invoice_items_df["part_number"].isin(valid_item_ids)
]
after_count = len(invoice_items_df)
# print(f"Filtered out {before_count - after_count} invalid invoice-item rows")

invoice_items_df.to_sql("InvoiceItems", conn, if_exists="append", index=False)
print(f"Inserted {len(invoice_items_df)} invoice items")

# Insert Compatibility
if not compatibility_df.empty:
    
    # Check missing items
    valid_items = set(items_df["item_id"])
    missing_core = set(compatibility_df["core_item"]) - valid_items
    missing_related = set(compatibility_df["related_item"]) - valid_items

    # Filter valid compatibility rows
    valid_compatibility_df = compatibility_df[
        compatibility_df["core_item"].isin(valid_items)
        & compatibility_df["related_item"].isin(valid_items)
    ]
    print(f"\n Filtered out {len(compatibility_df) - len(valid_compatibility_df)} invalid compatibility rows")

    # Keep only core_item and related_item (ignore description)
    valid_compatibility_df = valid_compatibility_df[["core_item", "related_item"]]

    # Insert valid rows into Compatibility table
    valid_compatibility_df.to_sql("Compatibility", conn, if_exists="append", index=False)
    print(f"Inserted {len(valid_compatibility_df)} compatibility entries")

else:
    print("No compatibility data found.")

conn.commit()
conn.close()

print("\n Database created and populated successfully!")
