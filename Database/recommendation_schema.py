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
"""
cursor.executescript(schema)

# Load CSV data
invoice_df = pd.read_csv("../data/generated_invoices.csv")
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

    # print(f"\nMissing core items: {len(missing_core)}")
    # print(missing_core)
    # print(f"\nMissing related items: {len(missing_related)}")
    # print(missing_related)

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
