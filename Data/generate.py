import csv
import random
from datetime import datetime, timedelta

# =====================================================
# ALL ITEMS (Your Exact Dataset)
# =====================================================

door_items = {
    "DO101": ("Door", 250), "DO102": ("Door", 250), "DO103": ("Door", 250),
    "HI101": ("Hinge", 30), "HI102": ("Hinge", 30), "HI103": ("Hinge", 30),
    "KN101": ("Knob", 35),  "KN102": ("Knob", 35),  "KN103": ("Knob", 35),
    "LO101": ("Lock", 60),  "LO102": ("Lock", 60),  "LO103": ("Lock", 60)
}

window_items = {
    "WI101": ("Window", 180), "WI102": ("Window", 180), "WI103": ("Window", 180),
    "FR101": ("Frame", 100),  "FR102": ("Frame", 100),  "FR103": ("Frame", 100),
    "SC101": ("Screen", 75),  "SC102": ("Screen", 75),  "SC103": ("Screen", 75),
    "HA101": ("Handle", 45),  "HA102": ("Handle", 45),  "HA103": ("Handle", 45)
}

sink_items = {
    "SI101": ("Sink", 120), "SI102": ("Sink", 120), "SI103": ("Sink", 120),
    "FA101": ("Faucet", 85), "FA102": ("Faucet", 85), "FA103": ("Faucet", 85),
    "DR101": ("Drain", 40),  "DR102": ("Drain", 40),  "DR103": ("Drain", 40),
    "CA101": ("Cabinet", 150), "CA102": ("Cabinet", 150), "CA103": ("Cabinet", 150)
}

ITEMS = {**door_items, **window_items, **sink_items}

# =====================================================
# COMPATIBILITY (SYMMETRIC + EXPANDED)
# =====================================================

compatibility = {}

def add(a, b):
    compatibility.setdefault(a, set()).add(b)
    compatibility.setdefault(b, set()).add(a)

for i in ["101", "102", "103"]:

    # ---- DOORS ----
    add(f"DO{i}", f"HI{i}")
    add(f"DO{i}", f"KN{i}")
    add(f"DO{i}", f"LO{i}")

    # Optional DO cluster expansion for better balance
    add(f"HI{i}", f"KN{i}")
    add(f"KN{i}", f"LO{i}")

    # ---- WINDOWS ----
    add(f"WI{i}", f"FR{i}")
    add(f"WI{i}", f"SC{i}")
    add(f"WI{i}", f"HA{i}")

    # Optional window expansion
    add(f"FR{i}", f"SC{i}")
    add(f"SC{i}", f"HA{i}")

    # ---- SINKS ----
    add(f"SI{i}", f"FA{i}")
    add(f"SI{i}", f"DR{i}")
    add(f"SI{i}", f"CA{i}")

    # NEW — Proper CA <-> FA/DR cluster expansion
    add(f"CA{i}", f"FA{i}")
    add(f"CA{i}", f"DR{i}")

# =====================================================
# CUSTOMER INFO
# =====================================================

customers = [f"CUST{str(i).zfill(3)}" for i in range(1, 25)]
salespersons = ["SP01", "SP02", "SP03", "SP04", "SP05"]
addresses = ["123 Main", "441 Main", "902 Main", "557 Main", "901 Main", "667 Main"]
emails = [f"customer{i}@email.com" for i in range(1, 25)]

# =====================================================
# RANDOM DATE
# =====================================================

def rnd_date():
    start = datetime(2024, 1, 1)
    end   = datetime(2024, 3, 31)
    return (start + timedelta(days=random.randint(0, 90))).strftime("%Y-%m-%d")

# =====================================================
# BALANCED ROOT ITEM LIST
# =====================================================

balanced_roots = []
roots_per_item = 200 // len(ITEMS)  # ≈ 5 each

for item in ITEMS:
    balanced_roots += [item] * roots_per_item

while len(balanced_roots) < 200:
    balanced_roots.append(random.choice(list(ITEMS.keys())))

random.shuffle(balanced_roots)

# =====================================================
# BUILD INVOICES
# =====================================================

rows = []
invoice_start = 53  # starts from INV0053

def make_row(inv, cust, date, sales, part):
    desc, price = ITEMS[part]
    qty = random.randint(1, 5)
    total = qty * price
    group = part[:2]

    return [
        inv, date, cust, random.choice(emails), random.choice(addresses),
        sales, desc, part, group, qty, price, total
    ]

for idx, root in enumerate(balanced_roots):

    inv = f"INV{str(invoice_start + idx).zfill(3)}"
    cust = random.choice(customers)
    sales = random.choice(salespersons)
    date = rnd_date()

    invoice_items = {root}
    comp_list = list(compatibility.get(root, []))
    random.shuffle(comp_list)

    # balanced number of compatible items
    k = random.choices([1, 2, 3], weights=[0.3, 0.6, 0.1])[0]

    invoice_items.update(comp_list[:k])

    for part in invoice_items:
        rows.append(make_row(inv, cust, date, sales, part))

# =====================================================
# WRITE CSV
# =====================================================

header = [
    "invoice_id", "date", "customer_id", "customer_contact_info",
    "billing_address", "salesperson",
    "item_description", "part_number", "variant_group",
    "quantity", "unit_price", "total_amount"
]

with open("generated_invoices_updated.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(header)
    writer.writerows(rows)

print("Balanced 200-invoice dataset generated.")
