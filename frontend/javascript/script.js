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

document.addEventListener("DOMContentLoaded", async () => {
  if (sessionStorage.getItem("fetchNewInvoiceID")) {
    await loadNextInvoiceID();
    sessionStorage.removeItem("fetchNewInvoiceID");
  } else {
    await loadNextInvoiceID();
  }
  
  // Auto-update date to current date
  const dateField = document.getElementById("invoiceDate");
  const today = new Date();
  const year = today.getFullYear();
  const month = String(today.getMonth() + 1).padStart(2, '0');
  const day = String(today.getDate()).padStart(2, '0');
  dateField.value = `${year}-${month}-${day}`;
});

// Clear/set HTML5 validity messages as the user types/tabs
document.addEventListener("DOMContentLoaded", () => {
  const customerEl = document.getElementById("customerContact");
  const billingEl = document.getElementById("billingAddress");
  const salespersonEl = document.getElementById("salesperson");

  [customerEl, billingEl, salespersonEl].forEach((el) => {
    if (!el) return;

    el.addEventListener("input", () => el.setCustomValidity(""));
    el.addEventListener("blur", () => {
      if (!el.value.trim()) el.setCustomValidity("Please fill out this field.");
      else el.setCustomValidity("");
    });
  });
});

document.addEventListener("DOMContentLoaded", async () => {
  // Step 1: Load next invoice ID
  if (sessionStorage.getItem("fetchNewInvoiceID")) {
    await loadNextInvoiceID();
    sessionStorage.removeItem("fetchNewInvoiceID");
  } else {
    await loadNextInvoiceID();
  }

  // Step 2: Load all items before restoring saved state
  await fetchItems();

  // Step 3: Restore any previously saved invoice
  const saved = sessionStorage.getItem("savedInvoice");
  if (saved) {
    const data = JSON.parse(saved);

    // Restore header fields
    document.getElementById("invoiceNumber").value = data.invoiceNumber || "";
    document.getElementById("invoiceDate").value = data.invoiceDate || "";
    document.getElementById("customerContact").value = data.customerContact || "";
    document.getElementById("billingAddress").value = data.billingAddress || "";
    document.getElementById("salesperson").value = data.salesperson || "";

    // Restore items
    const tbody = document.querySelector("#itemsTable tbody");
    tbody.innerHTML = "";

    data.items.forEach((item) => {
      const row = addNewRow();
      const partSelect = row.querySelector(".partNumber");
      partSelect.value = item.partNumber;

      const selectedItem = allItems.find(it => it.item_id === item.partNumber);
      if (selectedItem) {
        row.querySelector(".description").value = selectedItem.item_description;
        row.querySelector(".unitPrice").value = selectedItem.unit_price.toFixed(2);
      }

      row.querySelector(".quantity").value = item.quantity;
    });

    updateTotals();
  }
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
}); // (this closes your emailInput event listener)

// ====================== //
//  CREATE BUTTON STATE   //
//  (gray until valid)    //
// ====================== //
document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("invoiceForm");
  const submitBtn = form?.querySelector('button[type="submit"]');

  const customerEl   = document.getElementById("customerContact");
  const billingEl    = document.getElementById("billingAddress");
  const salespersonEl= document.getElementById("salesperson");

  function allRequiredFilled() {
    const email = (customerEl?.value || "").trim();
    const emailOk = email === "" ? false : emailRegex.test(email);
    return (
      emailOk &&
      (billingEl?.value || "").trim() !== "" &&
      (salespersonEl?.value || "").trim() !== ""
    );
  }

  function updateSubmitState() {
    if (!submitBtn) return;
    submitBtn.disabled = !allRequiredFilled();
  }

  [customerEl, billingEl, salespersonEl].forEach((el) => {
    el?.addEventListener("input", updateSubmitState);
    el?.addEventListener("blur", updateSubmitState);
  });

  updateSubmitState(); // Initial state check
});


// ====================== //
//  ITEMS FETCH & TABLE   //
// ====================== //
let allItems = [];
async function fetchItems() {
  try {
    const response = await fetch("http://127.0.0.1:5000/items");
    allItems = await response.json();
    console.log("Items loaded:", allItems);
    addNewRow();
    return allItems;
  } catch (error) {
    console.error("Error fetching items:", error);
    return [];
  }
}


// ====================== //
//   ITEM DETAIL NAVIGATE //
// ====================== //
document.addEventListener("click", function(e) {
  const link = e.target.closest(".info-hover-icon");
  if (!link) return;

  e.preventDefault();

  const invoiceState = {
    invoiceNumber: document.getElementById("invoiceNumber").value,
    invoiceDate: document.getElementById("invoiceDate").value,
    customerContact: document.getElementById("customerContact").value,
    billingAddress: document.getElementById("billingAddress").value,
    salesperson: document.getElementById("salesperson").value,
    items: []
  };

  document.querySelectorAll("#itemsTable tbody tr").forEach((row) => {
    invoiceState.items.push({
      partNumber: row.querySelector(".partNumber")?.value || "",
      description: row.querySelector(".description")?.value || "",
      quantity: row.querySelector(".quantity")?.value || "1",
      unitPrice: row.querySelector(".unitPrice")?.value || "0"
    });
  });

  // Store in sessionStorage
  sessionStorage.setItem("savedInvoice", JSON.stringify(invoiceState));

  // Navigate to item detail page
  const row = link.closest("tr");
  const desc = row.querySelector(".description")?.value?.trim();
  const part = row.querySelector(".partNumber")?.value?.trim();
  const key = part || desc;

  if (key) {
    window.location.href = `/item/${encodeURIComponent(key)}`;
    sessionStorage.removeItem("savedInvoice");

  }
});


// ====================== //
//   UPDATE TOTALS LOGIC  //
// ====================== //
function updateTotals() {
  const rows = document.querySelectorAll("#itemsTable tbody tr");
  let subtotal = 0;

  rows.forEach((row) => {
    const qty = parseFloat(row.querySelector(".quantity")?.value) || 0;
    const price = parseFloat(row.querySelector(".unitPrice")?.value) || 0;
    const amount = qty * price;
    row.querySelector(".amount").textContent = amount.toFixed(2);
    subtotal += amount;
  });

  const tax = subtotal * 0.05;
  
  // Price-based shipping calculation
  let shipping = 0.0;
  if (subtotal < 75) {
    shipping = 9.99;
  } else if (75 <= subtotal && subtotal < 150) {
    shipping = 14.99;
  } else if (150 <= subtotal && subtotal < 300) {
    shipping = 19.99;
  } else if (subtotal >= 300) {
    shipping = 0.0; // Free shipping for orders $300+
  }
  
  const total = subtotal + tax + shipping;

  document.getElementById("subtotal").textContent = subtotal.toFixed(2);
  document.getElementById("tax").textContent = tax.toFixed(2);
  document.getElementById("shipping").textContent = shipping.toFixed(2);
  document.getElementById("total").textContent = total.toFixed(2);
}

// ====================== //
//  DELETE BUTTON HELPERS //
// ====================== //
function rowHasContent(tr) {
  const part = tr.querySelector(".partNumber")?.value?.trim() || "";
  const desc = tr.querySelector(".description")?.value?.trim() || "";
  const price = parseFloat(tr.querySelector(".unitPrice")?.value) || 0;
  const addon = tr.querySelector(".addon")?.value?.trim() || "";
  return part !== "" || desc !== "" || price > 0 || addon !== "";
}

function isFirstRow(tr) {
  const tbody = document.querySelector("#itemsTable tbody");
  return tbody.querySelector("tr") === tr;
}

// UPDATED: visibility rules
function toggleDeleteVisibility(tr) {
  const btn = tr.querySelector("button.delete");
  if (!btn) return;

  if (isFirstRow(tr)) {
    // First row: show Delete only when there is content (so user can clear)
    if (rowHasContent(tr)) {
      btn.classList.remove("hidden");
    } else {
      btn.classList.add("hidden");
    }
  } else {
    // Other rows: always show Delete (can delete even if empty)
    btn.classList.remove("hidden");
  }
}

// ====================== //
//   ADD NEW ROW LOGIC    //
// ====================== //
function addNewRow() {
  const tbody = document.querySelector("#itemsTable tbody");

  const partOptions = allItems
    .map((item) => `<option value="${item.item_id}">${item.item_id}</option>`)
    .join("");

  const newRow = document.createElement("tr");
  newRow.innerHTML = `
  <td>
    <select class="partNumber">
      <option value="">Select Part</option>
      ${partOptions}
    </select>
  </td>

  <td class="desc-cell">
    <input type="text" class="description" placeholder="Auto-filled" readonly>
  </td>

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

  tbody.appendChild(newRow);

  const partSelect = newRow.querySelector(".partNumber");
  const qtyInput = newRow.querySelector(".quantity");
  const addonSelect = newRow.querySelector(".addon");
  const delBtn = newRow.querySelector(".delete");

  // DELETE button functionality
  delBtn.addEventListener("click", () => {
    // Clean up linked rows both ways before deleting
    if (newRow._addonRow && newRow._addonRow.isConnected) {
      newRow._addonRow.remove();
      newRow._addonRow = null;
    }
    
    // If this row was created as an add-on from a parent row, reset the parent's add-on dropdown to "None"
    if (newRow._parentRow) {
      const parentAddonSelect = newRow._parentRow.querySelector(".addon");
      if (parentAddonSelect) {
        parentAddonSelect.value = "";
      }
      newRow._parentRow._addonRow = null;
    }

    const tbody = document.querySelector("#itemsTable tbody");
    const totalRows = tbody.querySelectorAll("tr").length;

    if (isFirstRow(newRow) && totalRows === 1) {
      // Only one row in the table → clear but keep it
      partSelect.value = "";
      newRow.querySelector(".description").value = "";
      qtyInput.value = "1";
      newRow.querySelector(".unitPrice").value = "0";
      newRow.querySelector(".amount").textContent = "0.00";
      addonSelect.innerHTML = `<option value="">None</option>`;
      toggleDeleteVisibility(newRow);
      updateTotals();
    } else {
      // More than one row → remove this row completely
      newRow.remove();
      updateTotals();
    }
  });

  addonSelect.addEventListener("change", (e) => {
    const addonId = e.target.value;
    const baseRow = newRow; // this dropdown belongs to this row
  
    if (!addonId) {
      // remove linked addon row
      if (baseRow._addonRow && baseRow._addonRow.isConnected) {
        baseRow._addonRow.remove();
      }
      baseRow._addonRow = null;
  
      // remove info icon too (from feature branch)
      const existingIcon = newRow.querySelector(".addon-info-icon");
      if (existingIcon) existingIcon.remove();
  
      updateTotals();
      return;
    }
  
    // Update existing linked row
    if (baseRow._addonRow && baseRow._addonRow.isConnected) {
      const partSelect2 = baseRow._addonRow.querySelector(".partNumber");
      partSelect2.value = addonId;
  
      const qty2 = baseRow._addonRow.querySelector(".quantity");
      if (qty2) qty2.value = "1";
  
      partSelect2.dispatchEvent(new Event("change"));
      updateTotals();
    } else {
      // Create new linked add-on row
      const newAddonRow = addNewRow();
      baseRow._addonRow = newAddonRow;
      newAddonRow._parentRow = baseRow;
  
      const newAddonPartSelect = newAddonRow.querySelector(".partNumber");
      newAddonPartSelect.value = addonId;
      newAddonPartSelect.dispatchEvent(new Event("change"));
      updateTotals();
    }
  
    const existingIcon = newRow.querySelector(".addon-info-icon");
  
    if (!existingIcon) {
      const icon = document.createElement("span");
      icon.classList.add("addon-info-icon");
      icon.innerHTML = `<i class="fa-solid fa-circle-info"></i>`;
      icon.title = "View Add-on Details";
  
      const addonCell = addonSelect.closest("td");
      addonCell.classList.add("addon-cell");
      addonCell.appendChild(icon);
  
      icon.addEventListener("click", () => {
        window.location.href = `/item/${encodeURIComponent(addonId)}`;
      });
    } else {
      existingIcon.onclick = () => {
        window.location.href = `/item/${encodeURIComponent(addonId)}`;
      };
    }
  });
  

  // Part selection
  partSelect.addEventListener("change", async (e) => {
    const selectedId = e.target.value;
    const selectedItem = allItems.find(
      (item) => String(item.item_id) === String(selectedId)
    );

    // STEP 1: Always clear the add-on dropdown when part changes
    addonSelect.innerHTML = `<option value="">None</option>`;

    // STEP 2: If this row previously created an add-on row, remove it
    if (newRow._addonRow && newRow._addonRow.isConnected) {
      newRow._addonRow.remove();
      newRow._addonRow = null;
    }

    // NEW: If this row is a child add-on row, update the parent's add-on dropdown to match the new part
    if (newRow._parentRow && selectedId) {
      const parentAddonSelect = newRow._parentRow.querySelector(".addon");
      if (parentAddonSelect) {
        // Check if the new selectedId exists in the parent's add-on dropdown options
        const optionExists = Array.from(parentAddonSelect.options).some(
          opt => opt.value === selectedId
        );
        
        if (optionExists) {
          // Update parent's add-on dropdown to the new part
          parentAddonSelect.value = selectedId;
        } else {
          // If the new part is not in recommendations, reset to "None"
          parentAddonSelect.value = "";
        }
      }
    }

    if (selectedItem) {
      // Check if there's already another row with this item
      const existingRow = Array.from(tbody.querySelectorAll("tr")).find(
        (row) =>
          row.querySelector(".partNumber").value === selectedId &&
          row !== newRow
      );

      if (existingRow) {
        // Instead of adding a new row, update the existing row with latest info
        existingRow.querySelector(".description").value =
          selectedItem.item_description;
        existingRow.querySelector(".unitPrice").value =
          selectedItem.unit_price.toFixed(2);
        const qtyInput2 = existingRow.querySelector(".quantity");
        qtyInput2.value = parseInt(qtyInput2.value) + 1;

        // Remove the redundant new row
        newRow.remove();
        updateTotals();
        return;
      }

      // Otherwise, just update current row
      newRow.querySelector(".description").value = selectedItem.item_description;
      newRow.querySelector(".unitPrice").value = selectedItem.unit_price.toFixed(2);
      toggleDeleteVisibility(newRow);
      updateTotals();

      // STEP 3: Fetch and rebuild recommendations for the new part
      try {
        const res = await fetch(`http://127.0.0.1:5000/recommendations/${selectedId}`);
        const data = await res.json();

        // Reset dropdown again before adding new options
        addonSelect.innerHTML = `<option value="">None</option>`;

        if (data.length > 0) {
          data.forEach((rec) => {
            const opt = document.createElement("option");
            opt.value = rec.recommended_item;
          
            const percent = (rec.score * 100).toFixed(0);
            const match = allItems.find((item) => item.item_id === rec.recommended_item);
            const desc = match ? match.item_description : "";
          
            const fullLabel  = `${rec.recommended_item} – ${percent}% (${desc})`;
            const shortLabel = rec.recommended_item;
          
            opt.dataset.fullLabel  = fullLabel;
            opt.dataset.shortLabel = shortLabel;
          
            // When the list is open, we show the full label
            opt.textContent = fullLabel;
          
            addonSelect.appendChild(opt);
          });
          

          // FIXED SHORT/LONG LABEL LOGIC
          addonSelect.addEventListener("focus", () => {
            // Dropdown is opening → show FULL labels
            Array.from(addonSelect.options).forEach(opt => {
              if (opt.dataset.fullLabel) opt.textContent = opt.dataset.fullLabel;
            });
          });

          addonSelect.addEventListener("mousedown", () => {
            // Some browsers trigger mousedown before focus
            Array.from(addonSelect.options).forEach(opt => {
              if (opt.dataset.fullLabel) opt.textContent = opt.dataset.fullLabel;
            });
          });

          addonSelect.addEventListener("change", () => {
            // Selection made → set ONLY this one to short label
            const selected = addonSelect.options[addonSelect.selectedIndex];
            if (selected && selected.dataset.shortLabel) {
              selected.textContent = selected.dataset.shortLabel;
            }
          });

          // When dropdown closes (blur), ensure collapsed view shows short label
          addonSelect.addEventListener("blur", () => {
            const selected = addonSelect.options[addonSelect.selectedIndex];
            if (selected && selected.dataset.shortLabel) {
              selected.textContent = selected.dataset.shortLabel;
            }
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
    } else {
      // Reset if cleared
      newRow.querySelector(".description").value = "";
      newRow.querySelector(".unitPrice").value = "0";
      newRow.querySelector(".amount").textContent = "0.00";
      addonSelect.innerHTML = `<option value="">None</option>`;
      toggleDeleteVisibility(newRow);
      updateTotals();
    }
  });
  

  qtyInput.addEventListener("input", () => {
    toggleDeleteVisibility(newRow);
    updateTotals();
  });

  addonSelect.addEventListener("change", () => toggleDeleteVisibility(newRow));

  toggleDeleteVisibility(newRow);
  return newRow;
}

// When "Add Item" is clicked, just add a brand new empty row
document.getElementById("addItem").addEventListener("click", () => {
  addNewRow();
});

// ====================== //
//   FORM SUBMISSION      //
// ====================== //
document
  .getElementById("invoiceForm")
  .addEventListener("submit", (e) => {
    e.preventDefault();
    const customerEl = document.getElementById("customerContact");
    const billingEl = document.getElementById("billingAddress");
    const salespersonEl = document.getElementById("salesperson");

    [customerEl, billingEl, salespersonEl].forEach((el) =>
      el.setCustomValidity("")
    );

    if (!customerEl.value.trim()) {
      customerEl.setCustomValidity("Please fill out this field.");
      customerEl.reportValidity();
      return;
    }
    if (!billingEl.value.trim()) {
      billingEl.setCustomValidity("Please fill out this field.");
      billingEl.reportValidity();
      return;
    }
    if (!salespersonEl.value.trim()) {
      salespersonEl.setCustomValidity("Please fill out this field.");
      salespersonEl.reportValidity();
      return;
    }

    const email = customerEl.value.trim();
    if (!emailRegex.test(email)) {
      alert("Please enter a valid email address before submitting.");
      emailInput.focus();
      return;
    }

    const rows = document.querySelectorAll("#itemsTable tbody tr");
    const items = [];

    rows.forEach((row) => {
      const partNumber = row.querySelector(".partNumber").value;
      const description = row.querySelector(".description").value;
      const qty = parseFloat(row.querySelector(".quantity").value) || 0;
      const price = parseFloat(row.querySelector(".unitPrice").value) || 0;
      const amount = qty * price;
      const addon = row.querySelector(".addon")
        ? row.querySelector(".addon").value
        : "";
      items.push({ partNumber, description, qty, price, amount, addon });
    });

    const invoiceData = {
      number: document.getElementById("invoiceNumber").value,
      date: document.getElementById("invoiceDate").value,
      customer: email,
      billing: billingEl.value,
      salesperson: salespersonEl.value,
      subtotal: document.getElementById("subtotal").textContent,
      tax: document.getElementById("tax").textContent,
      shipping: document.getElementById("shipping").textContent,
      total: document.getElementById("total").textContent,
      items,
    };

    fetch("http://127.0.0.1:5000/save_invoice", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(invoiceData),
    })
      .then((res) => res.json())
      .then((response) => {
        console.log(response.message);
        const redirectId = response.invoice_id || invoiceData.number;
        localStorage.setItem("invoiceData", JSON.stringify(invoiceData));
        window.location.href = `/invoice?invoice_id=${redirectId}`;
        sessionStorage.setItem("fetchNewInvoiceID", "true");
        setTimeout(async () => {
          await loadNextInvoiceID();
          console.log("Invoice ID refreshed for next entry.");
        }, 1500);
      })
      .catch((err) => {
        console.error("Error saving invoice:", err);
        alert("Error saving invoice. Check console for details.");
      });
  });