const lineItemsContainer = document.getElementById("line-items");
const addItemBtn = document.getElementById("add-item-btn");
const taxRateInput = document.getElementById("tax_rate");

const subtotalEl = document.getElementById("subtotal");
const taxAmountEl = document.getElementById("tax-amount");
const grandTotalEl = document.getElementById("grand-total");

function updateTotals() {
    let subtotal = 0;
    const rows = lineItemsContainer.querySelectorAll(".line-item");

    rows.forEach(row => {
        const qty = parseFloat(row.querySelector(".qty").value) || 0;
        const price = parseFloat(row.querySelector(".price").value) || 0;
        if (qty > 0 && price >= 0) {
            subtotal += qty * price;
        }
    });

    const taxRate = parseFloat(taxRateInput.value) || 0;
    const taxAmount = subtotal * (taxRate / 100);
    const grandTotal = subtotal + taxAmount;

    subtotalEl.textContent = subtotal.toFixed(2);
    taxAmountEl.textContent = taxAmount.toFixed(2);
    grandTotalEl.textContent = grandTotal.toFixed(2);
}

addItemBtn.addEventListener("click", () => {
    const row = document.createElement("div");
    row.className = "line-item";
    row.innerHTML = `
        <input type="text" name="description[]" placeholder="Service description" aria-label="Description" required>
        <input type="number" name="quantity[]" class="qty" value="1" min="1" step="1" aria-label="Quantity" required>
        <input type="number" name="price[]" class="price" value="0.00" min="0" step="0.01" aria-label="Unit Price" required>
        <button type="button" class="btn-remove no-print" aria-label="Remove item">&times;</button>
    `;
    lineItemsContainer.appendChild(row);
    updateTotals();
});

lineItemsContainer.addEventListener("input", updateTotals);
taxRateInput.addEventListener("input", updateTotals);

lineItemsContainer.addEventListener("click", (e) => {
    if (e.target.classList.contains("btn-remove")) {
        const rows = lineItemsContainer.querySelectorAll(".line-item");
        if (rows.length > 1) {
            e.target.closest(".line-item").remove();
            updateTotals();
        }
    }
});

updateTotals();
