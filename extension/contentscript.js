console.log("[Recommender] contentScript loaded on:", window.location.href);

let lastSelectedPart = null;

/* =========================
   LISTEN: PART SELECTION
   ========================= */
document.addEventListener("change", (e) => {
  const partSelect = e.target.closest("select.partNumber");
  if (!partSelect) return;

  const selectedPart = partSelect.value;
  if (!selectedPart) return;

  lastSelectedPart = selectedPart;

  console.log("[Recommender] Selected part:", selectedPart);

  // 🔔 notify extension (badge only)
  chrome.runtime.sendMessage({ type: "PART_CONTEXT_UPDATED" });

  // ✅ PUSH context to 8080 (this is the key fix)
  fetch("http://127.0.0.1:8080/context", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ part: selectedPart })
  }).catch(err =>
    console.warn("[Recommender] Failed to update server context:", err)
  );
});

/* =========================
   RESPOND: EXTENSION REQUEST
   (used only on popup open)
   ========================= */
chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.type === "REQUEST_CURRENT_CONTEXT") {
    sendResponse({ part: lastSelectedPart });
  }
});

