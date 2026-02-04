document.addEventListener("DOMContentLoaded", () => {
  const statusEl = document.getElementById("status");
  const listEl = document.getElementById("recommendations");
  const refreshBtn = document.getElementById("refreshBtn");

  function getPartFromURL() {
    const params = new URLSearchParams(window.location.search);
    return params.get("part");
  }

  async function loadRecommendations() {
    statusEl.textContent = "Checking selected part…";
    listEl.innerHTML = "";

    // ✅ If running inside extension, ask content script
    if (typeof chrome !== "undefined" && chrome.runtime?.sendMessage) {
      chrome.runtime.sendMessage(
        { type: "REQUEST_CURRENT_CONTEXT" },
        (response) => {
          const part =
            response?.lastSelectedPart || response?.part || getPartFromURL();

          fetchAndRender(part);
        }
      );
    } else {
      // ✅ Fallback: use URL param (browser tab mode)
      fetchAndRender(getPartFromURL());
    }
  }

  async function fetchAndRender(part) {
    if (!part) {
      statusEl.textContent = "No part selected.";
      listEl.innerHTML = `<div class="empty">Select a part in the source system.</div>`;
      return;
    }

    statusEl.textContent = `Recommendations for ${part}`;

    try {
      const res = await fetch(
        `http://127.0.0.1:8080/recommendations/${encodeURIComponent(part)}`
      );
      const recs = await res.json();

      listEl.innerHTML = "";

      if (!Array.isArray(recs) || recs.length === 0) {
        listEl.innerHTML = `<div class="empty">No recommendations found.</div>`;
        return;
      }

      recs.forEach((rec) => {
        // ✅ Correct confidence math
        const percent = Math.round(rec.score * 10);

        const div = document.createElement("div");
        div.className = "recommendation";

        div.innerHTML = `
          <div class="item-name">${rec.recommended_item}</div>
          <div class="item-reason">${percent}% confidence</div>
        `;

        listEl.appendChild(div);
      });

      statusEl.textContent = "Recommendations updated";
    } catch (err) {
      console.error(err);
      statusEl.textContent = "Error loading recommendations.";
    }
  }

  refreshBtn.addEventListener("click", loadRecommendations);
  loadRecommendations();
});
