import pandas as pd
import sqlite3

# Read the CSV file
df = pd.read_csv("invoices.csv")

# Connect to SQLite database
conn = sqlite3.connect("invoices.db")
cursor = conn.cursor()

# Drop existing tables if they exist (to avoid schema mismatch)
cursor.execute("DROP TABLE IF EXISTS InvoiceItems")
cursor.execute("DROP TABLE IF EXISTS Invoices")
cursor.execute("DROP TABLE IF EXISTS Customers")

# Create Customers table
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS Customers (
        customer_id TEXT PRIMARY KEY,
        customer_contact_info TEXT NOT NULL,
        billing_address TEXT NOT NULL
    )
"""
)

# Create Invoices table
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS Invoices (
        invoice_id TEXT PRIMARY KEY,
        date DATE NOT NULL,
        customer_id TEXT NOT NULL,
        salesperson TEXT NOT NULL,
        FOREIGN KEY (customer_id) REFERENCES Customers(customer_id)
    )
"""
)

# Create InvoiceItems table
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS InvoiceItems (
        invoice_id TEXT NOT NULL,
        item_description TEXT NOT NULL,
        part_number TEXT NOT NULL,
        variant_group TEXT,
        quantity INTEGER NOT NULL,
        unit_price REAL NOT NULL,
        total_amount REAL NOT NULL,
        FOREIGN KEY (invoice_id) REFERENCES Invoices(invoice_id)
    )
"""
)

# Insert unique customers into Customers table
customers_df = df[
    ["customer_id", "customer_contact_info", "billing_address"]
].drop_duplicates()
customers_df.to_sql("Customers", conn, if_exists="append", index=False)

# Insert invoices into Invoices table
invoices_df = df[["invoice_id", "date", "customer_id", "salesperson"]].drop_duplicates()
invoices_df.to_sql("Invoices", conn, if_exists="append", index=False)

# Insert invoice items into InvoiceItems table
items_df = df[
    [
        "invoice_id",
        "item_description",
        "part_number",
        "variant_group",
        "quantity",
        "unit_price",
        "total_amount",
    ]
]
items_df.to_sql("InvoiceItems", conn, if_exists="append", index=False)

# Print schema and data for each table
tables = ["Customers", "Invoices", "InvoiceItems"]

for table in tables:
    print(f"\nSchema and Data for {table}:")

    # Print schema
    cursor.execute(f"PRAGMA table_info({table})")
    print("Schema:")
    for column in cursor.fetchall():
        print(
            f"  Column: {column[1]}, Type: {column[2]}, Not Null: {bool(column[3])}, Primary Key: {bool(column[5])}"
        )

    # Print sample data (first 5 rows)
    cursor.execute(f"SELECT * FROM {table} LIMIT 5")
    print("Sample Data:")
    for row in cursor.fetchall():
        print(f"  {row}")

# Commit changes and close connection
conn.commit()  # save changes to the database
conn.close()

print("\nSchema created and data imported successfully!")
