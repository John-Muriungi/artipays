(function () {
  const status = document.getElementById("payment-status");
  if (!status || !status.dataset.statusUrl) return;
  async function refresh() {
    try {
      const response = await fetch(status.dataset.statusUrl, { credentials: "same-origin" });
      if (!response.ok) return;
      const result = await response.json();
      if (result.status === "SUCCESS" && result.confirmation_url) {
        window.location.assign(result.confirmation_url);
      } else if (result.status === "FAILED" || result.status === "CANCELLED") {
        window.location.reload();
      }
    } catch (error) {
      console.error("Could not refresh payment status.", error);
    }
  }
  window.setInterval(refresh, 5000);
})();
