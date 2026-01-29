document.addEventListener("DOMContentLoaded", () => {
    chrome.action.setBadgeText({ text: "" });
  
    const statusEl = document.querySelector(".status");
    const listEl = document.getElementById("recommendations");
  
    statusEl.textContent = "Checking selected part…";
  
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      const tabId = tabs?.[0]?.id;
      if (!tabId) {
        statusEl.textContent = "No active tab.";
        return;
      }
  
      chrome.tabs.sendMessage(
        tabId,
        { type: "REQUEST_CURRENT_CONTEXT" },
        async (response) => {
          if (chrome.runtime.lastError || !response?.part) {
            statusEl.textContent = "Select a part to see recommendations.";
            return;
          }
  
          const part = response.part;
          statusEl.textContent = `Recommendations for ${part}`;
  
          try {
            const res = await fetch(
              `http://127.0.0.1:5000/recommendations/${part}`
            );
            const data = await res.json();
  
            listEl.innerHTML = "";
  
            if (!data || !data.length) {
              listEl.innerHTML = `<div class="empty">No recommendations</div>`;
              return;
            }
  
            data.forEach((rec) => {
              const div = document.createElement("div");
              div.className = "recommendation";
              div.style.cursor = "pointer";
  
              const pct = Math.round(rec.score * 10);
  
              div.innerHTML = `
                <div class="item-name">${rec.recommended_item}</div>
                <div class="item-reason">${pct}% match — click to add</div>
              `;
  
              div.addEventListener("click", () => {
                chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
                  const tabId = tabs?.[0]?.id;
                  if (!tabId) return;
  
                  chrome.tabs.sendMessage(tabId, {
                    type: "APPLY_ADDON",
                    payload: {
                      addon: rec.recommended_item
                    }
                  });
                });
              });
  
              listEl.appendChild(div);
            });
          } catch (err) {
            console.error("Error loading recommendations:", err);
            statusEl.textContent = "Error loading recommendations.";
          }
        }
      );
    });
  });
  