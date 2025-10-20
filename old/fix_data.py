import pandas as pd

# Load your invoice data
df = pd.read_csv("generated_invoices.csv")

# Define fixed unit prices
price_map = {
    "DO101": 250, "DO102": 250, "DO103": 250,
    "HA101": 45, "HA102": 45, "HA103": 45,
    "HI101": 30, "HI102": 30, "HI103": 30,
    "LO101": 60, "LO102": 60, "LO103": 60,
    "KN101": 35, "KN102": 35, "KN103": 35,
    "WI101": 180, "WI102": 180, "WI103": 180,
    "FR101": 100, "FR102": 100, "FR103": 100,
    "SC101": 75, "SC102": 75, "SC103": 75,
    "SI101": 120, "SI102": 120, "SI103": 120,
    "FA101": 85, "FA102": 85, "FA103": 85,
    "DR101": 40, "DR102": 40, "DR103": 40,
    "CA101": 150, "CA102": 150, "CA103": 150
}

# Apply fixed prices
df["unit_price"] = df["part_number"].map(price_map)

# Ensure quantity column exists and fill missing with 1
if "quantity" in df.columns:
    df["quantity"] = df["quantity"].fillna(1)
else:
    print("No 'quantity' column found — please confirm the column name.")

# Recalculate totals
df["total_amount"] = df["unit_price"] * df["quantity"]

# Save the updated file
df.to_csv("generated_invoices_fixed.csv", index=False)

print("Updated invoices with fixed prices and recalculated totals saved as 'generated_invoices_fixed.csv'")
print(df.head())
