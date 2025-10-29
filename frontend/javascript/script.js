let allItems = [];

// --- Load items then start with one blank row ---
async function fetchItems() {
  try {
    const res = await fetch("http://127.0.0.1:5000/items");
    allItems = await res.json();
    addNewRow(); // start blank; delete hidden
  } catch (e) {
    console.error("Error fetching items:", e);
  }
}
fetchItems();

// --- Totals ---
function updateTotals() {
  const rows = document.querySelectorAll("#itemsTable tbody tr");
  let subtotal = 0;

  rows.forEach(row => {
    const qty   = parseFloat(row.querySelector(".quantity")?.value) || 0;
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

/* ===== Delete visibility helpers =====
   "Content" means: part chosen OR description text OR unit price > 0 OR add-on chosen.
   Quantity alone does NOT count. */
function rowHasContent(tr) {
  const part  = tr.querySelector(".partNumber")?.value?.trim() || "";
  const desc  = tr.querySelector(".description")?.value?.trim() || "";
  const price = parseFloat(tr.querySelector(".unitPrice")?.value) || 0;
  const addon = tr.querySelector(".addon")?.value?.trim() || "";
  return (part !== "" || desc !== "" || price > 0 || addon !== "");
}
function isFirstRow(tr) {
  const tbody = document.querySelector("#itemsTable tbody");
  return tbody.querySelector("tr") === tr;
}
function toggleDeleteVisibility(tr) {
  const btn = tr.querySelector("button.delete");
  if (!btn) return;
  if (rowHasContent(tr)) btn.classList.remove("hidden");
  else btn.classList.add("hidden");
}

/* ===== Add a new item row ===== */
function addNewRow() {
  const tbody = document.querySelector("#itemsTable tbody");

  // Build part options
  const partOptions = allItems
    .map(item => `<option value="${item.item_id}">${item.item_id}</option>`)
    .join("");

  const tr = document.createElement("tr");
  tr.innerHTML = `
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
    <td class="actions">
      <button type="button" class="delete hidden">Delete</button>
    </td>
  `;
  tbody.appendChild(tr);

  // Hook elements
  const partSelect  = tr.querySelector(".partNumber");
  const qtyInput    = tr.querySelector(".quantity");
  const priceInput  = tr.querySelector(".unitPrice");
  const descInput   = tr.querySelector(".description");
  const addonSelect = tr.querySelector(".addon");
  const delBtn      = tr.querySelector(".delete");

  // Delete click: clear first row, remove others
  delBtn.addEventListener("click", () => {
    if (isFirstRow(tr)) {
      partSelect.value = "";
      descInput.value  = "";
      qtyInput.value   = "1";
      priceInput.value = "0";
      tr.querySelector(".amount").textContent = "0.00";
      addonSelect.innerHTML = `<option value="">None</option>`;
      toggleDeleteVisibility(tr); // hide again
      updateTotals();
    } else {
      tr.remove();
      updateTotals();
    }
  });

  // Part selection: fill price/desc, load recommendations, manage duplicates
  partSelect.addEventListener("change", async (e) => {
    const selectedId = e.target.value;
    const selectedItem = allItems.find(item => item.item_id === selectedId);

    if (selectedItem) {
      // If same part exists elsewhere, bump its qty and remove this row
      const existing = Array.from(tbody.querySelectorAll("tr")).find(
        row => row !== tr && row.querySelector(".partNumber")?.value === selectedId
      );
      if (existing) {
        const q = existing.querySelector(".quantity");
        q.value = String((parseInt(q.value || "0", 10) + 1));
        tr.remove();
        updateTotals();
        return;
      }

      // Fill fields
      descInput.value  = selectedItem.item_description;
      priceInput.value = Number(selectedItem.unit_price).toFixed(2);
      updateTotals();

      // Load add-ons
      try {
        const res = await fetch(`http://127.0.0.1:5000/recommendations/${selectedId}`);
        const data = await res.json();
        addonSelect.innerHTML = `<option value="">None</option>`;
        if (Array.isArray(data) && data.length > 0) {
          data.forEach(rec => {
            const opt = document.createElement("option");
            opt.value = rec.recommended_item;
            opt.textContent = rec.recommended_item;
            addonSelect.appendChild(opt);
          });
        }
      } catch (err) {
        console.error("Error fetching recommendations:", err);
        addonSelect.innerHTML = `<option value="">None</option>`;
      }
    } else {
      // Deselected: clear row back to blank
      descInput.value = "";
      priceInput.value = "0";
      tr.querySelector(".amount").textContent = "0.00";
      addonSelect.innerHTML = `<option value="">None</option>`;
      updateTotals();
    }

    toggleDeleteVisibility(tr);
  });

  // Reflect changes
  qtyInput.addEventListener("input", () => {
    updateTotals();
    toggleDeleteVisibility(tr); // qty alone won't show, but keep state fresh
  });
  addonSelect.addEventListener("change", () => toggleDeleteVisibility(tr));

  // Ensure the brand-new blank row starts with Delete hidden
  toggleDeleteVisibility(tr);
}

// Add row button
document.getElementById("addItem").addEventListener("click", addNewRow);

// Submit
document.getElementById("invoiceForm").addEventListener("submit", (e) => {
  e.preventDefault();

  const rows = document.querySelectorAll("#itemsTable tbody tr");
  const items = [];

  rows.forEach(row => {
    const partNumber  = row.querySelector(".partNumber").value;
    const description = row.querySelector(".description").value;
    const qty         = parseFloat(row.querySelector(".quantity").value) || 0;
    const price       = parseFloat(row.querySelector(".unitPrice").value) || 0;
    const amount      = qty * price;
    const addon       = row.querySelector(".addon").value;

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
