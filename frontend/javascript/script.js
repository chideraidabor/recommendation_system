let allItems = [];

// Fetch items from backend and populate first blank row
async function fetchItems() {
  try {
    const response = await fetch("http://127.0.0.1:5000/items");
    allItems = await response.json();
    console.log("Items loaded:", allItems);

    // Create one blank row after data is fetched
    addNewRow();
  } catch (error) {
    console.error("Error fetching items:", error);
  }
}
fetchItems();

// Function to update totals for all rows
function updateTotals() {
  const rows = document.querySelectorAll("#itemsTable tbody tr");
  let subtotal = 0;

  rows.forEach(row => {
    const qty = parseFloat(row.querySelector(".quantity")?.value) || 0;
    const price = parseFloat(row.querySelector(".unitPrice")?.value) || 0;
    const amount = qty * price;
    row.querySelector(".amount").textContent = amount.toFixed(2);
    subtotal += amount;
  });

  const tax = subtotal * 0.05;
  const shipping = 0.00;
  const total = subtotal + tax + shipping;

  document.getElementById("subtotal").textContent = subtotal.toFixed(2);
  document.getElementById("tax").textContent = tax.toFixed(2);
  document.getElementById("shipping").textContent = shipping.toFixed(2);
  document.getElementById("total").textContent = total.toFixed(2);
}

// Reusable function to add a new item row
function addNewRow() {
  const tbody = document.querySelector("#itemsTable tbody");

  // Build part number dropdown dynamically
  const partOptions = allItems
    .map(item => `<option value="${item.item_id}">${item.item_id}</option>`)
    .join("");

  const newRow = document.createElement("tr");
  newRow.innerHTML = `
    <td>
      <select class="partNumber">
        <option value="">Select Part</option>
        ${partOptions}
      </select>
    </td>
    <td><input type="text" class="description" placeholder="Auto-filled" readonly></td>
    <td><input type="number" value="1" min="1" class="quantity"></td>
    <td><input type="number" value="0" step="0.01" class="unitPrice" readonly></td>
    <td class="amount">0.00</td>
    <td>
      <select class="addon">
        <option value="">None</option>
      </select>
    </td>
  `;

  tbody.appendChild(newRow);

  const partSelect = newRow.querySelector(".partNumber");
  const qtyInput = newRow.querySelector(".quantity");
  const addonSelect = newRow.querySelector(".addon");

  // Handle part selection
  partSelect.addEventListener("change", async (e) => {
    const selectedId = e.target.value;
    const selectedItem = allItems.find(item => item.item_id === selectedId);

    if (selectedItem) {
      // Check for duplicates
      const existingRow = Array.from(tbody.querySelectorAll("tr")).find(
        row => row.querySelector(".partNumber").value === selectedId && row !== newRow
      );

      if (existingRow) {
        const existingQty = existingRow.querySelector(".quantity");
        existingQty.value = parseInt(existingQty.value) + 1;
        newRow.remove();
        updateTotals();
      } else {
        // Fill description and unit price
        newRow.querySelector(".description").value = selectedItem.item_description;
        newRow.querySelector(".unitPrice").value = selectedItem.unit_price.toFixed(2);
        updateTotals();

        // Fetch recommended add-ons dynamically
        try {
          const res = await fetch(`http://127.0.0.1:5000/recommendations/${selectedId}`);
          const data = await res.json();

          // Clear old options first
          addonSelect.innerHTML = `<option value="">None</option>`;

          if (data.length > 0) {
            data.forEach(rec => {
              const opt = document.createElement("option");
              opt.value = rec.recommended_item;
              opt.textContent = rec.recommended_item;
              addonSelect.appendChild(opt);
            });
          } else {
            const opt = document.createElement("option");
            opt.textContent = "No recommendations";
            opt.disabled = true;
            addonSelect.appendChild(opt);
          }
        } catch (err) {
          console.error("Error fetching recommendations:", err);
          addonSelect.innerHTML = `<option value="">Error loading add-ons</option>`;
        }
      }
    }
  });

  // Update totals when quantity changes
  qtyInput.addEventListener("input", updateTotals);
}

// Add new row when button clicked
document.getElementById("addItem").addEventListener("click", addNewRow);

// Handle form submission
document.getElementById("invoiceForm").addEventListener("submit", (e) => {
  e.preventDefault();

  const rows = document.querySelectorAll("#itemsTable tbody tr");
  const items = [];

  rows.forEach(row => {
    const partNumber = row.querySelector(".partNumber").value;
    const description = row.querySelector(".description").value;
    const qty = parseFloat(row.querySelector(".quantity").value);
    const price = parseFloat(row.querySelector(".unitPrice").value);
    const amount = qty * price;
    const addon = row.querySelector(".addon").value;

    items.push({ partNumber, description, qty, price, amount, addon });
  });

  const invoiceData = {
    number: document.getElementById("invoiceNumber").value,
    date: document.getElementById("invoiceDate").value,
    customer: document.getElementById("customerContact").value,
    billing: document.getElementById("billingAddress").value,
    salesperson: document.getElementById("salesperson").value,
    subtotal: document.getElementById("subtotal").textContent,
    tax: document.getElementById("tax").textContent,
    shipping: document.getElementById("shipping").textContent,
    total: document.getElementById("total").textContent,
    items
  };

  localStorage.setItem("invoiceData", JSON.stringify(invoiceData));
  window.location.href = "invoice.html";
});
