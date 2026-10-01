// Till page: sells products over a WebSocket and filters the product list.

const RECONNECT_DELAY_MS = 2000;
const TOAST_DURATION_MS = 2500;

const confirmDialog = document.getElementById("confirm-sale");
const confirmProductLabel = document.getElementById("confirm-sale-product");
const toast = document.getElementById("toast");
const searchInput = document.getElementById("product-search");

let socket = null;
let pendingProductId = null;
let toastTimer = null;

function salesSocketUrl() {
  const scheme = window.location.protocol === "https:" ? "wss" : "ws";
  return `${scheme}://${window.location.host}/ws/sales/`;
}

function connect() {
  socket = new WebSocket(salesSocketUrl());
  socket.addEventListener("message", (event) => handleServerMessage(JSON.parse(event.data)));
  socket.addEventListener("close", () => setTimeout(connect, RECONNECT_DELAY_MS));
}

function handleServerMessage(message) {
  if (message.type === "sale_recorded") {
    const { product_name: productName, sale_price: salePrice } = message.sale;
    showToast(`Sold ${productName} at Ksh ${salePrice}`, "success");
  } else {
    showToast("The sale was not recorded. Try again.", "error");
  }
}

function showToast(text, kind) {
  toast.textContent = text;
  toast.className = `toast toast-${kind}`;
  toast.hidden = false;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => {
    toast.hidden = true;
  }, TOAST_DURATION_MS);
}

function sell(productId) {
  if (socket === null || socket.readyState !== WebSocket.OPEN) {
    showToast("Not connected to the server. Reconnecting…", "error");
    return;
  }
  socket.send(JSON.stringify({ product_id: productId }));
}

document.querySelectorAll("[data-sell-product]").forEach((button) => {
  button.addEventListener("click", () => {
    pendingProductId = button.dataset.sellProduct;
    confirmProductLabel.textContent = button.dataset.productLabel;
    confirmDialog.showModal();
  });
});

confirmDialog.addEventListener("close", () => {
  if (confirmDialog.returnValue === "confirm" && pendingProductId !== null) {
    sell(pendingProductId);
  }
  pendingProductId = null;
});

searchInput.addEventListener("input", () => {
  const term = searchInput.value.trim().toLowerCase();
  document.querySelectorAll("[data-product-row]").forEach((row) => {
    row.hidden = !row.dataset.productName.includes(term);
  });
});

connect();
