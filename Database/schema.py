import sqlite3
import pandas as pd

# Connect to SQLite database
conn = sqlite3.connect('mydatabase.db')
cursor = conn.cursor()

# Enable foreign key support
cursor.execute('PRAGMA foreign_keys = ON;')

# Create schema
schema = """
-- Creating schema for invoices dataset
CREATE TABLE Customer (
    customer_id TEXT PRIMARY KEY,
    customer_contact_info TEXT,
    billing_address TEXT
);

CREATE TABLE Invoice (
    invoice_id TEXT PRIMARY KEY,
    date TEXT,
    customer_id TEXT,
    salesperson TEXT,
    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id)
);

CREATE TABLE InvoiceItem (
    invoice_id TEXT,
    part_number TEXT,
    item_description TEXT,
    variant_group TEXT,
    quantity INTEGER,
    unit_price REAL,
    total_amount REAL,
    PRIMARY KEY (invoice_id, part_number),
    FOREIGN KEY (invoice_id) REFERENCES Invoice(invoice_id),
    FOREIGN KEY (part_number) REFERENCES Item(item_id)
);

-- Creating schema for compatibility dataset
CREATE TABLE Item (
    item_id TEXT PRIMARY KEY,
    item_description TEXT
);

CREATE TABLE Compatibility (
    core_item TEXT,
    related_item TEXT,
    description TEXT,
    PRIMARY KEY (core_item, related_item),
    FOREIGN KEY (core_item) REFERENCES Item(item_id),
    FOREIGN KEY (related_item) REFERENCES Item(item_id)
);
"""

# Drop existing tables if they exist (to avoid schema mismatch)
cursor.execute("DROP TABLE IF EXISTS InvoiceItems")
cursor.execute("DROP TABLE IF EXISTS Invoices")
cursor.execute("DROP TABLE IF EXISTS Customers")
cursor.execute("DROP TABLE IF EXISTS Item")
cursor.execute("DROP TABLE IF EXISTS Compatibility")

# Execute schema creation
cursor.executescript(schema)


# Read the CSV file
invoice_df = pd.read_csv("data/invoices.csv")
compatibility_df = pd.read_csv("data/compatibility.csv")

# Insert unique customers into Customers table
customers_df = invoice_df[
    ["customer_id", "customer_contact_info", "billing_address"]
].drop_duplicates()
customers_df.to_sql("Customers", conn, if_exists="append", index=False)

# Insert invoices into Invoices table
invoices_df = invoice_df[["invoice_id", "date", "customer_id", "salesperson"]].drop_duplicates()
invoices_df.to_sql("Invoices", conn, if_exists="append", index=False)

# Insert invoice items into InvoiceItems table
items_df = invoice_df[
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




# Commit changes and close connection
conn.commit()  # save changes to the database
conn.close()

######################################################################################