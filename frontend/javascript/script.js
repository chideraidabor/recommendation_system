// ====================== //
//  AUTO INVOICE ID LOAD  //
// ====================== //
async function loadNextInvoiceID() {
  try {
    const res = await fetch("http://127.0.0.1:5000/next_invoice_id");
    const data = await res.json();
    document.getElementById("invoiceNumber").value = data.next_invoice_id;
  } catch (err) {
    console.error("Error fetching next invoice ID:", err);
    document.getElementById("invoiceNumber").value = "INV0001"; // fallback
  }
}

// document.addEventListener("DOMContentLoaded", loadNextInvoiceID);
//  Ensure new invoice number loads after redirect
document.addEventListener("DOMContentLoaded", async () => {
  if (sessionStorage.getItem("fetchNewInvoiceID")) {
    await loadNextInvoiceID();
    sessionStorage.removeItem("fetchNewInvoiceID");
  } else {
    await loadNextInvoiceID();
  }
});
// Clear/set HTML5 validity messages as the user types/tabs
document.addEventListener("DOMContentLoaded", () => {
  const customerEl    = document.getElementById("customerContact");
  const billingEl     = document.getElementById("billingAddress");
  const salespersonEl = document.getElementById("salesperson");

  [customerEl, billingEl, salespersonEl].forEach((el) => {
    if (!el) return;

    // Clear any prior custom error while typing
    el.addEventListener("input", () => {
      el.setCustomValidity("");
    });

    // On leaving the field, set the message only if empty
    el.addEventListener("blur", () => {
      if (!el.value.trim()) {
        el.setCustomValidity("Please fill out this field.");
      } else {
        el.setCustomValidity("");
      }
    });
  });
});



// ====================== //
//   EMAIL VALIDATION     //
// ====================== //
const emailInput = document.getElementById("customerContact");
const emailError = document.createElement("span");
emailError.id = "emailError";
emailError.style.color = "red";
emailError.style.fontSize = "12px";
emailInput.parentNode.insertBefore(emailError, emailInput.nextSibling);

//  Simple regex: supports most valid email patterns
const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;

emailInput.addEventListener("input", () => {
  const email = emailInput.value.trim();

  if (email === "") {
    emailError.textContent = "";
    emailInput.style.borderColor = "";
  } else if (!emailRegex.test(email)) {
    emailError.textContent = "⚠ Please enter a valid email address";
    emailInput.style.borderColor = "red";
  } else {
    emailError.textContent = "";
    emailInput.style.borderColor = "green";
  }
});

// ====================== //
//  ITEMS FETCH & TABLE   //
// ====================== //
let allItems = [];

// Fetch items from backend and populate first blank row
async function fetchItems() {
  try {
    const response = await fetch("http://127.0.0.1:5000/items");
    allItems = await response.json();
    console.log("Items loaded:", allItems);
    addNewRow();
  } catch (error) {
    console.error("Error fetching items:", error);
  }
}
fetchItems();

// ====================== //
//   UPDATE TOTALS LOGIC  //
// ====================== //
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

// ====================== //
//   ADD NEW ROW LOGIC    //
// ====================== //
function addNewRow() {
  const tbody = document.querySelector("#itemsTable tbody");

  // Build dropdown options
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
// When an add-on is selected, it creates a new row and prefills it with that item.
// We do NOT reset the original dropdown, so it stays selected.
addonSelect.addEventListener("change", (e) => {
  const addonId = e.target.value;
  if (!addonId) return; // ignore "None" or empty

  // Create the next row
  const newAddonRow = addNewRow();
  const newAddonPartSelect = newAddonRow.querySelector(".partNumber");

  // Select the add-on item in the new row and trigger normal population
  newAddonPartSelect.value = addonId;
  newAddonPartSelect.dispatchEvent(new Event("change"));

  // IMPORTANT: Do NOT modify e.target.value — this preserves the selection
});


  // Handle part selection
  partSelect.addEventListener("change", async (e) => {
    const selectedId = e.target.value;
    const selectedItem = allItems.find(item => String(item.item_id) === String(selectedId));

    if (selectedItem) {
      // Avoid duplicate rows
      const existingRow = Array.from(tbody.querySelectorAll("tr")).find(
        row => row.querySelector(".partNumber").value === selectedId && row !== newRow
      );

      if (existingRow) {
        const existingQty = existingRow.querySelector(".quantity");
        existingQty.value = parseInt(existingQty.value) + 1;
        newRow.remove();
        updateTotals();
      } else {
        // Fill description and price
        newRow.querySelector(".description").value = selectedItem.item_description;
        newRow.querySelector(".unitPrice").value = selectedItem.unit_price.toFixed(2);
        updateTotals();

        // Fetch recommended add-ons
        try {
          const res = await fetch(`http://127.0.0.1:5000/recommendations/${selectedId}`);
          const data = await res.json();
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

  qtyInput.addEventListener("input", updateTotals);
  return newRow;
}

// Add new item row manually
document.getElementById("addItem").addEventListener("click", addNewRow);

// ====================== //
//   FORM SUBMISSION      //
// ====================== //
document.getElementById("invoiceForm").addEventListener("submit", (e) => {
  e.preventDefault();
    const customerEl    = document.getElementById("customerContact");
  const billingEl     = document.getElementById("billingAddress");
  const salespersonEl = document.getElementById("salesperson");

  // Always clear stale messages at the start of a submit
  customerEl.setCustomValidity("");
  billingEl.setCustomValidity("");
  salespersonEl.setCustomValidity("");

  if (!customerEl.value.trim()) {
    customerEl.setCustomValidity("Please fill out this field.");
    customerEl.reportValidity();
    customerEl.focus();
    return;
  }
  if (!billingEl.value.trim()) {
    billingEl.setCustomValidity("Please fill out this field.");
    billingEl.reportValidity();
    billingEl.focus();
    return;
  }
  if (!salespersonEl.value.trim()) {
    salespersonEl.setCustomValidity("Please fill out this field.");
    salespersonEl.reportValidity();
    salespersonEl.focus();
    return;
  }

  // Validate email again before submit
  const email = document.getElementById("customerContact").value.trim();
  if (!emailRegex.test(email)) {
    alert("Please enter a valid email address before submitting.");
    emailInput.focus();
    return;
  }

  // Build items array
  const rows = document.querySelectorAll("#itemsTable tbody tr");
  const items = [];

  rows.forEach(row => {
    const partNumber = row.querySelector(".partNumber").value;
    const description = row.querySelector(".description").value;
    const qty = parseFloat(row.querySelector(".quantity").value);
    const price = parseFloat(row.querySelector(".unitPrice").value);
    const amount = qty * price;
    const addon = row.querySelector(".addon") ? row.querySelector(".addon").value : "";
    items.push({ partNumber, description, qty, price, amount, addon });
  });

  // Build invoice data
  const invoiceData = {
    number: document.getElementById("invoiceNumber").value,
    date: document.getElementById("invoiceDate").value,
    customer: email,
    billing: document.getElementById("billingAddress").value,
    salesperson: document.getElementById("salesperson").value,
    subtotal: document.getElementById("subtotal").textContent,
    tax: document.getElementById("tax").textContent,
    shipping: document.getElementById("shipping").textContent,
    total: document.getElementById("total").textContent,
    items
  };

  // Send data to backend
  fetch("http://127.0.0.1:5000/save_invoice", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(invoiceData)
  })
    .then(res => res.json())
    .then(response => {
      console.log(response.message);

      // Use backend invoice_id if available
      const redirectId = response.invoice_id || invoiceData.number;

      // Store locally
      localStorage.setItem("invoiceData", JSON.stringify(invoiceData));

      // Redirect
      window.location.href = `/invoice?invoice_id=${redirectId}`;

      // ✅ Make sure the next invoice ID is fetched fresh for the next load
      sessionStorage.setItem("fetchNewInvoiceID", "true");
      setTimeout(async () => {
        await loadNextInvoiceID();
        console.log("🔁 Invoice ID refreshed for next entry.");
      }, 1500);
      
    })
    .catch(err => {
      console.error("Error saving invoice:", err);
      alert("Error saving invoice. Check console for details.");
    });
});