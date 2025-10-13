document.addEventListener("DOMContentLoaded", () => {
  const data = JSON.parse(localStorage.getItem("invoiceData"));
  if (!data) {
    document.body.innerHTML = "<h2>No invoice data found!</h2>";
    return;
  }

  document.getElementById("displayNumber").textContent = data.number;
  document.getElementById("displayDate").textContent = data.date;
  document.getElementById("displayCustomer").textContent = data.customer;
  document.getElementById("displayBilling").textContent = data.billing;
  document.getElementById("displaySalesperson").textContent = data.salesperson;
  document.getElementById("displaySubtotal").textContent = data.subtotal;
  document.getElementById("displayTax").textContent = data.tax;
  document.getElementById("displayShipping").textContent = data.shipping;
  document.getElementById("displayTotal").textContent = data.total;

  const tbody = document.querySelector("#displayItems tbody");
  data.items.forEach(item => {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${item.description}</td>
      <td>${item.partNumber}</td>
      <td>${item.qty}</td>
      <td>${item.price.toFixed(2)}</td>
      <td>${item.amount.toFixed(2)}</td>
      <td>${item.addon}</td>
    `;
    tbody.appendChild(row);
  });
});
