// Example dataset: item → related recommendations
const recommendationsData = {
  "Bread": ["Butter", "Jam", "Eggs"],
  "Milk": ["Cereal", "Cookies", "Chocolate"],
  "Rice": ["Curry Powder", "Vegetables", "Lentils"]
};

// Populate dropdown when searchBox is used
document.getElementById("searchBox").addEventListener("input", function() {
  const query = this.value.toLowerCase();
  const dropdown = document.getElementById("dropdown");

  // Clear old options
  dropdown.innerHTML = "";

  // Match items from dataset
  Object.keys(recommendationsData).forEach(item => {
    if (item.toLowerCase().includes(query)) {
      const option = document.createElement("option");
      option.value = item;
      option.textContent = item;
      dropdown.appendChild(option);
    }
  });
});

// Show recommendations when an item is selected
document.getElementById("dropdown").addEventListener("change", function() {
  const selectedItem = this.value;
  const recs = recommendationsData[selectedItem] || [];
  const recDiv = document.getElementById("recommendations");

  recDiv.innerHTML = `<h3>Recommendations for ${selectedItem}:</h3><ul>` +
    recs.map(r => `<li>${r}</li>`).join("") +
    `</ul>`;
});
