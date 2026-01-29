console.log("[Recommender] contentScript loaded on:", window.location.href);

let lastSelectedPart = null;
let lastInvoiceItems = [];

document.addEventListener("change", (e) => {
  const partSelect = e.target.closest("select.partNumber");
  if (!partSelect) return;

  const selectedPart = partSelect.value;
  if (!selectedPart) return;

  lastSelectedPart = selectedPart;

  console.log("[Recommender] Part selected:", selectedPart);

  chrome.action.setBadgeText({ text: "!" });
  chrome.action.setBadgeBackgroundColor({ color: "#0078d4" });

  chrome.runtime.sendMessage({
    type: "PART_SELECTED",
    payload: { part_number: selectedPart }
  });
});

window.addEventListener("invoiceItemsUpdated", (event) => {
  const items = event?.detail?.items || [];
  lastInvoiceItems = items;

  chrome.runtime.sendMessage({
    type: "INVOICE_ITEMS_UPDATED",
    payload: items
  });
});


chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.type === "REQUEST_CURRENT_CONTEXT") {
    sendResponse({
      part: lastSelectedPart,
      invoiceItems: lastInvoiceItems
    });
  }
});


chrome.runtime.onMessage.addListener((msg) => {
  if (msg.type !== "APPLY_ADDON") return;

  const addonId = msg.payload?.addon;
  if (!addonId) return;

  console.log("[Recommender] Applying add-on:", addonId);

  const rows = Array.from(document.querySelectorAll("#itemsTable tbody tr"));
  if (!rows.length) return;

  const targetRow = [...rows].reverse().find(row =>
    row.querySelector(".partNumber")?.value
  );
  if (!targetRow) return;

  const addonSelect = targetRow.querySelector(".addon");
  if (!addonSelect) return;

  // ⏳ Wait until the add-on option exists (async-safe)
  const waitForOption = setInterval(() => {
    const option = Array.from(addonSelect.options).find(
      opt => opt.value === addonId
    );

    if (!option) return;

    clearInterval(waitForOption);

    addonSelect.value = addonId;
    addonSelect.dispatchEvent(new Event("change", { bubbles: true }));

    console.log("[Recommender] Add-on applied:", addonId);
  }, 100);

  // Safety timeout
  setTimeout(() => clearInterval(waitForOption), 3000);
});
