// ===============================
// EXTENSION ICON CLICK
// ===============================
chrome.action.onClicked.addListener((tab) => {
  if (!tab?.id) return;

  chrome.tabs.sendMessage(
    tab.id,
    { type: "REQUEST_CURRENT_CONTEXT" },
    (response) => {
      const part = response?.part;

      const url = part
        ? `http://127.0.0.1:8080/recommender?part=${encodeURIComponent(part)}`
        : "http://127.0.0.1:8080/recommender";

      chrome.windows.create({
        url,
        type: "popup",
        width: 900,
        height: 700
      });

      // Clear badge once opened
      chrome.action.setBadgeText({ text: "" });
    }
  );
});

// ===============================
// PART CHANGE → BADGE
// ===============================
chrome.runtime.onMessage.addListener((msg) => {
  if (msg.type === "PART_CONTEXT_UPDATED") {
    chrome.action.setBadgeText({ text: "!" });
    chrome.action.setBadgeBackgroundColor({ color: "#0078d4" });
  }
});
