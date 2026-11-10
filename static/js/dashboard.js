(function () {
  const container = document.getElementById("incoming-requests");
  if (!container || !container.dataset.feedUrl) return;
  const known = new Set(
    Array.from(container.querySelectorAll("[data-request-id]")).map((item) => item.dataset.requestId)
  );
  let pollingTimer;
  async function refresh() {
    try {
      const response = await fetch(container.dataset.feedUrl, {
        headers: { "X-Requested-With": "XMLHttpRequest" },
        credentials: "same-origin",
      });
      if (!response.ok) return;
      const data = await response.json();
      for (const item of data.requests) {
        if (known.has(item.public_id)) continue;
        known.add(item.public_id);
        const emptyState = container.querySelector(".empty-state");
        if (emptyState) emptyState.remove();
        const card = document.createElement("article");
        card.className = "request-card";
        card.dataset.requestId = item.public_id;
        const song = document.createElement("div");
        song.className = "song-icon";
        song.textContent = "♫";
        const info = document.createElement("div");
        info.className = "request-info";
        const title = document.createElement("strong");
        title.textContent = item.song_title;
        const artist = document.createElement("span");
        artist.textContent = `${item.song_artist} · ${item.requester_name || "Guest"}`;
        info.append(title, artist);
        const amount = document.createElement("div");
        amount.className = "request-amount";
        amount.textContent = `KES ${item.amount}${item.tip_amount ? ` + KES ${item.tip_amount} tip` : ""}`;
        const link = document.createElement("a");
        link.className = "button button-small button-quiet";
        link.href = "/requests/";
        link.textContent = "Open";
        card.append(song, info, amount, link);
        container.prepend(card);
        if ("Notification" in window && Notification.permission === "granted") {
          new Notification("New paid song request", { body: `${item.song_title} — ${item.song_artist}` });
        }
      }
    } catch (error) {
      console.error("Could not refresh request feed.", error);
    }
  }
  function setPolling(interval) {
    if (pollingTimer) window.clearInterval(pollingTimer);
    pollingTimer = window.setInterval(refresh, interval);
  }

  refresh();
  if (!("WebSocket" in window)) {
    setPolling(8000);
    return;
  }

  setPolling(8000);
  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  const socket = new WebSocket(`${protocol}//${window.location.host}/ws/artist/requests/`);
  socket.addEventListener("open", () => setPolling(30000));
  socket.addEventListener("message", (event) => {
    try {
      if (JSON.parse(event.data).type === "paid_request") refresh();
    } catch (error) {
      console.error("Could not process a request notification.", error);
    }
  });
  socket.addEventListener("error", () => setPolling(8000));
  socket.addEventListener("close", () => setPolling(8000));
})();
