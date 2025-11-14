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

  rows.forEach((row) => {
    const qty = parseFloat(row.querySelector(".quantity")?.value) || 0;
    const price = parseFloat(row.querySelector(".unitPrice")?.value) || 0;
    const amount = qty * price;
    row.querySelector(".amount").textContent = amount.toFixed(2);
    subtotal += amount;
  });

  const tax = subtotal * 0.05;
  const shipping = 0.0;
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
function toggleDeleteVisibility(tr) {
  const btn = tr.querySelector("button.delete");
  if (!btn) return;
  if (rowHasContent(tr)) btn.classList.remove("hidden");
  else btn.classList.add("hidden");
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

  tbody.appendChild(newRow);

  const partSelect = newRow.querySelector(".partNumber");
  const qtyInput = newRow.querySelector(".quantity");
  const addonSelect = newRow.querySelector(".addon");
  const delBtn = newRow.querySelector(".delete");

  // DELETE button functionality
  // DELETE button functionality
  delBtn.addEventListener("click", () => {
    // Clean up linked rows both ways before deleting
    if (newRow._addonRow && newRow._addonRow.isConnected) {
      newRow._addonRow.remove();
      newRow._addonRow = null;
    }
    if (newRow._parentRow) {
      newRow._parentRow._addonRow = null;
    }

    if (isFirstRow(newRow)) {
      // If this is the first row, clear it instead of deleting
      partSelect.value = "";
      newRow.querySelector(".description").value = "";
      qtyInput.value = "1";
      newRow.querySelector(".unitPrice").value = "0";
      newRow.querySelector(".amount").textContent = "0.00";
      addonSelect.innerHTML = `<option value="">None</option>`;
      toggleDeleteVisibility(newRow);
      updateTotals();
    } else {
      // Otherwise, remove the row completely
      newRow.remove();
      updateTotals();
    }
  });

// Add-on change: create once, then update that same linked row
addonSelect.addEventListener("change", (e) => {
  const addonId = e.target.value;
  const baseRow = newRow; // this dropdown belongs to this row

  // If cleared, remove linked add-on row
  if (!addonId) {
    if (baseRow._addonRow && baseRow._addonRow.isConnected) {
      baseRow._addonRow.remove();
    }
    baseRow._addonRow = null;
    updateTotals();
    return;
  }

  // If already created, just update its part number
  if (baseRow._addonRow && baseRow._addonRow.isConnected) {
    const partSelect2 = baseRow._addonRow.querySelector(".partNumber");
    partSelect2.value = addonId;
    const qty2 = baseRow._addonRow.querySelector(".quantity");
    if (qty2) qty2.value = "1"; // optional reset
    partSelect2.dispatchEvent(new Event("change"));
    updateTotals();
    return;
  }

  // Otherwise, create it once
  const newAddonRow = addNewRow();
  baseRow._addonRow = newAddonRow;
  newAddonRow._parentRow = baseRow; // backlink for cleanup

  const newAddonPartSelect = newAddonRow.querySelector(".partNumber");
  newAddonPartSelect.value = addonId;
  newAddonPartSelect.dispatchEvent(new Event("change"));
  updateTotals();
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
      const qtyInput = existingRow.querySelector(".quantity");
      qtyInput.value = parseInt(qtyInput.value) + 1;

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
          opt.textContent = `${rec.recommended_item} - ${percent}% (${desc})`;
          addonSelect.appendChild(opt);
        });

        // STEP 4: Make sure only one "change" listener exists (handles text revert issue)
        addonSelect.onchange = () => {
          const selectedOption = addonSelect.options[addonSelect.selectedIndex];
          if (selectedOption) {
            // Save full text the first time
            if (!selectedOption.dataset.fullText) {
              selectedOption.dataset.fullText = selectedOption.textContent;
            }

            // Show only the short value when closed
            selectedOption.textContent = selectedOption.value;
          }

          // When user clicks the dropdown again, restore full text for all options
          addonSelect.addEventListener("mousedown", () => {
            Array.from(addonSelect.options).forEach((opt) => {
              if (opt.dataset.fullText) {
                opt.textContent = opt.dataset.fullText;
              }
            });
          });
        };

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

// Add new item row manually
document.getElementById("addItem").addEventListener("click", addNewRow);

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
