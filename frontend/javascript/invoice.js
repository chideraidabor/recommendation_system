document.addEventListener("DOMContentLoaded", () => {
  const urlParams = new URLSearchParams(window.location.search);
  const invoiceId = urlParams.get("invoice_id");

  if (invoiceId) {
    fetch(`http://127.0.0.1:5000/get_invoice/${invoiceId}`)
      .then(res => res.json())
      .then(data => {
        if (data.error) {
          document.body.innerHTML = `<h2>${data.error}</h2>`;
          return;
        }

        const invoice = data.invoice;
        const items = data.items;
        const totals = data.totals;

        // Fill header info
        document.getElementById("displayNumber").textContent = invoice.invoice_id;
        document.getElementById("displayDate").textContent = invoice.date;
        document.getElementById("displayCustomer").textContent = invoice.customer_contact_info;
        document.getElementById("displayBilling").textContent = invoice.billing_address;
        document.getElementById("displaySalesperson").textContent = invoice.salesperson;

        // Fill totals
        document.getElementById("displaySubtotal").textContent = totals.subtotal.toFixed(2);
        document.getElementById("displayTax").textContent = totals.tax.toFixed(2);
        document.getElementById("displayShipping").textContent = totals.shipping.toFixed(2);
        document.getElementById("displayTotal").textContent = totals.total.toFixed(2);

        // Fill items
        const tbody = document.querySelector("#displayItems tbody");
        tbody.innerHTML = "";
        items.forEach(item => {
          const row = document.createElement("tr");
          row.innerHTML = `
            <td>${item.part_number}</td>
            <td>${item.item_description}</td>
            <td>${item.quantity}</td>
            <td>${parseFloat(item.unit_price).toFixed(2)}</td>
            <td>${parseFloat(item.total_amount).toFixed(2)}</td>
            <td>${item.variant_group || "-"}</td>
          `;
          tbody.appendChild(row);
        });
      })
      .catch(err => {
        console.error("Error loading invoice:", err);
        document.body.innerHTML = `<h2>Failed to load invoice data</h2>`;
      });

  } else {
    // (old method)
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
    tbody.innerHTML = "";
    data.items.forEach(item => {
      const row = document.createElement("tr");
      row.innerHTML = `
        <td>${item.partNumber}</td>
        <td>${item.description}</td>
        <td>${item.qty}</td>
        <td>${item.price.toFixed(2)}</td>
        <td>${item.amount.toFixed(2)}</td>
        <td>${item.addon || "-"}</td>
      `;
      tbody.appendChild(row);
    });
  }
});
