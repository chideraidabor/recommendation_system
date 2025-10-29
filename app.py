# from flask import Flask, jsonify, render_template, request
# from flask_cors import CORS
# import sqlite3
# from datetime import datetime

# app = Flask(
#     __name__,
#     template_folder="frontend/templates",
#     static_folder="frontend"
# )
# CORS(app)

# DB_PATH = "Database/recommendation.db"


# # --------------------------------------------------------------------
# # Utility: Get database connection
# # --------------------------------------------------------------------
# def connect_db():
#     conn = sqlite3.connect(DB_PATH)
#     conn.row_factory = sqlite3.Row
#     conn.execute("PRAGMA foreign_keys = ON;")
#     return conn


# # --------------------------------------------------------------------
# # Base Routes
# # --------------------------------------------------------------------
# @app.route('/')
# def index():
#     return render_template('index.html')

# @app.route('/invoice')
# def invoice_page():
#     return render_template('invoice.html')


# # --------------------------------------------------------------------
# # Items and Recommendations
# # --------------------------------------------------------------------
# @app.route("/items", methods=["GET"])
# def get_items():
#     conn = connect_db()
#     cursor = conn.cursor()
#     cursor.execute("SELECT item_id, item_description, unit_price FROM Items")
#     rows = cursor.fetchall()
#     conn.close()
#     return jsonify([
#         {"item_id": r["item_id"], "item_description": r["item_description"], "unit_price": r["unit_price"]}
#         for r in rows
#     ])


# @app.route("/recommendations/<item_id>", methods=["GET"])
# def get_recommendations(item_id):
#     conn = connect_db()
#     cursor = conn.cursor()
#     cursor.execute("""
#         SELECT recommended_item, cosine_similarity
#         FROM Recommendations
#         WHERE item_id = ?
#         ORDER BY cosine_similarity DESC
#         LIMIT 5
#     """, (item_id,))
#     rows = cursor.fetchall()
#     conn.close()
#     return jsonify([
#         {"recommended_item": r["recommended_item"], "score": r["cosine_similarity"]}
#         for r in rows
#     ])


# # --------------------------------------------------------------------
# # Get Next Invoice ID
# # --------------------------------------------------------------------
# @app.route('/next_invoice_id', methods=['GET'])
# def next_invoice_id():
#     conn = connect_db()
#     cursor = conn.cursor()
#     cursor.execute("SELECT invoice_id FROM Invoices ORDER BY invoice_id DESC LIMIT 1")
#     last = cursor.fetchone()
#     conn.close()

#     if last and last["invoice_id"].startswith("INV"):
#         num = int(last["invoice_id"][3:]) + 1
#     else:
#         num = 1

#     next_id = f"INV{num:04d}"
#     return jsonify({"next_invoice_id": next_id})


# @app.route('/save_invoice', methods=['POST'])
# def save_invoice():
#     from datetime import datetime

#     data = request.get_json()
#     print("🧾 Received invoice data:", data)

#     conn = connect_db()
#     conn.row_factory = sqlite3.Row
#     cursor = conn.cursor()

#     # 1️⃣ Check invoice ID — auto-increment if duplicate
#     invoice_id = data.get("number")
#     cursor.execute("SELECT 1 FROM Invoices WHERE invoice_id = ?", (invoice_id,))
#     exists = cursor.fetchone()
#     if exists:
#         cursor.execute("SELECT invoice_id FROM Invoices ORDER BY invoice_id DESC LIMIT 1")
#         last = cursor.fetchone()
#         if last and last["invoice_id"].startswith("INV"):
#             num = int(last["invoice_id"][3:]) + 1
#         else:
#             num = 1
#         invoice_id = f"INV{num:04d}"
#         print(f"⚠️ Duplicate invoice found — new ID assigned: {invoice_id}")

#     # 2️⃣ Extract core data
#     date = data.get("date") or datetime.now().strftime("%Y-%m-%d")
#     customer_contact = data.get("customer")
#     billing = data.get("billing")
#     salesperson = data.get("salesperson")
#     items = data.get("items", [])

#     # 3️⃣ Customer handling
#     cursor.execute("SELECT customer_id FROM Customers WHERE customer_contact_info = ?", (customer_contact,))
#     row = cursor.fetchone()
#     if row:
#         customer_id = row["customer_id"]
#         print(f"🟢 Existing customer found: {customer_id}")
#     else:
#         cursor.execute("SELECT COUNT(*) FROM Customers")
#         count = cursor.fetchone()[0] or 0
#         customer_id = f"CUST{count + 1:04d}"
#         cursor.execute("""
#             INSERT INTO Customers (customer_id, customer_contact_info, billing_address)
#             VALUES (?, ?, ?)
#         """, (customer_id, customer_contact, billing))
#         print(f"🆕 Created new customer: {customer_id}")

#     # 4️⃣ Insert invoice
#     cursor.execute("""
#         INSERT INTO Invoices (invoice_id, date, customer_id, salesperson)
#         VALUES (?, ?, ?, ?)
#     """, (invoice_id, date, customer_id, salesperson))
#     print(f"🧾 Inserted invoice: {invoice_id}")

#     # 5️⃣ Insert items
#     for item in items:
#         cursor.execute("""
#             INSERT INTO InvoiceItems (
#                 invoice_id, part_number, item_description,
#                 variant_group, quantity, unit_price, total_amount
#             )
#             VALUES (?, ?, ?, ?, ?, ?, ?)
#         """, (
#             invoice_id,
#             item.get("partNumber"),
#             item.get("description"),
#             item.get("addon") or "",
#             item.get("qty") or 0,
#             item.get("price") or 0.0,
#             item.get("amount") or 0.0
#         ))

#     conn.commit()
#     conn.close()

#     print(f"✅ Invoice {invoice_id} saved successfully for customer {customer_id}.")
#     return jsonify({
#         "message": f"Invoice {invoice_id} saved successfully!",
#         "invoice_id": invoice_id
#     }), 201

# # --------------------------------------------------------------------
# # Retrieve Invoice (for /invoice page)
# # --------------------------------------------------------------------
# @app.route('/get_invoice/<invoice_id>', methods=['GET'])
# def get_invoice(invoice_id):
#     conn = connect_db()
#     cursor = conn.cursor()

#     # Fetch invoice header + customer info
#     cursor.execute("""
#         SELECT i.invoice_id, i.date, i.salesperson,
#                c.customer_contact_info, c.billing_address
#         FROM Invoices i
#         JOIN Customers c ON i.customer_id = c.customer_id
#         WHERE i.invoice_id = ?
#     """, (invoice_id,))
#     invoice = cursor.fetchone()

#     if not invoice:
#         conn.close()
#         return jsonify({"error": "Invoice not found"}), 404

#     # Fetch line items
#     cursor.execute("""
#         SELECT part_number, item_description, variant_group,
#                quantity, unit_price, total_amount
#         FROM InvoiceItems
#         WHERE invoice_id = ?
#     """, (invoice_id,))
#     items = cursor.fetchall()
#     conn.close()

#     subtotal = sum([float(i["total_amount"]) for i in items])
#     tax = subtotal * 0.05
#     shipping = 0.00
#     total = subtotal + tax + shipping

#     return jsonify({
#         "invoice": dict(invoice),
#         "items": [dict(i) for i in items],
#         "totals": {
#             "subtotal": subtotal,
#             "tax": tax,
#             "shipping": shipping,
#             "total": total
#         }
#     })

# if __name__ == "__main__":
#     app.run(debug=True)


from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
import sqlite3
from datetime import datetime

app = Flask(
    __name__,
    template_folder="frontend/templates",
    static_folder="frontend"
)
CORS(app)
DB_PATH = "Database/recommendation.db"

def connect_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/invoice')
def invoice_page():
    return render_template('invoice.html')

@app.route("/items", methods=["GET"])
def get_items():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT item_id, item_description, unit_price FROM Items")
    rows = cursor.fetchall()
    conn.close()
    return jsonify([
        {"item_id": r["item_id"], "item_description": r["item_description"], "unit_price": r["unit_price"]}
        for r in rows
    ])


@app.route("/recommendations/<item_id>", methods=["GET"])
def get_recommendations(item_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT recommended_item, cosine_similarity
        FROM Recommendations
        WHERE item_id = ?
        ORDER BY cosine_similarity DESC
        LIMIT 5
    """, (item_id,))
    rows = cursor.fetchall()
    conn.close()
    return jsonify([
        {"recommended_item": r["recommended_item"], "score": r["cosine_similarity"]}
        for r in rows
    ])

@app.route('/next_invoice_id', methods=['GET'])
def next_invoice_id():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT invoice_id FROM Invoices")
    rows = cursor.fetchall()
    conn.close()

    existing_numbers = []
    for row in rows:
        inv = str(row["invoice_id"])
        if inv.startswith("INV"):
            try:
                num = int(inv[3:])
                existing_numbers.append(num)
            except ValueError:
                continue

    if existing_numbers:
        next_num = max(existing_numbers) + 1
    else:
        next_num = 1

    next_id = f"INV{next_num:04d}"
    print(f"🆕 Checked DB — next invoice ID: {next_id}")
    return jsonify({"next_invoice_id": next_id})

@app.route('/save_invoice', methods=['POST'])
def save_invoice():
    data = request.get_json()
    print("🧾 Received invoice data:", data)

    conn = connect_db()
    cursor = conn.cursor()

    # 1️⃣ Check invoice ID — auto-increment if duplicate
    invoice_id = data.get("number")
    cursor.execute("SELECT 1 FROM Invoices WHERE invoice_id = ?", (invoice_id,))
    exists = cursor.fetchone()
    if exists:
        cursor.execute("SELECT invoice_id FROM Invoices ORDER BY invoice_id DESC LIMIT 1")
        last = cursor.fetchone()
        if last and str(last["invoice_id"]).startswith("INV"):
            try:
                num = int(last["invoice_id"][3:]) + 1
            except (ValueError, TypeError):
                num = 1
        else:
            num = 1
        invoice_id = f"INV{num:04d}"
        print(f"⚠️ Duplicate invoice found — new ID assigned: {invoice_id}")

    # 2️⃣ Extract data
    date = data.get("date") or datetime.now().strftime("%Y-%m-%d")
    customer_contact = data.get("customer")
    billing = data.get("billing")
    salesperson = data.get("salesperson")
    items = data.get("items", [])

    cursor.execute("SELECT customer_id FROM Customers WHERE customer_contact_info = ?", (customer_contact,))
    row = cursor.fetchone()
    if row:
        customer_id = row["customer_id"]
        print(f" Existing customer found: {customer_id}")
    else:
        cursor.execute("SELECT COUNT(*) FROM Customers")
        count = cursor.fetchone()[0] or 0
        customer_id = f"CUST{count + 1:04d}"
        cursor.execute("""
            INSERT INTO Customers (customer_id, customer_contact_info, billing_address)
            VALUES (?, ?, ?)
        """, (customer_id, customer_contact, billing))
        print(f"Created new customer: {customer_id}")

    # 4️ Insert invoice
    cursor.execute("""
        INSERT INTO Invoices (invoice_id, date, customer_id, salesperson)
        VALUES (?, ?, ?, ?)
    """, (invoice_id, date, customer_id, salesperson))
    print(f"🧾 Inserted invoice: {invoice_id}")

    # 5️ Insert items
    for item in items:
        cursor.execute("""
            INSERT INTO InvoiceItems (
                invoice_id, part_number, item_description,
                variant_group, quantity, unit_price, total_amount
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            invoice_id,
            item.get("partNumber"),
            item.get("description"),
            item.get("addon") or "",
            item.get("qty") or 0,
            item.get("price") or 0.0,
            item.get("amount") or 0.0
        ))

    conn.commit()
    conn.close()

    print(f" Invoice {invoice_id} saved successfully for customer {customer_id}.")
    return jsonify({
        "message": f"Invoice {invoice_id} saved successfully!",
        "invoice_id": invoice_id
    }), 201


# ================================================================
#  RETRIEVE INVOICE
# ================================================================
@app.route('/get_invoice/<invoice_id>', methods=['GET'])
def get_invoice(invoice_id):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT i.invoice_id, i.date, i.salesperson,
               c.customer_contact_info, c.billing_address
        FROM Invoices i
        JOIN Customers c ON i.customer_id = c.customer_id
        WHERE i.invoice_id = ?
    """, (invoice_id,))
    invoice = cursor.fetchone()

    if not invoice:
        conn.close()
        return jsonify({"error": "Invoice not found"}), 404

    cursor.execute("""
        SELECT part_number, item_description, variant_group,
               quantity, unit_price, total_amount
        FROM InvoiceItems
        WHERE invoice_id = ?
    """, (invoice_id,))
    items = cursor.fetchall()
    conn.close()

    subtotal = sum([float(i["total_amount"]) for i in items])
    tax = subtotal * 0.05
    shipping = 0.00
    total = subtotal + tax + shipping

    return jsonify({
        "invoice": dict(invoice),
        "items": [dict(i) for i in items],
        "totals": {
            "subtotal": subtotal,
            "tax": tax,
            "shipping": shipping,
            "total": total
        }
    })


if __name__ == "__main__":
    app.run(debug=True)
