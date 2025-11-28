document.addEventListener("DOMContentLoaded", function () {
  // Handle clicking the info icon
  document.addEventListener("click", function(e) {
    if (e.target.closest(".infoLink")) {
      e.preventDefault();
      const row = e.target.closest("td");
      const itemName = row.querySelector(".descriptionSelect").value;
      window.location.href = `/item/${encodeURIComponent(itemName)}`;
    }
  });
});
