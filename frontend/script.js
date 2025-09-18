function updateTotals() {
  const rows = document.querySelectorAll("#itemsTable tbody tr");
  let subtotal = 0;

  rows.forEach(row => {
    const qty = parseFloat(row.querySelector("td:nth-child(3) input").value) || 0;
    const price = parseFloat(row.querySelector("td:nth-child(4) input").value) || 0;
    const amount = qty * price;
    row.querySelector(".amount").textContent = amount.toFixed(2);
    subtotal += amount;
  });

  const tax = subtotal * 0.05; // 5% tax mock
  const shipping = 0.00; // fixed for now
  const total = subtotal + tax + shipping;

  document.getElementById("subtotal").textContent = subtotal.toFixed(2);
  document.getElementById("tax").textContent = tax.toFixed(2);
  document.getElementById("shipping").textContent = shipping.toFixed(2);
  document.getElementById("total").textContent = total.toFixed(2);
}

// Add new row
document.getElementById("addItem").addEventListener("click", () => {
  const tbody = document.querySelector("#itemsTable tbody");
  const newRow = document.createElement("tr");
  newRow.innerHTML = `
    <td>
      <select>
        <option>Door</option>
        <option>Handle</option>
        <option>Lock</option>
      </select>
    </td>
    <td>
      <select>
        <option>DR123</option>
        <option>HD368</option>
        <option>LK222</option>
      </select>
    </td>
    <td><input type="number" value="1" min="1"></td>
    <td><input type="number" value="100" step="0.01"></td>
    <td class="amount">100.00</td>
    <td>
      <select>
        <option>Handle</option>
        <option>Extra Keys</option>
        <option>None</option>
      </select>
    </td>
  `;
  tbody.appendChild(newRow);

  // Re-bind change listeners
  newRow.querySelectorAll("input").forEach(input => {
    input.addEventListener("input", updateTotals);
  });

  updateTotals();
});

// Auto-update totals when quantity or price changes
document.querySelectorAll("#itemsTable input").forEach(input => {
  input.addEventListener("input", updateTotals);
});

// Form submit (mock)
document.getElementById("invoiceForm").addEventListener("submit", (e) => {
  e.preventDefault();
  alert("Invoice created (mock data only). Check console.");
  console.log("Invoice data:", {
    number: document.getElementById("invoiceNumber").value,
    date: document.getElementById("invoiceDate").value,
    customer: document.getElementById("customerContact").value,
    billing: document.getElementById("billingAddress").value,
    salesperson: document.getElementById("salesperson").value
  });
});

updateTotals();
