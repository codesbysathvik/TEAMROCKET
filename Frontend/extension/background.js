const BACKEND_SCAN = "http://127.0.0.1:5000/scan";

chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.status !== "complete") return;
  if (!tab.url || tab.url.startsWith("chrome://")) return;

  checkUrl(tabId, tab.url);
});

async function checkUrl(tabId, url) {
  try {
    const res = await fetch(BACKEND_SCAN, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url })
    });

    const data = await res.json();
    console.log("Scan result:", data);

    if (data.final_score >= 70) {
      triggerWarning(tabId, url, data);
    }
  } catch (e) {
    console.log("Backend error:", e);
  }
}

function triggerWarning(tabId, url, data) {
  // Show notification
  chrome.notifications.create({
    type: "basic",
    iconUrl: "icons/icon128.png",
    title: "⚠️ Dangerous Website Detected",
    message: `Risk Score: ${data.final_score}\nClick to see details.`,
    priority: 2
  });

  // Open block screen
  chrome.tabs.update(tabId, {
    url: chrome.runtime.getURL("block.html") + `?url=${encodeURIComponent(url)}`
  });
}
