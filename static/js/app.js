document.addEventListener("click", function (event) {
  const button = event.target.closest("[data-amount], [data-tip]");
  if (!button) return;
  const amount = button.dataset.amount || button.dataset.tip;
  const field = document.querySelector('input[name="tip_amount"], input[name="amount"]');
  if (field) {
    field.value = amount;
    field.dispatchEvent(new Event("input", { bubbles: true }));
  }
});

document.addEventListener("input", function (event) {
  if (event.target.name !== "tip_amount") return;
  const total = document.getElementById("request-total");
  if (total) total.textContent = Number(total.dataset.base) + (Number(event.target.value) || 0);
});
